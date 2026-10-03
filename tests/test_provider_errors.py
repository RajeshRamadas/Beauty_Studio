from types import SimpleNamespace

import pytest

from app.core.config import settings
from app.services import provider_adapter
from app.services.provider_adapter import ProviderError, call_openai_image_edit

PERSON = (b"x", "image/jpeg", "jpg")


class FakeAPIError(Exception):
    def __init__(self, status, code, message="boom"):
        super().__init__(message)
        self.status_code = status
        self.body = {"error": {"code": code, "message": message}}


def _client_raising(exc):
    class Images:
        def edit(self, **_):
            raise exc
    return lambda **_: SimpleNamespace(images=Images())


@pytest.fixture(autouse=True)
def _key(monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test-secret")
    monkeypatch.setattr(settings, "DEMO_MODE", False)


def test_no_key_fails_instead_of_faking(monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "")
    with pytest.raises(ProviderError, match="OPENAI_API_KEY is not set"):
        call_openai_image_edit(PERSON, None, "p", "1024x1024")


@pytest.mark.parametrize("status,code,expected", [
    (401, "invalid_api_key", "rejected the API key"),
    (429, "insufficient_quota", "no credit"),
    (404, "model_not_found", "isn't available to this account"),
    (400, "moderation_blocked", "safety system"),
    (429, "rate_limit_exceeded", "rate limiting"),
])
def test_api_errors_are_reported(monkeypatch, status, code, expected):
    monkeypatch.setattr(provider_adapter, "OpenAI", _client_raising(FakeAPIError(status, code)))
    with pytest.raises(ProviderError, match=expected):
        call_openai_image_edit(PERSON, None, "p", "1024x1024")


def test_error_message_never_contains_key(monkeypatch):
    exc = FakeAPIError(400, "bad", "Incorrect key sk-test-secret provided")
    monkeypatch.setattr(provider_adapter, "OpenAI", _client_raising(exc))
    with pytest.raises(ProviderError) as info:
        call_openai_image_edit(PERSON, None, "p", "1024x1024")
    assert "sk-test-secret" not in str(info.value)


def test_demo_mode_is_explicit_and_labelled(monkeypatch):
    import io
    from PIL import Image
    buf = io.BytesIO()
    Image.new("RGB", (300, 300), "red").save(buf, format="JPEG")
    monkeypatch.setattr(settings, "DEMO_MODE", True)
    result = call_openai_image_edit((buf.getvalue(), "image/jpeg", "jpg"), None, "p", "1024x1024")
    assert getattr(result, "demo", False) is True
