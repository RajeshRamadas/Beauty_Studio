import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.api.v1.endpoints import generations
from app.core.config import settings
from app.main import app
from app.services import catalog
from app.services.prompt_builder import build_prompt, compose_prompt, parse_areas
from tests.test_styles import _jpeg

client = TestClient(app)
CONSENT = {"consent_version": settings.PHOTO_CONSENT_VERSION}


def test_parse_areas_validates_and_dedupes():
    assert parse_areas("Hairstyle, Makeup,Hairstyle") == ["Hairstyle", "Makeup"]
    assert parse_areas("Overall beauty look,Makeup") == ["Makeup"]
    assert parse_areas("", required=False) == []
    with pytest.raises(HTTPException):
        parse_areas("")
    with pytest.raises(HTTPException):
        parse_areas("Tattoos")
    with pytest.raises(HTTPException):
        parse_areas("Hairstyle,Hair colour,Makeup,Nail art,Beard & grooming")


def test_longest_combination_fits_database_column():
    longest = ", ".join(["Beard & grooming", "Hair colour", "Hairstyle", "Nail art"])
    assert len(longest) <= 50


def test_reference_prompt_changes_only_selected_areas():
    p = build_prompt(["Hairstyle", "Makeup"], True, None)
    assert "IMAGE 2" in p and "Hair style:" in p and "Makeup:" in p
    assert "Keep unchanged:" in p and "natural hair colour" in p and "facial hair" in p
    assert "Hair colour:" not in p


def test_hair_colour_area_drops_keep_colour_rule():
    p = build_prompt(["Hairstyle", "Hair colour"], True, None)
    assert "Hair colour:" in p and "natural hair colour" not in p


def test_template_prompt_uses_server_text_and_area_rules():
    hair = catalog.get("hair_men_classic_taper")
    colour = catalog.get("colour_men_salt_and_pepper")
    p = compose_prompt([{"area": "Hairstyle", "source": "template", "template": hair},
                        {"area": "Hair colour", "source": "template", "template": colour}], "bold", True, "shorter on top")
    assert hair["prompt"] in p and colour["prompt"] in p
    assert "visible hairline" in p and "do not recolour skin, eyebrows" in p
    assert "roots" in p and "bold" in p and "User notes: shorter on top." in p
    assert "Keep unchanged:" in p and "the person's makeup" in p and "natural hair colour" not in p


def test_subtle_and_medium_intensity():
    t = catalog.get("makeup_soft_glam")
    spec = [{"area": "Makeup", "source": "template", "template": t}]
    assert "subtle" in compose_prompt(spec, "subtle")
    assert "subtle" not in compose_prompt(spec, "medium") and "bold" not in compose_prompt(spec, "medium")
    assert "skin texture and skin tone" in compose_prompt(spec)


def test_generation_accepts_multiple_reference_areas(monkeypatch):
    captured = {}
    monkeypatch.setattr(generations, "process_generation_background_job", lambda *a, **k: captured.update(args=a))
    r = client.post("/api/v1/generations",
                    files={"target_image": ("me.jpg", _jpeg(), "image/jpeg"), "reference_image": ("ref.jpg", _jpeg(), "image/jpeg")},
                    data=dict(CONSENT, category="Hairstyle,Hair colour,Makeup"))
    assert r.status_code == 202, r.text
    assert r.json()["category"] == "Hairstyle, Hair colour, Makeup"
    prompt = captured["args"][9]
    assert "Hair style:" in prompt and "Hair colour:" in prompt and "Makeup:" in prompt


def test_generation_rejects_empty_areas(monkeypatch):
    monkeypatch.setattr(generations, "process_generation_background_job", lambda *a, **k: None)
    r = client.post("/api/v1/generations",
                    files={"target_image": ("me.jpg", _jpeg(), "image/jpeg"), "reference_image": ("ref.jpg", _jpeg(), "image/jpeg")},
                    data=dict(CONSENT, category=" , "))
    assert r.status_code == 400
