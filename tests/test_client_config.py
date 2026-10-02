from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app

client = TestClient(app)


def test_client_config_defaults_to_osm(monkeypatch):
    monkeypatch.setattr(settings, "GOOGLE_MAPS_API_KEY", "")
    data = client.get("/api/v1/client-config").json()
    assert data["maps"] == {"provider": "osm", "google_api_key": None, "google_map_id": None}


def test_client_config_uses_google_when_key_set(monkeypatch):
    monkeypatch.setattr(settings, "GOOGLE_MAPS_API_KEY", "test-key")
    monkeypatch.setattr(settings, "GOOGLE_MAPS_MAP_ID", "map-123")
    data = client.get("/api/v1/client-config").json()
    assert data["maps"] == {"provider": "google", "google_api_key": "test-key", "google_map_id": "map-123"}


def test_client_config_does_not_leak_server_secrets():
    body = client.get("/api/v1/client-config").text
    assert settings.SECRET_KEY not in body
    if settings.OPENAI_API_KEY:
        assert settings.OPENAI_API_KEY not in body
