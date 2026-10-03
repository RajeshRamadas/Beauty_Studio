import io
import json
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from PIL import Image, ImageEnhance, ImageFilter, ImageStat

from app.api.v1.endpoints import generations
from app.core.config import settings
from app.core.rate_limiter import rate_limiter
from app.main import app
from app.services import face_analyzer, provider_adapter
from app.services.image_enhance import enhance, enhance_bytes

client = TestClient(app)
CONSENT = {"consent_version": settings.PHOTO_CONSENT_VERSION}
SAMPLES = ["sample_short_bob.jpg", "sample_glamour_waves.jpg", "sample_beach_waves.jpg", "sample_braided_updo.jpg"]


@pytest.fixture(autouse=True)
def _reset():
    rate_limiter._requests.clear()
    yield
    rate_limiter._requests.clear()


def _bob():
    return Image.open("sample_short_bob.jpg").convert("RGB")


def _jpeg(img):
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return buf.getvalue()


@pytest.mark.parametrize("name", SAMPLES)
def test_well_lit_portraits_are_left_untouched(name):
    assert enhance(Image.open(name))[1] == []


def test_dark_photo_is_brightened():
    dark = ImageEnhance.Brightness(_bob()).enhance(0.5)
    out, applied = enhance(dark)
    assert "brightened" in applied
    assert ImageStat.Stat(out.convert("L")).mean[0] > ImageStat.Stat(dark.convert("L")).mean[0] + 30


def test_strong_colour_cast_is_reduced_not_removed():
    r, g, b = _bob().split()
    warm = Image.merge("RGB", (r.point(lambda v: min(255, int(v * 1.25))), g, b.point(lambda v: int(v * 0.8))))
    out, applied = enhance(warm)
    assert applied == ["colour_balance"]
    ratio = lambda im: ImageStat.Stat(im).mean[0] / ImageStat.Stat(im).mean[2]  # noqa: E731
    assert ratio(_bob()) < ratio(out) < ratio(warm)  # closer to normal, still warmer than the original


def test_soft_photo_is_sharpened():
    assert enhance(_bob().filter(ImageFilter.GaussianBlur(2)))[1] == ["sharpened"]


def test_enhancement_can_be_turned_off(monkeypatch):
    monkeypatch.setattr(settings, "PHOTO_ENHANCE", False)
    data = _jpeg(ImageEnhance.Brightness(_bob()).enhance(0.5))
    assert enhance_bytes(data) == (data, [])


def test_generation_sends_the_enhanced_photo(monkeypatch):
    captured = {}
    monkeypatch.setattr(generations, "process_generation_background_job", lambda *a, **k: captured.update(args=a))
    dark = _jpeg(ImageEnhance.Brightness(_bob()).enhance(0.5))
    r = client.post("/api/v1/generations", files={"target_image": ("me.jpg", dark, "image/jpeg")},
                    data=dict(CONSENT, templates="hair_women_classic_bob"))
    assert r.status_code == 202, r.text
    assert "Brightened" in r.json()["enhancements"]
    sent = Image.open(io.BytesIO(captured["args"][1]))
    assert ImageStat.Stat(sent.convert("L")).mean[0] > 70


def test_photo_check_reports_planned_adjustments(monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "")
    r, g, b = _bob().split()
    warm = Image.merge("RGB", (r.point(lambda v: min(255, int(v * 1.25))), g, b.point(lambda v: int(v * 0.8))))
    data = client.post("/api/v1/check-photo", data=CONSENT, files={"face_image": ("me.jpg", _jpeg(warm), "image/jpeg")}).json()
    assert data["usable"] and data["enhancements"] == ["Balanced the colour of the light"]


def test_face_analysis_uses_side_photo(monkeypatch):
    from tests.test_face_analysis import REPLY
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test")
    seen = {}

    class R:
        def create(self, **kw):
            seen.update(kw)
            return SimpleNamespace(output_text=json.dumps(REPLY))

    monkeypatch.setattr(face_analyzer, "OpenAI", lambda **_: SimpleNamespace(responses=R()))
    photo = _jpeg(_bob())
    data = client.post("/api/v1/analyze-face", data=CONSENT, files={
        "face_image": ("front.jpg", photo, "image/jpeg"), "side_image": ("side.jpg", photo, "image/jpeg")}).json()
    content = seen["input"][0]["content"]
    assert [c["type"] for c in content] == ["input_text", "input_image", "input_text", "input_image"]
    assert "side (profile)" in content[2]["text"]
    assert data["photos_used"] == 2 and data["enhancements"] == []


def test_input_fidelity_falls_back_when_model_rejects_it(monkeypatch):
    monkeypatch.setattr(settings, "DEMO_MODE", False)
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test")
    monkeypatch.setattr(settings, "OPENAI_INPUT_FIDELITY", "high")
    calls = []

    class Images:
        def edit(self, **kw):
            calls.append(dict(kw))
            if "input_fidelity" in kw:
                raise RuntimeError("Unknown parameter: 'input_fidelity'.")
            return "ok"

    monkeypatch.setattr(provider_adapter, "OpenAI", lambda **_: SimpleNamespace(images=Images()))
    result = provider_adapter.call_openai_image_edit((b"x", "image/jpeg", "jpg"), None, "prompt", "1024x1024")
    assert result == "ok" and calls[0]["input_fidelity"] == "high" and "input_fidelity" not in calls[1]
