import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()

@router.get("/images/{key_path:path}")
def get_image_asset(key_path: str):
    # Sanitize path to prevent directory traversal
    clean_path = os.path.normpath(key_path)
    if clean_path.startswith("..") or clean_path.startswith("/"):
        raise HTTPException(400, "Invalid image path.")

    full_path = os.path.join("storage", clean_path)
    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        raise HTTPException(404, f"Image asset '{clean_path}' not found.")

    mime_type = "image/png" if clean_path.endswith(".png") else "image/jpeg"
    return FileResponse(full_path, media_type=mime_type)
