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
    "face_detected": True, "issue": "", "style_section": "women", "facial_hair": "None",
    "face_shape": "Heart", "face_shape_reason": "Wider forehead and a narrow chin.",
    "skin_tone": "Medium", "undertone": "Warm",
    "hair_texture": "Wavy", "hair_length": "Long", "hair_thickness": "Thick", "hair_colour": "Dark brown",
    "summary": "Lovely warm tones.",
    "hairstyles": [
        {"name": "Curtain Bangs", "description": "Curtain Bangs styled for this person.", "reason": "Softens the forehead.", "closest_catalogue": "Curtain Bangs"},
        {"name": "Curtain Bangs", "description": "Curtain Bangs styled for this person.", "reason": "duplicate", "closest_catalogue": "Curtain Bangs"},
        {"name": "Beach Waves", "description": "Beach Waves styled for this person.", "reason": "Works with natural waves.", "closest_catalogue": "Beach Waves"},
    ],
    "makeup": [{"name": "Soft Glam", "description": "Soft Glam styled for this person.", "reason": "Warm shades suit you.", "closest_catalogue": "Soft Glam"}],
    "grooming": [{"name": "Full Beard", "description": "Full Beard styled for this person.", "reason": "should be dropped for women's section", "closest_catalogue": "Full Beard"}],
    "full_looks": [{"name": "Red Carpet", "description": "Red Carpet styled for this person.", "reason": "Balanced.", "closest_catalogue": "Red Carpet"}],
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


MEN_REPLY = dict(MODEL_REPLY, style_section="men", facial_hair="Short beard",
                 hairstyles=[{"name": "Classic Fade", "description": "Classic Fade styled for this person.", "reason": "Sharp.", "closest_catalogue": "Classic Fade"}, {"name": "Glamour Waves", "description": "Glamour Waves styled for this person.", "reason": "wrong section", "closest_catalogue": "Glamour Waves"}],
                 makeup=[{"name": "Soft Glam", "description": "Soft Glam styled for this person.", "reason": "dropped", "closest_catalogue": "Soft Glam"}],
                 grooming=[{"name": "Boxed Beard", "description": "Boxed Beard styled for this person.", "reason": "Defines the jaw.", "closest_catalogue": "Boxed Beard"}],
                 full_looks=[{"name": "Groom Look", "description": "Groom Look styled for this person.", "reason": "Polished.", "closest_catalogue": "Groom Look"}])


def _fake(monkeypatch, reply, seen=None):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test")

    class R:
        def create(self, **kw):
            if seen is not None:
                seen.update(kw)
            return SimpleNamespace(output_text=json.dumps(reply))

    monkeypatch.setattr(face_analyzer, "OpenAI", lambda **_: SimpleNamespace(responses=R()))


def test_womens_section_drops_grooming(monkeypatch):
    _fake(monkeypatch, MODEL_REPLY)
    data = client.post("/api/v1/analyze-face", files=_photo()).json()
    assert data["style_section"] == "women" and data["style_section_source"] == "photo"
    assert data["recommendations"]["grooming"] == []


def test_mens_section_from_photo(monkeypatch):
    _fake(monkeypatch, MEN_REPLY)
    data = client.post("/api/v1/analyze-face", files=_photo()).json()
    assert data["style_section"] == "men"
    rec = data["recommendations"]
    assert [h["name"] for h in rec["hairstyles"]] == ["Classic Fade", "Glamour Waves"]
    assert rec["hairstyles"][1]["closest_catalogue"] is None  # women's match dropped in the men's section
    assert rec["makeup"] == []
    assert rec["grooming"][0]["name"] == "Boxed Beard" and rec["grooming"][0]["image_url"] is None
    assert rec["full_looks"][0]["name"] == "Groom Look"


def test_user_choice_overrides_model(monkeypatch):
    seen = {}
    _fake(monkeypatch, MEN_REPLY, seen)
    data = client.post("/api/v1/analyze-face", files=_photo(), data={"section": "women"}).json()
    assert data["style_section"] == "women" and data["style_section_source"] == "you"
    names = [h["name"] for h in data["recommendations"]["hairstyles"]]
    assert names == ["Classic Fade", "Glamour Waves"]  # personalised suggestions are kept...
    assert data["recommendations"]["hairstyles"][0]["closest_catalogue"] is None  # ...but a men's catalogue match is dropped
    assert "chose the women's section" in seen["instructions"]



PERSONAL = dict(MODEL_REPLY, style_section="men",
    hairstyles=[
        {"name": "Curly taper fade", "description": "Low taper fade at the temples and nape, 5-6 cm defined curls on top.",
         "reason": "Keeps curl volume while slimming the square jaw.", "closest_catalogue": "Curly Top"},
        {"name": "Curly taper fade", "description": "duplicate", "reason": "x", "closest_catalogue": "none"},
        {"name": "Classic Fade", "description": "Exactly the catalogue classic fade.", "reason": "y", "closest_catalogue": "Classic Fade"},
        {"name": "No description", "description": "", "reason": "dropped", "closest_catalogue": "none"},
    ],
    grooming=[{"name": "Short boxed beard", "description": "1 cm boxed beard with a sharp cheek line and a low neckline.",
               "reason": "Sharpens the jaw.", "closest_catalogue": "Boxed Beard"}],
    avoid=[{"name": "Heavy fringe", "reason": "Hides the strong brow line."}])


def test_personalised_suggestions_keep_description_and_photo_rules(monkeypatch):
    _fake(monkeypatch, PERSONAL)
    rec = client.post("/api/v1/analyze-face", files=_photo()).json()
    data = rec
    hs = data["recommendations"]["hairstyles"]
    assert [h["name"] for h in hs] == ["Curly taper fade", "Classic Fade"]  # de-duplicated, empty description dropped
    assert hs[0]["description"].startswith("Low taper fade") and hs[0]["closest_catalogue"] == "Curly Top"
    assert hs[0]["image_url"] is None  # a similar style's photo is never shown for a different style
    assert data["recommendations"]["grooming"][0]["name"] == "Short boxed beard"
    assert data["avoid"] == [{"name": "Heavy fringe", "reason": "Hides the strong brow line."}]


def test_prompt_asks_for_personalised_varied_styles(monkeypatch):
    seen = {}
    _fake(monkeypatch, PERSONAL, seen)
    client.post("/api/v1/analyze-face", files=_photo())
    assert "NOT limited to the catalogue" in seen["instructions"]
    assert "Two different people must get different suggestions" in seen["instructions"]
