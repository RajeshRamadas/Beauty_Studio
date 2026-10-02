import base64
import os
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi.concurrency import run_in_threadpool
from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Request, status, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, get_current_user_optional
from app.core.config import settings
from app.core.logging import logger
from app.core.rate_limiter import rate_limiter
from app.db.models import GenerationRequestModel, ImageAssetModel, UserModel, ConsentRecordModel
from app.schemas.generation import GenerationAcceptedResponse, GenerationStatusResponse, ImageAssetInfo
from app.services.image_processor import read_limited_image, process_image, pick_size
from app.services.generation_service import process_generation_background_job
from app.services.storage import storage_service

router = APIRouter()

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
    )

@router.post("/generations", status_code=202, response_model=GenerationAcceptedResponse)
async def create_generation(
    request: Request,
    background_tasks: BackgroundTasks,
    target_image: UploadFile = File(..., description="User target photo"),
    reference_image: UploadFile = File(..., description="Style reference image"),
    category: str = Form(...),
    style: str = Form(""),
    notes: str = Form(""),
    consent_version: str = Form("v1.0"),
    db: Session = Depends(get_db),
    current_user: Optional[UserModel] = Depends(get_current_user_optional),
):
    if category not in settings.CATEGORIES:
        raise HTTPException(400, "Unsupported beauty category.")


    # Rate limiting check
    client_ip = request.client.host if request.client else "127.0.0.1"
    rate_key = current_user.id if current_user else f"ip:{client_ip}"
    rate_limiter.check_rate_limit(rate_key)


    person_raw = await read_limited_image(target_image, "Target photo")
    style_raw = await read_limited_image(reference_image, "Style reference")

    person_b, person_mime, person_ext, person_size = process_image(person_raw, "Target photo")
    style_b, style_mime, style_ext, style_size = process_image(style_raw, "Style reference")

    category_instructions = {
        "Hairstyle": "Apply the hairstyle, cut, styling, and hair-color cues shown in the reference, while adapting naturally to the person's own hairline, head shape, and hair texture.",
        "Makeup": "Apply the makeup look, colors, finish, and placement shown in the reference, adapted naturally to the person's face and skin tone.",
        "Nail art": "Apply the nail-art design, colors, pattern, and finish shown in the reference.",
        "Overall beauty look": "Use the reference as inspiration for the overall beauty styling.",
    }
    prompt = (
        "You are editing two input images. IMAGE 1 is the target photo of the person and must remain the base image. "
        "IMAGE 2 is a style reference showing the desired look. Transfer the relevant style from IMAGE 2 onto the person in IMAGE 1. "
        f"Requested category: {category}. {category_instructions.get(category, '')} "
        "Use IMAGE 2 as a visual reference for style only; do not copy the reference person's identity, face, body, pose, or background. "
        "Preserve the target person's identity, facial features, face shape, skin tone, expression, age appearance, pose, camera angle, clothing, and background from IMAGE 1 as closely as possible."
    )
    if style.strip():
        prompt += f" Additional style description: {style.strip()[:300]}."
    if notes.strip():
        prompt += f" User notes: {notes.strip()[:500]}."

    size = pick_size(*person_size)
    request_id = str(uuid.uuid4())
    created_at = utc_now_iso()
    user_id = current_user.id if current_user else None

    # Create DB record with queued status
    db_req = GenerationRequestModel(
        id=request_id,
        user_id=user_id,
        category=category,
        style_description=style.strip()[:300] if style else None,
        notes=notes.strip()[:500] if notes else None,
        status="queued",
        model_name=settings.OPENAI_IMAGE_MODEL,
        quality=settings.OPENAI_IMAGE_QUALITY,
        size=size,
    )
    db.add(db_req)

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

    db.delete(req)
    db.commit()
    logger.info("Deleted generation request_id=%s by user_id=%s", request_id, current_user.id if current_user else "guest")

@router.post("/analyze-face")
async def analyze_face(
    request: Request,
    face_image: UploadFile = File(...),
    current_user: Optional[UserModel] = Depends(get_current_user_optional),
):
    """Analyse face shape, skin tone and hair, and recommend styles from the app's catalogue."""
    from app.services.face_analyzer import FaceAnalysisFailed, FaceAnalysisUnavailable, analyze_face as run_analysis

    client_ip = request.client.host if request.client else "127.0.0.1"
    rate_key = "analysis:" + (current_user.id if current_user else f"ip:{client_ip}")
    rate_limiter.check_rate_limit(rate_key, settings.ANALYSIS_LIMIT_PER_DAY, label="face analysis")

    raw = await read_limited_image(face_image, "Face photo")
    img_bytes, mime, _ext, _size = process_image(raw, "Face photo")
    try:
        return await run_in_threadpool(run_analysis, img_bytes, mime)
    except FaceAnalysisUnavailable as exc:
        raise HTTPException(503, str(exc))
    except FaceAnalysisFailed as exc:
        raise HTTPException(502, str(exc))
