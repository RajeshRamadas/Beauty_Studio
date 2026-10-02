import os
import re
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.services.storage import verify

router = APIRouter()

MIME = {".png": "image/png", ".webp": "image/webp"}


@router.get("/images/{key_path:path}")
def get_image_asset(key_path: str, exp: Optional[int] = None, sig: Optional[str] = None):
    """A customer image. Only reachable through a short-lived signed URL from the generation's owner."""
    # Sanitize path to prevent directory traversal
    clean_path = os.path.normpath(key_path)
    if clean_path.startswith("..") or clean_path.startswith("/"):
        raise HTTPException(400, "Invalid image path.")
    if exp is None or not verify(clean_path, exp, sig or ""):
        raise HTTPException(403, "This image link has expired or is invalid.")

    full_path = os.path.join("storage", clean_path)
    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        raise HTTPException(404, "Image not found.")
    return FileResponse(full_path, media_type=MIME.get(os.path.splitext(clean_path)[1], "image/jpeg"))


@router.get("/catalog-images/{name}")
def get_catalog_image(name: str):
    """A catalogue reference image uploaded by an admin (public, like the seed images)."""
    if not re.fullmatch(r"[a-z0-9_]+-(front|side|back)-[0-9a-f]{8}\.(jpg|png|webp)", name):
        raise HTTPException(404, "Image not found.")
    path = os.path.join("storage", "catalog", name)
    if not os.path.isfile(path):
        raise HTTPException(404, "Image not found.")
    return FileResponse(path, media_type=MIME.get(os.path.splitext(name)[1], "image/jpeg"))
