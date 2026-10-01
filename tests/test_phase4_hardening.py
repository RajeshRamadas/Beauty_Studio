import io
from PIL import Image
from fastapi.testclient import TestClient
from app.core.config import settings
from app.core.rate_limiter import rate_limiter
from app.main import app

settings.OPENAI_API_KEY = "test-key-123"
client = TestClient(app)

def create_dummy_jpeg(width=300, height=300, color="red"):
    img = Image.new("RGB", (width, height), color=color)
    out = io.BytesIO()
    img.save(out, format="JPEG")
    return out.getvalue()

def test_rate_limiter_enforcement():
    # Set low rate limit for test
    test_key = "test_rate_user_123"
    
    # 1. First 2 requests pass
    rate_limiter.check_rate_limit(test_key, max_requests=2)
    rate_limiter.check_rate_limit(test_key, max_requests=2)

    # 2. 3rd request throws 429
    import pytest
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        rate_limiter.check_rate_limit(test_key, max_requests=2)
    assert exc_info.value.status_code == 429
    assert "Daily generation quota exceeded" in exc_info.value.detail

def test_admin_metrics_endpoint():
    response = client.get("/api/v1/admin/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "telemetry" in data
    assert "total_requests" in data["telemetry"]
    assert "total_cost_usd" in data["telemetry"]

def test_image_delivery_endpoint():
    # Attempt to fetch nonexistent image
    res = client.get("/api/v1/images/nonexistent_file.png")
    assert res.status_code == 404

    # Traversal attack check (rejected by router or endpoint path validation)
    res_bad = client.get("/api/v1/images/../app/main.py")
    assert res_bad.status_code in [400, 404]

