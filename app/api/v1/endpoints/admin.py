import re
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import get_admin_user, get_db
from app.core.config import settings
from app.db.models import (GenerationRequestModel, GenerationSelectionModel, StyleTemplateModel, UsageEventModel,
                           UserModel)
from app.services import catalog
from app.services.catalog_seed import ALL_SHAPES, _slug
from app.services.image_processor import read_limited_image

router = APIRouter()

@router.get("/admin/metrics")
def get_metrics(db: Session = Depends(get_db)):
    total_requests = db.query(func.count(GenerationRequestModel.id)).scalar() or 0
    succeeded_count = db.query(func.count(GenerationRequestModel.id)).filter(GenerationRequestModel.status == "succeeded").scalar() or 0
    failed_count = db.query(func.count(GenerationRequestModel.id)).filter(GenerationRequestModel.status == "failed").scalar() or 0
    total_cost_usd = db.query(func.sum(GenerationRequestModel.cost_usd)).scalar() or 0.0
    avg_duration_ms = db.query(func.avg(UsageEventModel.duration_ms)).scalar() or 0.0

    return {
        "status": "ok",
        "model": settings.OPENAI_IMAGE_MODEL,
        "quality": settings.OPENAI_IMAGE_QUALITY,
        "storage_type": settings.STORAGE_TYPE,
        "rate_limit_per_day": settings.RATE_LIMIT_PER_DAY,
        "telemetry": {
            "total_requests": total_requests,
            "succeeded_count": succeeded_count,
            "failed_count": failed_count,
            "total_cost_usd": round(float(total_cost_usd), 4),
            "total_cost_formatted": f"${total_cost_usd:.4f} USD",
            "average_duration_ms": round(float(avg_duration_ms), 1),
        },
    }


# ── Catalogue management (requirements 12) ──────────────────────────────────

ID_PREFIX = {"Hairstyle": "hair", "Hair colour": "colour", "Makeup": "makeup", "Beard & grooming": "beard",
             "Nail art": "nails", "Overall beauty look": "look"}


class TemplateIn(BaseModel):
    category: str
    group: str = "all"
    name: str = Field(..., min_length=2, max_length=80)
    description: str = Field("", max_length=300)
    prompt: str = Field("", max_length=600, description="What the image model is told to apply (server-side only)")
    extra_tags: List[str] = []
    face_shapes: List[str] = []
    lengths: List[str] = []
    textures: List[str] = []
    finish: Optional[str] = None
    maintenance: Optional[str] = None
    occasions: List[str] = []
    features: List[str] = []
    hex: Optional[str] = None
    undertones: List[str] = []
    technique: Optional[str] = None
    families: List[str] = []
    subcategory: Optional[str] = None
    intensity: Optional[str] = None
    attributes: List[str] = []
    parts: List[str] = []
    featured: bool = False
    sort_order: int = 1000


def _validate(t: Dict) -> None:
    if t["category"] not in catalog.CATEGORIES:
        raise HTTPException(400, "Unknown category.")
    if t["group"] not in catalog.GROUPS:
        raise HTTPException(400, "group must be women, men or all.")
    if t["category"] == "Makeup" and t["group"] != "all":
        raise HTTPException(400, "Makeup templates are available to everyone: use group 'all'.")
    if any(s not in ALL_SHAPES for s in t.get("face_shapes") or []):
        raise HTTPException(400, "face_shapes must be from: " + ", ".join(ALL_SHAPES))
    if t.get("hex") and not re.fullmatch(r"#[0-9A-Fa-f]{6}", t["hex"]):
        raise HTTPException(400, "hex must look like #A8743F.")
    for part in t.get("parts") or []:
        if not catalog.get(part, include_unpublished=True):
            raise HTTPException(400, f"Unknown template in parts: {part[:80]}")


def _publish_problems(t: Dict) -> List[str]:
    problems = []
    if not t.get("description"):
        problems.append("add a description")
    if t["category"] == "Overall beauty look":
        if len(t.get("parts") or []) < 2:
            problems.append("a look needs at least two templates in parts")
    elif len(t.get("prompt") or "") < 15:
        problems.append("add a try-on instruction (prompt) of at least 15 characters")
    return problems


def _row(db: Session, template_id: str) -> StyleTemplateModel:
    row = db.query(StyleTemplateModel).filter(StyleTemplateModel.id == template_id).first()
    if not row:
        raise HTTPException(404, "Template not found.")
    return row


def _admin_view(t: Dict) -> Dict:
    out = dict(t)
    out["warnings"] = _publish_problems(t) + ([] if t.get("images") or t["category"] in ("Hair colour", "Overall beauty look")
                                              else ["no reference image: tried on from its description"])
    return out


@router.get("/admin/catalog")
def admin_list(_admin: UserModel = Depends(get_admin_user)):
    """Every template, including drafts and archived ones, with the try-on instruction and warnings."""
    return [_admin_view(t) for t in catalog.all_templates(include_unpublished=True)]


@router.post("/admin/catalog", status_code=201)
def admin_create(body: TemplateIn, db: Session = Depends(get_db), _admin: UserModel = Depends(get_admin_user)):
    t = body.model_dump()
    _validate(t)
    base = f"{ID_PREFIX[t['category']]}_{t['group'] + '_' if t['category'] in ('Hairstyle', 'Hair colour', 'Overall beauty look') else ''}{_slug(t['name'])}"
    template_id, n = base, 2
    while db.query(StyleTemplateModel.id).filter(StyleTemplateModel.id == template_id).first():
        template_id, n = f"{base}_{n}", n + 1
    t.update(id=template_id, status="draft", version=1)
    db.add(catalog.row_from_dict(t))
    db.commit()
    catalog.invalidate()
    return _admin_view(catalog.get(template_id, include_unpublished=True))


@router.put("/admin/catalog/{template_id}")
def admin_update(template_id: str, body: TemplateIn, db: Session = Depends(get_db),
                 _admin: UserModel = Depends(get_admin_user)):
    row = _row(db, template_id)
    current = catalog.get(template_id, include_unpublished=True)
    t = dict(current, **body.model_dump())
    _validate(t)
    t["version"] = current["version"] + 1
    if t["status"] == "published" and _publish_problems(t):
        raise HTTPException(400, "A published template must stay complete: " + "; ".join(_publish_problems(t)))
    catalog.row_from_dict(t, row)
    db.commit()
    catalog.invalidate()
    return _admin_view(catalog.get(template_id, include_unpublished=True))


class StatusIn(BaseModel):
    status: str


@router.post("/admin/catalog/{template_id}/status")
def admin_set_status(template_id: str, body: StatusIn, db: Session = Depends(get_db),
                     _admin: UserModel = Depends(get_admin_user)):
    if body.status not in catalog.STATUSES:
        raise HTTPException(400, "status must be draft, published or archived.")
    row = _row(db, template_id)
    if body.status == "published":
        problems = _publish_problems(catalog.get(template_id, include_unpublished=True))
        if problems:
            raise HTTPException(400, "Can't publish yet: " + "; ".join(problems))
    row.status = body.status
    db.commit()
    catalog.invalidate()
    return _admin_view(catalog.get(template_id, include_unpublished=True))


@router.post("/admin/catalog/{template_id}/images")
async def admin_upload_image(template_id: str, view: str = Form("front"), image: UploadFile = File(...),
                             db: Session = Depends(get_db), _admin: UserModel = Depends(get_admin_user)):
    """Upload a front, side or back reference photo. Only upload photos you have the rights to use."""
    if view not in ("front", "side", "back"):
        raise HTTPException(400, "view must be front, side or back.")
    _row(db, template_id)
    raw = await read_limited_image(image, "The reference photo")
    catalog.attach_image(db, template_id, view, raw)
    return _admin_view(catalog.get(template_id, include_unpublished=True))


@router.delete("/admin/catalog/{template_id}/images/{view}")
def admin_remove_image(template_id: str, view: str, db: Session = Depends(get_db),
                       _admin: UserModel = Depends(get_admin_user)):
    row = _row(db, template_id)
    t = catalog.get(template_id, include_unpublished=True)
    t["images"] = {k: v for k, v in (t.get("images") or {}).items() if k != view}
    t["version"] += 1
    catalog.row_from_dict(t, row)
    db.commit()
    catalog.invalidate()
    return _admin_view(catalog.get(template_id, include_unpublished=True))


@router.get("/admin/catalog-metrics")
def admin_catalog_metrics(db: Session = Depends(get_db), _admin: UserModel = Depends(get_admin_user)):
    """Try-ons and success rate per template."""
    rows = (db.query(GenerationSelectionModel.template_id, GenerationRequestModel.status, func.count())
            .join(GenerationRequestModel, GenerationRequestModel.id == GenerationSelectionModel.request_id)
            .filter(GenerationSelectionModel.template_id.isnot(None))
            .group_by(GenerationSelectionModel.template_id, GenerationRequestModel.status).all())
    stats: Dict[str, Dict] = {}
    for template_id, status_, count in rows:
        s = stats.setdefault(template_id, {"tryons": 0, "succeeded": 0, "failed": 0})
        s["tryons"] += count
        if status_ in ("succeeded", "failed"):
            s[status_] += count
    for s in stats.values():
        done = s["succeeded"] + s["failed"]
        s["success_rate"] = round(100 * s["succeeded"] / done) if done else None
    return stats
