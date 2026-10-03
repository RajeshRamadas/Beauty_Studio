import base64
import io
from types import SimpleNamespace

import pytest
from PIL import Image

from app.core.config import settings
from app.db.models import GenerationRequestModel, ImageAssetModel, QualityCheckModel
from app.db.session import SessionLocal
from app.services import generation_service as gs


def _png(color):
    buf = io.BytesIO()
    Image.new("RGB", (64, 64), color).save(buf, format="PNG")
    return buf.getvalue()


def _result(color):
    return SimpleNamespace(data=[SimpleNamespace(b64_json=base64.b64encode(_png(color)).decode())], usage=None)


def _verdict(overall, issues=()):
    return {"overall": overall, "scores": {"identity": overall, "style_match": 95, "unchanged": 95, "realism": 95},
            "issues": list(issues), "passed": overall >= settings.QUALITY_MIN_SCORE}


def _new_request():
    db = SessionLocal()
    req = GenerationRequestModel(category="Hairstyle", status="queued")
    db.add(req)
    db.commit()
    rid = req.id
    db.close()
    return rid


def _run(rid):
    gs.process_generation_background_job(rid, _png("red"), "image/png", "png", (64, 64), None, None, None, None,
                                         "PROMPT", "1024x1024", quality_context={"areas": ["Hairstyle"], "style_text": "Bob"})
    db = SessionLocal()
    req = db.get(GenerationRequestModel, rid)
    results = db.query(ImageAssetModel).filter_by(request_id=rid, role="result").count()
    qc = db.query(QualityCheckModel).filter_by(request_id=rid).first()
    out = (req.status, req.error_message, results, qc.overall if qc else None, qc.attempts if qc else None)
    db.close()
    return out


@pytest.fixture
def calls(monkeypatch):
    monkeypatch.setattr(settings, "QUALITY_CHECK", "required")
    monkeypatch.setattr(settings, "QUALITY_MIN_SCORE", 90)
    monkeypatch.setattr(settings, "QUALITY_MAX_ATTEMPTS", 2)
    log = {"prompts": [], "verdicts": []}

    def fake_edit(person, style, prompt, size):
        log["prompts"].append(prompt)
        return _result("blue")

    def fake_judge(*a, **k):
        return log["verdicts"].pop(0)

    monkeypatch.setattr(gs, "call_openai_image_edit", fake_edit)
    monkeypatch.setattr(gs, "judge_result", fake_judge)
    return log


def test_passes_first_time(calls):
    calls["verdicts"] = [_verdict(94)]
    status, err, results, overall, attempts = _run(_new_request())
    assert (status, results, overall, attempts) == ("succeeded", 1, 94, 1)
    assert len(calls["prompts"]) == 1


def test_retries_with_feedback_then_passes(calls):
    calls["verdicts"] = [_verdict(70, ["nose shape changed"]), _verdict(92)]
    status, err, results, overall, attempts = _run(_new_request())
    assert (status, results, overall, attempts) == ("succeeded", 1, 92, 2)
    assert "nose shape changed" in calls["prompts"][1]


def test_rejects_when_never_accurate_and_saves_no_image(calls):
    calls["verdicts"] = [_verdict(60, ["face changed"]), _verdict(75, ["face changed"])]
    status, err, results, overall, attempts = _run(_new_request())
    assert status == "failed" and results == 0 and overall is None
    assert "best accuracy 75%" in err and "needs 90%" in err and "No image was saved" in err


def test_judge_failure_saves_no_image(calls, monkeypatch):
    def boom(*a, **k):
        raise gs.JudgeFailed("down")
    monkeypatch.setattr(gs, "judge_result", boom)
    status, err, results, overall, attempts = _run(_new_request())
    assert status == "failed" and results == 0 and "couldn't verify" in err


def test_status_response_includes_accuracy(calls):
    from fastapi.testclient import TestClient
    from app.main import app
    calls["verdicts"] = [_verdict(93)]
    rid = _new_request()
    _run(rid)
    data = TestClient(app).get(f"/api/v1/generations/{rid}").json()
    assert data["accuracy"] == 93 and data["attempts"] == 1
    assert data["accuracy_breakdown"]["Face kept"] == 93


def test_judge_overall_is_lowest_score(monkeypatch):
    import json
    from app.services import result_judge
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test")
    seen = {}

    class R:
        def create(self, **kw):
            seen.update(kw)
            return SimpleNamespace(output_text=json.dumps(
                {"identity": 97, "style_match": 88, "unchanged": 140, "realism": 93, "issues": ["waves too loose"]}))

    monkeypatch.setattr(result_judge, "OpenAI", lambda **_: SimpleNamespace(responses=R()))
    v = result_judge.judge_result(_png("red"), "image/png", None, None, _png("blue"), ["Hairstyle"], "Glamour Waves")
    assert v["scores"]["unchanged"] == 100  # clamped
    assert v["overall"] == 88 and v["passed"] is False and v["issues"] == ["waves too loose"]
    texts = [c.get("text", "") for c in seen["input"][0]["content"]]
    assert any("hair style" in t and "Glamour Waves" in t for t in texts)
