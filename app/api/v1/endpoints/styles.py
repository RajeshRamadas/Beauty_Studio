from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.services import catalog

router = APIRouter()


@router.get("/styles")
def list_styles(
    audience: Optional[str] = Query(None, description="Older name for group"),
    group: Optional[str] = Query(None, description="women or men (templates for all are included); omit for everything"),
    category: Optional[str] = Query(None),
):
    """Published catalogue templates. `image` is null for templates tried on from their description."""
    return [catalog.public_view(t) for t in catalog.published(category, group or audience)]


@router.get("/styles/{template_id}")
def get_style(template_id: str):
    t = catalog.get(template_id)
    if not t:
        raise HTTPException(404, "Style not found.")
    return catalog.public_view(t)
