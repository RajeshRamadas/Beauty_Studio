import io
from PIL import Image
import pytest
from fastapi import HTTPException
from app.services.image_processor import process_image, pick_size

def test_pick_size():
    assert pick_size(1500, 1000) == "1536x1024"
    assert pick_size(1000, 1500) == "1024x1536"
    assert pick_size(1000, 1000) == "1024x1024"

def test_process_valid_image():
    img = Image.new("RGB", (300, 400), color="red")
    out = io.BytesIO()
    img.save(out, format="JPEG")
    raw = out.getvalue()

    b, mime, ext, size = process_image(raw, "Test Image")
    assert mime == "image/jpeg"
    assert ext == "jpg"
    assert size == (300, 400)

def test_process_undersized_image():
    img = Image.new("RGB", (100, 100), color="blue")
    out = io.BytesIO()
    img.save(out, format="JPEG")
    raw = out.getvalue()

    with pytest.raises(HTTPException) as exc_info:
        process_image(raw, "Test Image")
    assert exc_info.value.status_code == 400
    assert "at least 256 × 256" in exc_info.value.detail
