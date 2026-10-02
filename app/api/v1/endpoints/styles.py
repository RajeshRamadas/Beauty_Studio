from typing import Optional

from fastapi import APIRouter, Query

from app.services.style_catalogue import styles_for

router = APIRouter()


@router.get("/styles")
def list_styles(audience: Optional[str] = Query(None, description="women or men; omit for all")):
    """Styles the app can try on. `image` is null for styles generated from their description."""
    return [
        {k: s[k] for k in ("name", "category", "audience", "image", "description")}
        for s in styles_for(audience)
    ]
