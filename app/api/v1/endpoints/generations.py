import base64
import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from fastapi.concurrency import run_in_threadpool
from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Request, status, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, get_current_user_optional, require_photo_consent
from app.core.config import settings
from app.core.logging import logger
from app.core.rate_limiter import rate_limiter
from app.db.models import (ConsentRecordModel, GenerationRequestModel, GenerationSelectionModel, ImageAssetModel,
                           UsageEventModel, UserModel)
from app.schemas.generation import GenerationAcceptedResponse, GenerationStatusResponse, ImageAssetInfo
from app.services.image_processor import read_limited_image, process_image, pick_size
from app.services.generation_service import process_generation_background_job
from app.services.storage import storage_service
from app.services import catalog, recommender
from app.services.prompt_builder import MAX_AREAS, compose_prompt, parse_areas, summary

router = APIRouter()

def delete_request(db: Session, req: GenerationRequestModel) -> None:
    """Delete a generation with its source, reference and result images (files and rows)."""
    for asset in req.assets:
        storage_service.delete(asset.storage_key)
    db.query(ConsentRecordModel).filter(ConsentRecordModel.request_id == req.id).update({"request_id": None})
    db.query(UsageEventModel).filter(UsageEventModel.request_id == req.id).delete()
    db.delete(req)
    db.commit()


def purge_expired(db: Session) -> int:
    """Retention: delete anonymous generations older than RETENTION_DAYS (signed-in users delete their own)."""
    from datetime import timedelta
    cutoff = datetime.now(timezone.utc) - timedelta(days=settings.RETENTION_DAYS)
    old = (db.query(GenerationRequestModel)
           .filter(GenerationRequestModel.user_id.is_(None), GenerationRequestModel.created_at < cutoff).all())
    for req in old:
        delete_request(db, req)
    return len(old)


def utc_now_iso():
    return datetime.now(timezone.utc).isoformat()

def build_status_response(req: GenerationRequestModel) -> GenerationStatusResponse:
    asset_infos = []
    result_b64 = None

    for asset in req.assets:
        url = storage_service.get_signed_url(asset.storage_key)
        asset_infos.append(
            ImageAssetInfo(
                id=asset.id,
                role=asset.role,
                mime_type=asset.mime_type,
                byte_size=asset.byte_size,
                width=asset.width,
                height=asset.height,
                url=url,
            )
        )
        if asset.role == "result" and req.status == "succeeded":
            path = os.path.join("storage", asset.storage_key) if storage_service.storage_type == "local" else asset.storage_key
            if os.path.exists(path):
                with open(path, "rb") as f:
                    result_b64 = base64.b64encode(f.read()).decode("utf-8")

    return GenerationStatusResponse(
        request_id=req.id,
        status=req.status,
        category=req.category,
        model=req.model_name,
        quality=req.quality,
        size=req.size,
        cost_usd=req.cost_usd,
        cost_formatted=f"${req.cost_usd:.3f} USD" if req.cost_usd is not None else None,
        error_message=req.error_message,
        created_at=req.created_at.isoformat() if req.created_at else "",
        completed_at=req.completed_at.isoformat() if req.completed_at else None,
        result_image_b64=result_b64,
        assets=asset_infos,
        selections=[{"area": x.area, "source": x.source, "template_id": x.template_id,
                     "template_version": x.template_version, "name": x.name} for x in req.selections],
        intensity=req.selections[0].intensity if req.selections else None,
        **_quality_fields(req),
    )


def _quality_fields(req: GenerationRequestModel) -> dict:
    qc = req.quality_check
    if not qc:
        return {}
    import json
    from app.services.result_judge import LABELS
    scores = json.loads(qc.scores_json)
    return {
        "accuracy": qc.overall,
        "accuracy_breakdown": {LABELS.get(k, k): v for k, v in scores.items()},
        "attempts": qc.attempts,
    }

def _template_image(spec_list: List[dict]):
    """The first selected template that has a reference photo, with its bytes, so the model can see the style."""
    for spec in spec_list:
        t = spec.get("template") or {}
        path = catalog.image_path(t.get("image")) if spec["source"] == "template" else None
        if path:
            with open(path, "rb") as f:
                return spec, f.read()
    return None, None


def _parse_custom(raw: str) -> List[dict]:
    if not raw.strip():
        return []
    try:
        items = json.loads(raw)
        assert isinstance(items, list)
    except Exception:
        raise HTTPException(400, "custom_styles must be a JSON list.")
    out = []
    for item in items[:MAX_AREAS]:
        area = str((item or {}).get("area", ""))
        name = str(item.get("name", "")).strip()[:60]
        description = str(item.get("description", "")).strip()[:400]
        if area not in settings.CATEGORIES or area == "Overall beauty look":
            raise HTTPException(400, f"Unsupported beauty category: {area[:40]}.")
        if not name or len(description) < 15:
            raise HTTPException(400, "A personalised style needs a name and a description of at least 15 characters.")
        out.append({"area": area, "source": "custom", "template": {"name": name, "prompt": description}})
    return out


def build_specs(templates: str, custom_styles: str, category: str, has_reference: bool,
                style: str, style_description: str) -> List[dict]:
    """One spec per area from template IDs, personalised styles and the reference photo (see prompt_builder)."""
    specs: List[dict] = []
    for template_id in [t.strip() for t in templates.split(",") if t.strip()]:
        t = catalog.get(template_id)
        if not t:
            raise HTTPException(400, "One of the chosen styles is no longer available. Please choose it again.")
        if t["category"] == "Overall beauty look":
            raise HTTPException(400, "Send the templates a look is made of, not the look itself.")
        specs.append({"area": t["category"], "source": "template", "template": t})
    specs += _parse_custom(custom_styles)

    areas = parse_areas(category, required=not specs)
    taken = {s["area"] for s in specs}
    if has_reference:
        if not areas and not specs:
            raise HTTPException(400, "Choose what the reference photo should change.")
        for area in areas:
            if area in taken:
                raise HTTPException(400, f"{area} is already set by a chosen style; use the reference photo for other areas.")
            specs.append({"area": area, "source": "reference"})
    elif areas:
        # Older clients: one style name (or personalised description) for every area in `category`.
        t = catalog.find_by_name(style, areas) if style.strip() else None
        if not t and style.strip() and len(style_description.strip()) >= 15:
            t = {"name": style.strip()[:60], "prompt": style_description.strip()[:400]}
        if not t:
            raise HTTPException(400, "Add a style reference image, or choose a style from the catalogue.")
        source = "template" if t.get("id") else "custom"
        specs += [{"area": a, "source": source, "template": t} for a in areas if a not in taken]

    if len({s["area"] for s in specs}) != len(specs):
        raise HTTPException(400, "Choose one style per area.")
    if not specs:
        raise HTTPException(400, "Choose at least one style to try on.")
    if len(specs) > MAX_AREAS:
        raise HTTPException(400, f"Choose up to {MAX_AREAS} areas to change.")
    order = list(catalog.CATEGORIES)
    return sorted(specs, key=lambda s: order.index(s["area"]))


@router.post("/generations", status_code=202, response_model=GenerationAcceptedResponse)
async def create_generation(
    request: Request,
    background_tasks: BackgroundTasks,
    target_image: UploadFile = File(..., description="User target photo"),
    reference_image: Optional[UploadFile] = File(None, description="Optional style reference photo for the areas in `category`"),
    templates: str = Form("", description="Comma-separated catalogue template IDs, at most one per category"),
    custom_styles: str = Form("", description='JSON list of personalised styles: [{"area", "name", "description"}]'),
    category: str = Form("", description="Areas the reference photo changes, comma-separated, e.g. \"Hairstyle,Makeup\""),
    intensity: str = Form("medium", description="subtle, medium or bold (hair colour and makeup)"),
    keep_roots: bool = Form(False, description="Hair colour: keep natural colour at the roots"),
    style: str = Form("", description="Older clients: a catalogue style name"),
    style_description: str = Form("", description="Older clients: describes a personalised style"),
    notes: str = Form(""),
    consent_version: str = Form("", description="The photo consent version the user accepted"),
    db: Session = Depends(get_db),
    current_user: Optional[UserModel] = Depends(get_current_user_optional),
):
    consent_version = require_photo_consent(consent_version)
    if intensity not in ("subtle", "medium", "bold"):
        raise HTTPException(400, "Intensity must be subtle, medium or bold.")
    has_reference = reference_image is not None and bool(reference_image.filename)
    specs = build_specs(templates, custom_styles, category, has_reference, style, style_description)
    areas = [s["area"] for s in specs]
    category = ", ".join(areas)  # stored and returned as e.g. "Hairstyle, Makeup"

    # Rate limiting check
    client_ip = request.client.host if request.client else "127.0.0.1"
    rate_key = current_user.id if current_user else f"ip:{client_ip}"
    rate_limiter.check_rate_limit(rate_key)

    person_raw = await read_limited_image(target_image, "Your photo")
    if has_reference:
        style_raw = await read_limited_image(reference_image, "The style reference photo")
        style_label = "The style reference photo"
    else:
        ref_spec, style_raw = _template_image(specs)
        if ref_spec:
            ref_spec["uses_reference"] = True
        style_label = "The style's reference photo"

    person_b, person_mime, person_ext, person_size = process_image(person_raw, "Your photo")
    if style_raw is not None:
        style_b, style_mime, style_ext, style_size = process_image(style_raw, style_label)
    else:
        style_b = style_mime = style_ext = style_size = None

    prompt = compose_prompt(specs, intensity, keep_roots and "Hair colour" in areas, notes)
    if not templates.strip() and not custom_styles.strip() and style.strip() and specs[0]["source"] != "reference" \
            and style.strip() != specs[0]["template"]["name"]:
        prompt += f" Additional style description: {style.strip()[:300]}."

    size = pick_size(*person_size)
    request_id = str(uuid.uuid4())
    created_at = utc_now_iso()
    user_id = current_user.id if current_user else None

    # Create DB record with queued status
    db_req = GenerationRequestModel(
        id=request_id,
        user_id=user_id,
        category=category,
        style_description="; ".join(s["template"]["name"] for s in specs if s["source"] != "reference")[:300] or None,
        notes=notes.strip()[:500] if notes else None,
        status="queued",
        model_name=settings.OPENAI_IMAGE_MODEL,
        quality=settings.OPENAI_IMAGE_QUALITY,
        size=size,
    )
    db.add(db_req)
    for s in specs:
        t = s.get("template") or {}
        db.add(GenerationSelectionModel(
            request_id=request_id, area=s["area"], source=s["source"], template_id=t.get("id"),
            template_version=t.get("version"), name=(t.get("name") or "Reference photo")[:80], intensity=intensity,
        ))

    # Record consent
    db.add(ConsentRecordModel(
        user_id=user_id,
        request_id=request_id,
        consent_version=consent_version,
    ))
    db.commit()

    # Schedule background worker
    background_tasks.add_task(
        process_generation_background_job,
        request_id,
        person_b,
        person_mime,
        person_ext,
        person_size,
        style_b,
        style_mime,
        style_ext,
        style_size,
        prompt,
        size,
        quality_context={"areas": areas, "style_text": summary(specs, intensity, notes)},
    )

    logger.info("Queued async generation: request_id=%s user_id=%s category=%s", request_id, user_id, category)

    return {
        "request_id": request_id,
        "status": "queued",
        "category": category,
        "created_at": created_at,
        "status_url": f"{settings.API_V1_STR}/generations/{request_id}",
    }

@router.get("/generations", response_model=List[GenerationStatusResponse])
def list_user_generations(
    limit: int = 20,
    offset: int = 0,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    reqs = (
        db.query(GenerationRequestModel)
        .filter(GenerationRequestModel.user_id == current_user.id)
        .order_by(GenerationRequestModel.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [build_status_response(req) for req in reqs]

@router.get("/generations/{request_id}", response_model=GenerationStatusResponse)
def get_generation_status(
    request_id: str,
    current_user: Optional[UserModel] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    req = db.query(GenerationRequestModel).filter(GenerationRequestModel.id == request_id).first()
    if not req:
        raise HTTPException(404, f"Generation request '{request_id}' not found.")

    # Ownership check if request has a user_id
    if req.user_id and (not current_user or current_user.id != req.user_id):
        raise HTTPException(403, "Access denied. You do not own this generation request.")

    return build_status_response(req)

@router.delete("/generations/{request_id}", status_code=204)
def delete_generation(
    request_id: str,
    current_user: Optional[UserModel] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    req = db.query(GenerationRequestModel).filter(GenerationRequestModel.id == request_id).first()
    if not req:
        raise HTTPException(404, f"Generation request '{request_id}' not found.")

    if req.user_id and (not current_user or current_user.id != req.user_id):
        raise HTTPException(403, "Access denied. You do not own this generation request.")

    delete_request(db, req)
    logger.info("Deleted generation request_id=%s by user_id=%s", request_id, current_user.id if current_user else "guest")

@router.post("/analyze-face")
async def analyze_face(
    request: Request,
    face_image: UploadFile = File(...),
    group: str = Form("", description="Catalogue to suggest from: women, men or all (chosen by the user)"),
    section: str = Form("", description="Older clients: women, men or auto"),
    length: str = Form(""),
    maintenance: str = Form(""),
    occasion: str = Form(""),
    consent_version: str = Form(""),
    current_user: Optional[UserModel] = Depends(get_current_user_optional),
):
    """Estimate face shape, undertone and visible hair with confidence, and suggest catalogue templates and new ideas."""
    from app.services.face_analyzer import FaceAnalysisFailed, FaceAnalysisUnavailable, analyze_face as run_analysis

    require_photo_consent(consent_version)
    group = group or (section if section in ("women", "men") else "all")
    if group not in ("women", "men", "all"):
        raise HTTPException(400, "group must be women, men or all.")
    client_ip = request.client.host if request.client else "127.0.0.1"
    rate_key = "analysis:" + (current_user.id if current_user else f"ip:{client_ip}")
    rate_limiter.check_rate_limit(rate_key, settings.ANALYSIS_LIMIT_PER_DAY, label="face analysis")

    raw = await read_limited_image(face_image, "Your photo")
    img_bytes, mime, _ext, _size = process_image(raw, "Your photo")
    prefs = _prefs(length, maintenance, occasion)
    try:
        return await run_in_threadpool(run_analysis, img_bytes, mime, group, prefs)
    except FaceAnalysisUnavailable as exc:
        raise HTTPException(503, str(exc))
    except FaceAnalysisFailed as exc:
        raise HTTPException(502, str(exc))


PREF_VALUES = {
    "length": ("very short", "short", "medium", "long"),
    "maintenance": ("low", "medium", "high"),
    "occasion": ("everyday", "professional", "formal", "occasion", "evening", "party", "creative"),
}


def _prefs(length: str = "", maintenance: str = "", occasion: str = "") -> dict:
    prefs = {"length": length.strip().lower(), "maintenance": maintenance.strip().lower(),
             "occasion": occasion.strip().lower()}
    for key, value in prefs.items():
        if value and value not in PREF_VALUES[key]:
            raise HTTPException(400, f"Unsupported {key}: {value[:30]}.")
    return {k: v for k, v in prefs.items() if v}


class RecommendationRequest(BaseModel):
    group: str = "all"
    analysis: Dict[str, Any] = {}
    preferences: Dict[str, str] = {}


@router.post("/recommendations")
def recommendations(body: RecommendationRequest):
    """Re-rank catalogue templates for an analysis and preferences, without calling the AI again."""
    from app.services.face_analyzer import analysis_for_ranking
    if body.group not in ("women", "men", "all"):
        raise HTTPException(400, "group must be women, men or all.")
    prefs = _prefs(**{k: str(v) for k, v in body.preferences.items() if k in PREF_VALUES})
    return recommender.recommend(body.group, analysis_for_ranking(body.analysis), prefs)


@router.post("/check-photo")
async def check_photo(
    request: Request,
    face_image: UploadFile = File(...),
    consent_version: str = Form(""),
    current_user: Optional[UserModel] = Depends(get_current_user_optional),
):
    """Check a face photo is complete and clear: one face, face and hair in frame, sharp, well lit."""
    from app.services.photo_check import check_photo as run_check

    require_photo_consent(consent_version)
    client_ip = request.client.host if request.client else "127.0.0.1"
    rate_key = "photo-check:" + (current_user.id if current_user else f"ip:{client_ip}")
    rate_limiter.check_rate_limit(rate_key, settings.PHOTO_CHECK_LIMIT_PER_DAY, label="photo check")

    raw = await read_limited_image(face_image, "Your photo")
    img_bytes, mime, _ext, _size = process_image(raw, "Your photo")
    return await run_in_threadpool(run_check, img_bytes, mime)
