import io
from PIL import Image, ImageOps
from fastapi import HTTPException, UploadFile
from app.core.config import settings


async def read_limited_image(upload: UploadFile, label: str) -> bytes:
    raw_bytes = await upload.read(settings.MAX_BYTES + 1)
    if not raw_bytes:
        raise HTTPException(400, f"{label} image is empty.")
    if len(raw_bytes) > settings.MAX_BYTES:
        raise HTTPException(413, f"{label} image must be 12 MB or smaller.")
    return raw_bytes


def process_image(raw: bytes, label: str):
    """Validate, fix EXIF orientation, downscale if needed, and re-encode. Returns (bytes, mime, ext, (w, h))."""
    try:
        probe = Image.open(io.BytesIO(raw))
        probe.verify()
        img = Image.open(io.BytesIO(raw))
        fmt = img.format
        img.load()
    except Exception:
        raise HTTPException(400, f"{label} is not a valid or complete image.")

    if fmt not in settings.ALLOWED_FORMATS:
        raise HTTPException(400, f"{label}: use JPG, PNG, or WEBP.")

    img = ImageOps.exif_transpose(img)
    w, h = img.size
    if w < settings.MIN_SIDE or h < settings.MIN_SIDE:
        raise HTTPException(
            400, f"{label} image is {w} × {h} px; it must be at least {settings.MIN_SIDE} × {settings.MIN_SIDE} px."
        )

    img.thumbnail((settings.MAX_SIDE, settings.MAX_SIDE), Image.LANCZOS)
    out = io.BytesIO()
    if img.mode in ("RGBA", "LA", "P"):
        img.convert("RGBA").save(out, format="PNG")
        mime, ext = "image/png", "png"
    else:
        img.convert("RGB").save(out, format="JPEG", quality=92)
        mime, ext = "image/jpeg", "jpg"
    return out.getvalue(), mime, ext, img.size

def pick_size(w: int, h: int) -> str:
    ratio = w / h
    if ratio > 1.2:
        return "1536x1024"
    if ratio < 0.83:
        return "1024x1536"
    return "1024x1024"
