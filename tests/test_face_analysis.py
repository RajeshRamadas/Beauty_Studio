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
CONSENT = {"consent_version": settings.PHOTO_CONSENT_VERSION}


def _photo():
    buf = io.BytesIO()
    Image.new("RGB", (400, 500), (200, 160, 140)).save(buf, format="JPEG")
    return {"face_image": ("me.jpg", buf.getvalue(), "image/jpeg")}


def _idea(name, template_id="none", description=None):
    return {"name": name, "description": f"{name}, described concretely for the editor." if description is None else description,
            "reason": "Fits what we saw.", "closest_template_id": template_id}


REPLY = {
    "face_visible": True, "issue": "", "lighting": "good", "suitable_for_tryon": True,
    "face_shape": {"value": "Heart", "confidence": "high"}, "face_shape_reason": "Wider forehead, narrow chin.",
    "skin_tone": {"value": "Medium", "confidence": "medium"}, "undertone": {"value": "Warm", "confidence": "medium"},
    "hair_length": "Long", "hair_texture": "Wavy", "hair_colour": "Dark brown", "facial_hair": "None",
    "summary": "Lovely warm tones.",
    "hairstyles": [_idea("Soft butterfly layers", "hair_women_butterfly_cut"), _idea("Soft butterfly layers"),
                   _idea("Glossy lob", "hair_men_buzz_cut"), _idea("No description", description="")],
    "makeup": [_idea("Peach glow", "makeup_natural_glow")],
    "grooming": [_idea("Should be dropped for the women's catalogue")],
    "tips": ["Add volume at the jaw."],
}


@pytest.fixture(autouse=True)
def _reset_limits():
    rate_limiter._requests.clear()
    yield
    rate_limiter._requests.clear()


def _fake(monkeypatch, reply, seen=None):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test")

    class R:
        def create(self, **kw):
            if seen is not None:
                seen.update(kw)
            return SimpleNamespace(output_text=json.dumps(reply))

    monkeypatch.setattr(face_analyzer, "OpenAI", lambda **_: SimpleNamespace(responses=R()))


def _analyse(data=None):
    return client.post("/api/v1/analyze-face", files=_photo(), data=dict(CONSENT, **(data or {})))


def test_requires_api_key(monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "")
    r = _analyse()
    assert r.status_code == 503 and "OPENAI_API_KEY" in r.json()["detail"]


def test_requires_consent(monkeypatch):
    _fake(monkeypatch, REPLY)
    assert client.post("/api/v1/analyze-face", files=_photo()).status_code == 428


def test_analysis_has_estimates_with_confidence(monkeypatch):
    seen = {}
    _fake(monkeypatch, REPLY, seen)
    data = _analyse({"group": "women"}).json()
    assert data["face_shape"] == {"value": "Heart", "confidence": "high"}
    assert data["undertone"] == {"value": "Warm", "confidence": "medium"}
    assert data["hair"] == {"visible_length": "Long", "texture": "Wavy", "natural_color_estimate": "Dark brown"}
    assert data["image_quality"] == {"face_visible": True, "lighting": "good", "suitable_for_tryon": True}
    # The photo is sent as an image input with a strict JSON schema that allows "Uncertain".
    content = seen["input"][0]["content"]
    assert content[1]["type"] == "input_image" and content[1]["image_url"].startswith("data:image/jpeg;base64,")
    assert seen["text"]["format"]["strict"] is True
    schema = seen["text"]["format"]["schema"]["properties"]
    assert "Uncertain" in schema["face_shape"]["properties"]["value"]["enum"]
    assert "Uncertain" in schema["undertone"]["properties"]["value"]["enum"]


def test_ideas_are_cleaned_and_linked_to_templates(monkeypatch):
    _fake(monkeypatch, REPLY)
    ideas = _analyse({"group": "women"}).json()["ideas"]
    hs = ideas["hairstyles"]
    assert [h["name"] for h in hs] == ["Soft butterfly layers", "Glossy lob"]  # de-duplicated, empty dropped
    assert hs[0]["closest_template"] == {"id": "hair_women_butterfly_cut", "name": "Butterfly Cut"}
    assert hs[1]["closest_template"] is None  # a men's template is not offered in the women's catalogue
    assert ideas["makeup"][0]["closest_template"]["id"] == "makeup_natural_glow"
    assert ideas["grooming"] == []


def test_catalogue_suggestions_ranked_from_the_analysis(monkeypatch):
    _fake(monkeypatch, REPLY)
    cat = _analyse({"group": "women"}).json()["catalogue"]
    top = cat["hairstyles"][0]
    assert top["label"] == "Suggested" and "heart" in top["face_shapes"] and "wavy" in top["textures"]
    assert any("heart face shapes" in r for r in top["reasons"])
    assert all(h["group"] in ("women", "all") for h in cat["hairstyles"])
    assert cat["hair_colour_note"] is None and cat["hair_colours"]
    assert all("warm" in c["undertones"] for c in cat["hair_colours"])
    assert cat["beard"] == []


def test_uncertain_estimates_are_not_used(monkeypatch):
    reply = dict(REPLY, face_shape={"value": "Uncertain", "confidence": "high"},
                 undertone={"value": "Uncertain", "confidence": "medium"}, hair_texture="Not visible",
                 hair_length="Not visible")
    _fake(monkeypatch, reply)
    data = _analyse({"group": "men"}).json()
    assert data["face_shape"] == {"value": "Uncertain", "confidence": "low"}
    cat = data["catalogue"]
    assert cat["hair_colours"] == [] and "couldn't estimate your undertone" in cat["hair_colour_note"]
    assert all(h["label"] == "Another option" and h["reasons"] == [] for h in cat["hairstyles"])


def test_preferences_filter_catalogue(monkeypatch):
    _fake(monkeypatch, REPLY)
    cat = _analyse({"group": "men", "maintenance": "low"}).json()["catalogue"]
    assert cat["hairstyles"] and all(h["maintenance"] == "low" for h in cat["hairstyles"])
    assert any("Matches your selected preference" in r for r in cat["hairstyles"][0]["reasons"])
    assert _analyse({"maintenance": "weekly"}).status_code == 400


def test_group_is_the_users_choice_and_never_inferred(monkeypatch):
    seen = {}
    _fake(monkeypatch, REPLY, seen)
    data = _analyse({"group": "men"}).json()
    assert data["group"] == "men"
    assert "men's catalogue" in seen["instructions"] and "Do not mention or guess the person's gender" in seen["instructions"]
    assert "style_section" not in seen["text"]["format"]["schema"]["properties"]
    assert _analyse({"section": "auto"}).json()["group"] == "all"  # older clients: no guessing


def test_no_face(monkeypatch):
    _fake(monkeypatch, dict(REPLY, face_visible=False, issue="Two faces in the photo."))
    data = _analyse().json()
    assert data["face_detected"] is False and data["catalogue"] is None and data["issue"]


def test_provider_error_is_502(monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test")

    class Boom:
        def create(self, **_):
            raise RuntimeError("down")

    monkeypatch.setattr(face_analyzer, "OpenAI", lambda **_: SimpleNamespace(responses=Boom()))
    assert _analyse().status_code == 502


def test_rejects_non_image(monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test")
    r = client.post("/api/v1/analyze-face", data=CONSENT, files={"face_image": ("x.txt", b"hello", "text/plain")})
    assert r.status_code == 400


def test_daily_limit(monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "")
    monkeypatch.setattr(settings, "ANALYSIS_LIMIT_PER_DAY", 2)
    assert [_analyse().status_code for _ in range(3)] == [503, 503, 429]


def test_recommendations_endpoint_reranks_without_ai():
    analysis = {"face_shape": {"value": "Round", "confidence": "medium"},
                "undertone": {"value": "Cool", "confidence": "high"},
                "hair": {"visible_length": "Short", "texture": "Curly"}}
    r = client.post("/api/v1/recommendations", json={"group": "men", "analysis": analysis,
                                                     "preferences": {"occasion": "professional"}})
    assert r.status_code == 200
    data = r.json()
    assert all("professional" in h["occasions"] for h in data["hairstyles"])
    assert data["hair_colours"] and all("cool" in c["undertones"] for c in data["hair_colours"])
    assert all(c["group"] in ("men", "all") for c in data["hair_colours"])
    assert data["beard"]
