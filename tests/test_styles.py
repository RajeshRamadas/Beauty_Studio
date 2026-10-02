import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.api.v1.endpoints import generations
from app.core.config import settings
from app.core.rate_limiter import rate_limiter
from app.db.models import GenerationSelectionModel
from app.db.session import SessionLocal
from app.main import app
from app.services import catalog

client = TestClient(app)
CONSENT = {"consent_version": settings.PHOTO_CONSENT_VERSION}


@pytest.fixture(autouse=True)
def _reset_limits():
    rate_limiter._requests.clear()
    yield
    rate_limiter._requests.clear()


def _jpeg():
    buf = io.BytesIO()
    Image.new("RGB", (400, 500), (120, 100, 90)).save(buf, format="JPEG")
    return buf.getvalue()


def _photo():
    return {"target_image": ("me.jpg", _jpeg(), "image/jpeg")}


def _capture(monkeypatch):
    captured = {}
    monkeypatch.setattr(generations, "process_generation_background_job",
                        lambda *a, **k: captured.update(args=a, kw=k))
    return captured


# ── Catalogue ─────────────────────────────────────────────

def test_catalogue_has_the_required_templates():
    names = lambda cat, group: {t["name"] for t in catalog.published(cat, group) if t["group"] == group}  # noqa: E731
    assert len(names("Hairstyle", "men")) >= 29 and {"Buzz Cut", "Modern Mullet", "Man Bun"} <= names("Hairstyle", "men")
    assert len(names("Hairstyle", "women")) >= 34 and {"Butterfly Cut", "Chignon", "Wolf Cut"} <= names("Hairstyle", "women")
    assert len(names("Hair colour", "women")) == 17 and len(names("Hair colour", "men")) == 14
    assert len(catalog.published("Makeup")) == 25


def test_every_template_has_unique_id_and_required_fields():
    items = catalog.all_templates()
    ids = [t["id"] for t in items]
    assert len(ids) == len(set(ids))
    for t in items:
        assert t["name"] and t["category"] in catalog.CATEGORIES and t["description"] and t["version"] >= 1
        if t["category"] != "Overall beauty look":
            assert len(t["prompt"]) >= 15, t["id"]


def test_men_and_women_browse_separately_and_makeup_is_for_everyone():
    men = client.get("/api/v1/styles", params={"group": "men"}).json()
    women = client.get("/api/v1/styles", params={"group": "women"}).json()
    assert all(s["group"] in ("men", "all") for s in men)
    assert "hair_men_buzz_cut" in {s["id"] for s in men} and "hair_women_pixie_cut" not in {s["id"] for s in men}
    makeup_ids = {s["id"] for s in catalog.published("Makeup")}
    assert makeup_ids <= {s["id"] for s in men} and makeup_ids <= {s["id"] for s in women}
    everything = client.get("/api/v1/styles").json()
    assert len(everything) == len(catalog.published())


def test_public_view_hides_server_prompts():
    s = client.get("/api/v1/styles/hair_women_butterfly_cut").json()
    assert s["name"] == "Butterfly Cut" and "prompt" not in s and "status" not in s
    assert {"oval", "round", "square", "heart"} <= set(s["face_shapes"]) and "layers" in s["tags"]
    assert client.get("/api/v1/styles/nope").status_code == 404


def test_seed_sync_never_overwrites_admin_edits():
    db = SessionLocal()
    try:
        row = db.get(catalog.StyleTemplateModel, "nails_marble")
        row.name = "Marble (edited)"
        db.commit()
        assert catalog.sync_seed(db) == 0
        assert db.get(catalog.StyleTemplateModel, "nails_marble").name == "Marble (edited)"
        row.name = "Marble"
        db.commit()
    finally:
        db.close()
        catalog.invalidate()


# ── Generation from templates ─────────────────────────────

def test_composed_look_passes_each_template_distinctly(monkeypatch):
    captured = _capture(monkeypatch)
    r = client.post("/api/v1/generations", files=_photo(), data=dict(
        CONSENT, templates="makeup_natural_glow,hair_women_butterfly_cut,colour_women_caramel_balayage",
        intensity="subtle", keep_roots="true"))
    assert r.status_code == 202, r.text
    assert r.json()["category"] == "Hairstyle, Hair colour, Makeup"
    prompt = captured["args"][9]
    assert "Butterfly Cut: a butterfly cut" in prompt and "Caramel Balayage" in prompt and "Natural Glow" in prompt
    assert "roots" in prompt and "subtle" in prompt and "IMAGE 2" not in prompt
    rid = r.json()["request_id"]
    db = SessionLocal()
    rows = db.query(GenerationSelectionModel).filter_by(request_id=rid).all()
    db.close()
    assert {(x.area, x.template_id, x.template_version) for x in rows} == {
        ("Hairstyle", "hair_women_butterfly_cut", 1), ("Hair colour", "colour_women_caramel_balayage", 1),
        ("Makeup", "makeup_natural_glow", 1)}
    status = client.get(f"/api/v1/generations/{rid}").json()
    assert {s["template_id"] for s in status["selections"]} >= {"hair_women_butterfly_cut"}
    assert status["intensity"] == "subtle"


def test_template_with_photo_sends_it_as_reference(monkeypatch):
    captured = _capture(monkeypatch)
    r = client.post("/api/v1/generations", files=_photo(),
                    data=dict(CONSENT, templates="hair_women_classic_bob,makeup_rose_lip"))
    assert r.status_code == 202, r.text
    style_b, prompt = captured["args"][5], captured["args"][9]
    assert style_b is not None
    assert "used only for: hair style" in prompt and "(IMAGE 2 shows this style)" in prompt


def test_reference_photo_for_other_areas(monkeypatch):
    captured = _capture(monkeypatch)
    r = client.post("/api/v1/generations",
                    files=dict(_photo(), reference_image=("ref.jpg", _jpeg(), "image/jpeg")),
                    data=dict(CONSENT, templates="hair_men_textured_crop", category="Beard & grooming"))
    assert r.status_code == 202, r.text
    prompt = captured["args"][9]
    assert "Textured Crop" in prompt and "used only for: beard and grooming" in prompt


def test_rejects_two_templates_for_one_area_and_unknown_ids(monkeypatch):
    _capture(monkeypatch)
    r = client.post("/api/v1/generations", files=_photo(),
                    data=dict(CONSENT, templates="hair_men_buzz_cut,hair_men_crew_cut"))
    assert r.status_code == 400
    r = client.post("/api/v1/generations", files=_photo(), data=dict(CONSENT, templates="hair_men_nope"))
    assert r.status_code == 400
    r = client.post("/api/v1/generations", files=_photo(), data=dict(CONSENT, templates="look_women_red_carpet"))
    assert r.status_code == 400


def test_generation_needs_consent(monkeypatch):
    _capture(monkeypatch)
    r = client.post("/api/v1/generations", files=_photo(), data={"templates": "hair_men_buzz_cut"})
    assert r.status_code == 428


def test_personalised_style_from_face_analysis(monkeypatch):
    captured = _capture(monkeypatch)
    r = client.post("/api/v1/generations", files=_photo(), data=dict(
        CONSENT, custom_styles='[{"area": "Hairstyle", "name": "Curly taper fade", '
                               '"description": "Low taper fade, 5-6 cm defined curls on top."}]'))
    assert r.status_code == 202, r.text
    prompt = captured["args"][9]
    assert "Curly taper fade: Low taper fade, 5-6 cm defined curls" in prompt
    assert "Curly taper fade" in captured["kw"]["quality_context"]["style_text"]


def test_older_clients_style_name_still_works(monkeypatch):
    captured = _capture(monkeypatch)
    r = client.post("/api/v1/generations", files=_photo(),
                    data=dict(CONSENT, category="Beard & grooming", style="Short Boxed Beard"))
    assert r.status_code == 202, r.text
    assert "Short Boxed Beard" in captured["args"][9]
    r = client.post("/api/v1/generations", files=_photo(), data=dict(CONSENT, category="Hairstyle", style="Made up"))
    assert r.status_code == 400
    r = client.post("/api/v1/generations", files=_photo(),
                    data=dict(CONSENT, category="Hairstyle", style="Thing", style_description="short"))
    assert r.status_code == 400


def test_delete_removes_stored_images(monkeypatch):
    from app.db.models import ImageAssetModel
    from app.services.storage import storage_service
    _capture(monkeypatch)
    rid = client.post("/api/v1/generations", files=_photo(),
                      data=dict(CONSENT, templates="hair_men_buzz_cut")).json()["request_id"]
    storage_service.save_image(f"targets/{rid}.jpg", b"x")
    db = SessionLocal()
    db.add(ImageAssetModel(request_id=rid, role="target", storage_key=f"targets/{rid}.jpg", mime_type="image/jpeg",
                           byte_size=1, width=1, height=1))
    db.commit()
    db.close()
    assert client.delete(f"/api/v1/generations/{rid}").status_code == 204
    import os
    assert not os.path.exists(f"storage/targets/{rid}.jpg")
    assert client.get(f"/api/v1/generations/{rid}").status_code == 404
