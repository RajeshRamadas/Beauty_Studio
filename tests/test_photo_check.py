import io
import json
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from PIL import Image, ImageEnhance, ImageFilter

from app.core.config import settings
from app.core.rate_limiter import rate_limiter
from app.main import app
from app.services import photo_check

client = TestClient(app)


def _upload(img):
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="JPEG", quality=95)
    return {"face_image": ("me.jpg", buf.getvalue(), "image/jpeg")}


@pytest.fixture
def sample():
    return Image.open("sample_short_bob.jpg")


@pytest.fixture(autouse=True)
def _reset(monkeypatch):
    rate_limiter._requests.clear()
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "")
    yield
    rate_limiter._requests.clear()


def codes(r):
    return [p["code"] for p in r.json()["problems"]]


def test_sharp_photo_passes_basic_check(sample):
    r = client.post("/api/v1/check-photo", files=_upload(sample))
    assert r.status_code == 200
    assert r.json() == {"usable": True, "problems": [], "level": "basic"}


def test_blurry_photo_rejected(sample):
    r = client.post("/api/v1/check-photo", files=_upload(sample.filter(ImageFilter.GaussianBlur(6))))
    assert r.json()["usable"] is False and "too_blurry" in codes(r)
    assert r.json()["problems"][0]["message"]


def test_dark_photo_rejected(sample):
    r = client.post("/api/v1/check-photo", files=_upload(ImageEnhance.Brightness(sample).enhance(0.25)))
    assert "too_dark" in codes(r)


def test_small_photo_rejected(sample):
    r = client.post("/api/v1/check-photo", files=_upload(sample.resize((300, 300))))
    assert "low_resolution" in codes(r)


def test_model_problems_added_when_key_set(monkeypatch, sample):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test")
    seen = {}

    class R:
        def create(self, **kw):
            seen.update(kw)
            return SimpleNamespace(output_text=json.dumps({"problems": ["hair_cut_off", "face_cut_off"]}))

    monkeypatch.setattr(photo_check, "OpenAI", lambda **_: SimpleNamespace(responses=R()))
    r = client.post("/api/v1/check-photo", files=_upload(sample))
    data = r.json()
    assert data["usable"] is False and data["level"] == "full"
    assert codes(r) == ["hair_cut_off", "face_cut_off"]
    assert seen["input"][0]["content"][1]["detail"] == "low"


def test_model_failure_falls_back_to_basic(monkeypatch, sample):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test")

    class Boom:
        def create(self, **_):
            raise RuntimeError("down")

    monkeypatch.setattr(photo_check, "OpenAI", lambda **_: SimpleNamespace(responses=Boom()))
    data = client.post("/api/v1/check-photo", files=_upload(sample)).json()
    assert data == {"usable": True, "problems": [], "level": "basic"}
