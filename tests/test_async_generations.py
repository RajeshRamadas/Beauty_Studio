import io
import time
from PIL import Image
from fastapi.testclient import TestClient
from app.core.config import settings
from app.main import app

settings.OPENAI_API_KEY = "test-key-123"
client = TestClient(app)


def create_dummy_jpeg(width=300, height=300, color="red"):
    img = Image.new("RGB", (width, height), color=color)
    out = io.BytesIO()
    img.save(out, format="JPEG")
    return out.getvalue()

def test_async_generation_creation_and_polling():
    target_bytes = create_dummy_jpeg(300, 300, "green")
    ref_bytes = create_dummy_jpeg(300, 300, "yellow")

    files = {
        "target_image": ("target.jpg", target_bytes, "image/jpeg"),
        "reference_image": ("ref.jpg", ref_bytes, "image/jpeg"),
    }
    data = {
        "category": "Hairstyle",
        "style": "short wavy bob",
        "notes": "keep natural tone",
    }

    # 1. Submit request -> HTTP 202 Accepted
    response = client.post("/api/v1/generations", files=files, data=data)
    assert response.status_code == 202
    res_data = response.json()
    assert "request_id" in res_data
    assert res_data["status"] == "queued"
    assert res_data["category"] == "Hairstyle"
    assert "status_url" in res_data

    request_id = res_data["request_id"]

    # 2. Poll status endpoint -> HTTP 200 OK
    poll_response = client.get(f"/api/v1/generations/{request_id}")
    assert poll_response.status_code == 200
    poll_data = poll_response.json()
    assert poll_data["request_id"] == request_id
    assert poll_data["category"] == "Hairstyle"
    assert poll_data["status"] in ["queued", "processing", "succeeded", "failed"]

def test_poll_nonexistent_request():
    response = client.get("/api/v1/generations/non-existent-uuid-12345")
    assert response.status_code == 404
