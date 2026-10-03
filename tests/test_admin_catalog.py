import io
import uuid

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.core.config import settings
from app.db.models import StyleTemplateModel
from app.db.session import SessionLocal
from app.main import app
from app.services import catalog

client = TestClient(app)


def _token(email):
    client.post("/api/v1/auth/register", json={"email": email, "password": "pass"})
    return client.post("/api/v1/auth/token", data={"username": email, "password": "pass"}).json()["access_token"]


@pytest.fixture
def admin(monkeypatch):
    email = f"admin-{uuid.uuid4().hex[:8]}@example.com"
    monkeypatch.setattr(settings, "ADMIN_EMAILS", email)
    return {"Authorization": "Bearer " + _token(email)}


@pytest.fixture
def created():
    ids = []
    yield ids
    db = SessionLocal()
    for template_id in ids:
        row = db.get(StyleTemplateModel, template_id)
        if row:
            db.delete(row)
    db.commit()
    db.close()
    catalog.invalidate()


NEW = {"category": "Hairstyle", "group": "women", "name": "Test Bixie", "description": "Between a bob and a pixie",
       "prompt": "a bixie: a short cut between a pixie and a bob, ear length with soft layers",
       "face_shapes": ["oval", "heart"], "lengths": ["short"], "maintenance": "medium", "occasions": ["everyday"]}


def test_catalogue_management_needs_admin():
    assert client.get("/api/v1/admin/catalog").status_code == 401
    user = {"Authorization": "Bearer " + _token(f"user-{uuid.uuid4().hex[:8]}@example.com")}
    assert client.get("/api/v1/admin/catalog", headers=user).status_code == 403


def test_draft_publish_edit_archive(admin, created):
    r = client.post("/api/v1/admin/catalog", json=NEW, headers=admin)
    assert r.status_code == 201, r.text
    t = r.json()
    created.append(t["id"])
    assert t["id"] == "hair_women_test_bixie" and t["status"] == "draft" and t["version"] == 1
    assert "no reference image" in " ".join(t["warnings"])
    # Drafts are not in the public catalogue.
    assert t["id"] not in {s["id"] for s in client.get("/api/v1/styles").json()}

    assert client.post(f"/api/v1/admin/catalog/{t['id']}/status", json={"status": "published"}, headers=admin).status_code == 200
    assert t["id"] in {s["id"] for s in client.get("/api/v1/styles").json()}

    edited = client.put(f"/api/v1/admin/catalog/{t['id']}", json=dict(NEW, description="Edited"), headers=admin).json()
    assert edited["version"] == 2 and edited["description"] == "Edited" and edited["status"] == "published"

    assert client.post(f"/api/v1/admin/catalog/{t['id']}/status", json={"status": "archived"}, headers=admin).status_code == 200
    assert client.get(f"/api/v1/styles/{t['id']}").status_code == 404


def test_cannot_publish_incomplete_or_restrict_makeup(admin, created):
    t = client.post("/api/v1/admin/catalog", json=dict(NEW, name="Test Empty", prompt=""), headers=admin).json()
    created.append(t["id"])
    r = client.post(f"/api/v1/admin/catalog/{t['id']}/status", json={"status": "published"}, headers=admin)
    assert r.status_code == 400 and "try-on instruction" in r.json()["detail"]
    r = client.post("/api/v1/admin/catalog", json=dict(NEW, category="Makeup", group="women"), headers=admin)
    assert r.status_code == 400


def test_upload_reference_image(admin, created):
    t = client.post("/api/v1/admin/catalog", json=dict(NEW, name="Test Photo"), headers=admin).json()
    created.append(t["id"])
    buf = io.BytesIO()
    Image.new("RGB", (400, 500), (90, 60, 50)).save(buf, format="JPEG")
    r = client.post(f"/api/v1/admin/catalog/{t['id']}/images", data={"view": "side"},
                    files={"image": ("side.jpg", buf.getvalue(), "image/jpeg")}, headers=admin)
    assert r.status_code == 200, r.text
    url = r.json()["images"]["side"]
    assert url.startswith("/api/v1/catalog-images/") and r.json()["version"] == 2
    assert client.get(url).status_code == 200
    assert client.get("/api/v1/catalog-images/../../app.db").status_code == 404


def test_metrics(admin):
    r = client.get("/api/v1/admin/catalog-metrics", headers=admin)
    assert r.status_code == 200 and isinstance(r.json(), dict)
