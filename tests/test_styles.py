import io

from fastapi.testclient import TestClient
from PIL import Image

from app.api.v1.endpoints import generations
from app.main import app

client = TestClient(app)


def test_styles_filtered_by_audience():
    men = client.get("/api/v1/styles", params={"audience": "men"}).json()
    women = client.get("/api/v1/styles", params={"audience": "women"}).json()
    assert men and women
    assert all(s["audience"] in ("men", "all") for s in men)
    assert {"Classic Fade", "Full Beard"} <= {s["name"] for s in men}
    assert "Glamour Waves" not in {s["name"] for s in men}
    assert any(s["category"] == "Beard & grooming" for s in men)
    assert len(client.get("/api/v1/styles").json()) == len(men) + len(women)


def _jpeg():
    buf = io.BytesIO()
    Image.new("RGB", (400, 500), (120, 100, 90)).save(buf, format="JPEG")
    return buf.getvalue()


def test_generation_without_reference_needs_catalogue_style(monkeypatch):
    monkeypatch.setattr(generations, "process_generation_background_job", lambda *a, **k: None)
    r = client.post("/api/v1/generations", files={"target_image": ("me.jpg", _jpeg(), "image/jpeg")},
                    data={"category": "Hairstyle", "style": "Something made up"})
    assert r.status_code == 400


def test_generation_text_only_for_catalogue_style(monkeypatch):
    captured = {}
    monkeypatch.setattr(generations, "process_generation_background_job", lambda *a, **k: captured.update(args=a))
    r = client.post("/api/v1/generations", files={"target_image": ("me.jpg", _jpeg(), "image/jpeg")},
                    data={"category": "Beard & grooming", "style": "Boxed Beard"})
    assert r.status_code == 202, r.text
    args = captured["args"]
    style_b, prompt = args[5], args[9]
    assert style_b is None
    assert "Boxed Beard" in prompt and "short boxed beard" in prompt and "IMAGE 2" not in prompt
