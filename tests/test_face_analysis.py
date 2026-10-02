import io
import json
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.core.config import settings
from app.core.rate_limiter import rate_limiter
from app.main import app
from app.services import face_analyzer

client = TestClient(app)


def _photo():
    buf = io.BytesIO()
    Image.new("RGB", (400, 500), (200, 160, 140)).save(buf, format="JPEG")
    return {"face_image": ("me.jpg", buf.getvalue(), "image/jpeg")}


MODEL_REPLY = {
    "face_detected": True, "issue": "",
    "face_shape": "Heart", "face_shape_reason": "Wider forehead and a narrow chin.",
    "skin_tone": "Medium", "undertone": "Warm",
    "hair_texture": "Wavy", "hair_length": "Long", "hair_thickness": "Thick", "hair_colour": "Dark brown",
    "summary": "Lovely warm tones.",
    "hairstyles": [
        {"name": "Curtain Bangs", "reason": "Softens the forehead."},
        {"name": "Curtain Bangs", "reason": "duplicate"},
        {"name": "Beach Waves", "reason": "Works with natural waves."},
    ],
    "makeup": [{"name": "Soft Glam", "reason": "Warm shades suit you."}],
    "full_looks": [{"name": "Red Carpet", "reason": "Balanced."}],
    "hair_colours": [
        {"name": "Caramel", "hex": "#C68642", "reason": "Warm."},
        {"name": "Bad", "hex": "javascript:1", "reason": "invalid hex dropped"},
    ],
    "tips": ["Add volume at the jaw."],
}


@pytest.fixture(autouse=True)
def _reset_limits():
    rate_limiter._requests.clear()
    yield
    rate_limiter._requests.clear()


def test_requires_api_key(monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "")
    r = client.post("/api/v1/analyze-face", files=_photo())
    assert r.status_code == 503
    assert "OPENAI_API_KEY" in r.json()["detail"]


def test_returns_normalised_analysis(monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test")
    seen = {}

    class FakeResponses:
        def create(self, **kwargs):
            seen.update(kwargs)
            return SimpleNamespace(output_text=json.dumps(MODEL_REPLY))

    monkeypatch.setattr(face_analyzer, "OpenAI", lambda **_: SimpleNamespace(responses=FakeResponses()))
    r = client.post("/api/v1/analyze-face", files=_photo())
    assert r.status_code == 200
    data = r.json()
    assert data["face_shape"] == "Heart"
    assert data["hair"] == {"texture": "Wavy", "length": "Long", "thickness": "Thick", "colour": "Dark brown"}
    hs = data["recommendations"]["hairstyles"]
    assert [h["name"] for h in hs] == ["Curtain Bangs", "Beach Waves"]
    assert hs[0]["category"] == "Hairstyle" and hs[0]["image_url"].endswith(".jpg")
    assert data["recommendations"]["makeup"][0]["category"] == "Makeup"
    assert data["hair_colours"] == [{"name": "Caramel", "hex": "#C68642", "reason": "Warm."}]
    # The photo is sent as an image input with a strict JSON schema.
    content = seen["input"][0]["content"]
    assert content[1]["type"] == "input_image" and content[1]["image_url"].startswith("data:image/jpeg;base64,")
    assert seen["text"]["format"]["strict"] is True


def test_provider_error_is_502(monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test")

    class Boom:
        def create(self, **_):
            raise RuntimeError("down")

    monkeypatch.setattr(face_analyzer, "OpenAI", lambda **_: SimpleNamespace(responses=Boom()))
    r = client.post("/api/v1/analyze-face", files=_photo())
    assert r.status_code == 502


def test_rejects_non_image(monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test")
    r = client.post("/api/v1/analyze-face", files={"face_image": ("x.txt", b"hello", "text/plain")})
    assert r.status_code == 400


def test_daily_limit(monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "")
    monkeypatch.setattr(settings, "ANALYSIS_LIMIT_PER_DAY", 2)
    codes = [client.post("/api/v1/analyze-face", files=_photo()).status_code for _ in range(3)]
    assert codes == [503, 503, 429]
