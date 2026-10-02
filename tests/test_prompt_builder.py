import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.api.v1.endpoints import generations
from app.main import app
from app.services.prompt_builder import build_prompt, parse_areas
from app.services.style_catalogue import get_style
from tests.test_styles import _jpeg

client = TestClient(app)


def test_parse_areas_validates_and_dedupes():
    assert parse_areas("Hairstyle, Makeup,Hairstyle") == ["Hairstyle", "Makeup"]
    assert parse_areas("Overall beauty look,Makeup") == ["Makeup"]
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


def test_text_only_prompt_uses_catalogue_description():
    style = get_style("Classic Fade")
    p = build_prompt(["Hairstyle"], False, style, style="Classic Fade", notes="shorter on top")
    assert "IMAGE 2" not in p and style["description"] in p
    assert "Additional style description" not in p  # the style name alone is not repeated
    assert "User notes: shorter on top." in p


def test_generation_accepts_multiple_areas(monkeypatch):
    captured = {}
    monkeypatch.setattr(generations, "process_generation_background_job", lambda *a, **k: captured.update(args=a))
    r = client.post("/api/v1/generations",
                    files={"target_image": ("me.jpg", _jpeg(), "image/jpeg"), "reference_image": ("ref.jpg", _jpeg(), "image/jpeg")},
                    data={"category": "Hairstyle,Hair colour,Makeup"})
    assert r.status_code == 202, r.text
    assert r.json()["category"] == "Hairstyle, Hair colour, Makeup"
    prompt = captured["args"][9]
    assert "Hair style:" in prompt and "Hair colour:" in prompt and "Makeup:" in prompt


def test_generation_rejects_empty_areas(monkeypatch):
    monkeypatch.setattr(generations, "process_generation_background_job", lambda *a, **k: None)
    r = client.post("/api/v1/generations",
                    files={"target_image": ("me.jpg", _jpeg(), "image/jpeg"), "reference_image": ("ref.jpg", _jpeg(), "image/jpeg")},
                    data={"category": " , "})
    assert r.status_code == 400
