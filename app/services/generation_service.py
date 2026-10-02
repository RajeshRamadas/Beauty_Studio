import base64
from typing import Optional
import io
import time
from datetime import datetime, timezone
from PIL import Image

from app.core.config import settings
from app.core.logging import logger
from app.db.session import SessionLocal
import json

from app.db.models import GenerationRequestModel, ImageAssetModel, QualityCheckModel, UsageEventModel
from app.services.provider_adapter import DEMO_MODEL_NAME, ProviderError, call_openai_image_edit, extract_cost_data
from app.services.result_judge import LABELS, JudgeFailed, judge_result
from app.services.storage import storage_service

def utc_now():
    return datetime.now(timezone.utc)

def process_generation_background_job(
    request_id: str,
    person_b: bytes,
    person_mime: str,
    person_ext: str,
    person_size: tuple,
    style_b: Optional[bytes],
    style_mime: str,
    style_ext: str,
    style_size: tuple,
    prompt: str,
    size: str,
    quality_context: Optional[dict] = None,
):
    db = SessionLocal()
    start_time = time.time()
    try:
        req = db.query(GenerationRequestModel).filter(GenerationRequestModel.id == request_id).first()
        if not req:
            logger.error("Background job request_id=%s not found in DB", request_id)
            return

        req.status = "processing"
        db.commit()

        # Save target and reference assets to storage & DB
        target_key = f"targets/{request_id}.{person_ext}"
        storage_service.save_image(target_key, person_b)
        db.add(ImageAssetModel(
            request_id=request_id,
            role="target",
            storage_key=target_key,
            mime_type=person_mime,
            byte_size=len(person_b),
            width=person_size[0],
            height=person_size[1],
        ))

        if style_b is not None:
            ref_key = f"references/{request_id}.{style_ext}"
            storage_service.save_image(ref_key, style_b)
            db.add(ImageAssetModel(
                request_id=request_id,
                role="reference",
                storage_key=ref_key,
                mime_type=style_mime,
                byte_size=len(style_b),
                width=style_size[0],
                height=style_size[1],
            ))

        # Call OpenAI, then score the result. Retry with feedback when it falls short of the
        # accuracy bar; if no attempt passes, fail without saving or showing any image.
        person_tuple = (person_b, person_mime, person_ext)
        style_tuple = (style_b, style_mime, style_ext) if style_b is not None else None
        ctx = quality_context or {}
        check_quality = settings.QUALITY_CHECK != "off"
        max_attempts = max(1, settings.QUALITY_MAX_ATTEMPTS) if check_quality else 1

        attempt_prompt = prompt
        best = None  # (raw_bytes, result, verdict)
        attempts = 0
        for attempts in range(1, max_attempts + 1):
            result = call_openai_image_edit(person_tuple, style_tuple, attempt_prompt, size)
            encoded = result.data[0].b64_json
            if not encoded:
                raise ProviderError("OpenAI returned an empty image. Please try again.")
            raw = base64.b64decode(encoded)
            if getattr(result, "demo", False) or not check_quality:
                best = (raw, result, None)
                break
            try:
                verdict = judge_result(person_b, person_mime, style_b, style_mime, raw,
                                       ctx.get("areas") or [], ctx.get("style_text") or "")
            except JudgeFailed as exc:
                logger.error("Quality check failed for request_id=%s: %s", request_id, exc)
                raise ProviderError("We couldn't verify the result's accuracy, so no image was saved. Please try again.")
            logger.info("request_id=%s attempt %d accuracy %d%% %s issues=%s", request_id, attempts,
                        verdict["overall"], verdict["scores"], verdict["issues"])
            if best is None or verdict["overall"] > best[2]["overall"]:
                best = (raw, result, verdict)
            if verdict["passed"]:
                break
            if verdict["issues"]:
                attempt_prompt = prompt + " Important, fix these problems seen in a previous attempt: " + "; ".join(verdict["issues"]) + "."

        raw_result, result, verdict = best
        if verdict is not None and not verdict["passed"]:
            weakest = min(verdict["scores"], key=verdict["scores"].get)
            reasons = ", ".join(verdict["issues"][:2]) or LABELS[weakest].lower() + " too low"
            raise ProviderError(
                f"We couldn't make an accurate enough result (best accuracy {verdict['overall']}%, "
                f"needs {settings.QUALITY_MIN_SCORE}%: {reasons}). No image was saved. "
                "Try a clearer front-facing photo, a closer style reference, or fewer changes at once."
            )

        res_img = Image.open(io.BytesIO(raw_result))
        res_w, res_h = res_img.size

        result_key = f"results/{request_id}.png"
        storage_service.save_image(result_key, raw_result)
        db.add(ImageAssetModel(
            request_id=request_id,
            role="result",
            storage_key=result_key,
            mime_type="image/png",
            byte_size=len(raw_result),
            width=res_w,
            height=res_h,
        ))

        is_demo = getattr(result, "demo", False)
        cost_data = extract_cost_data(result, settings.OPENAI_IMAGE_MODEL, settings.OPENAI_IMAGE_QUALITY, size)
        if is_demo:
            cost_data = dict(cost_data, cost_usd=0.0, cost_formatted="$0.000 (demo)")
        elif attempts > 1 and cost_data.get("cost_usd"):
            cost_data = dict(cost_data, cost_usd=round(cost_data["cost_usd"] * attempts, 4))  # every attempt is billed
        duration_ms = int((time.time() - start_time) * 1000)

        if verdict is not None:
            db.add(QualityCheckModel(
                request_id=request_id, overall=verdict["overall"], attempts=attempts,
                scores_json=json.dumps(verdict["scores"]), issues_json=json.dumps(verdict["issues"]),
            ))
        req.status = "succeeded"
        req.model_name = DEMO_MODEL_NAME if is_demo else settings.OPENAI_IMAGE_MODEL
        req.quality = settings.OPENAI_IMAGE_QUALITY
        req.size = size
        req.cost_usd = cost_data["cost_usd"]
        req.completed_at = utc_now()

        db.add(UsageEventModel(
            request_id=request_id,
            provider_status="succeeded",
            duration_ms=duration_ms,
        ))

        db.commit()
        logger.info("Background job succeeded: request_id=%s duration=%dms cost=%s", request_id, duration_ms, cost_data["cost_formatted"])

    except Exception as exc:
        db.rollback()
        duration_ms = int((time.time() - start_time) * 1000)
        if isinstance(exc, ProviderError):
            logger.error("Background job failed for request_id=%s: %s", request_id, exc)
        else:
            logger.exception("Background job failed for request_id=%s", request_id)
        try:
            req = db.query(GenerationRequestModel).filter(GenerationRequestModel.id == request_id).first()
            if req:
                req.status = "failed"
                req.error_message = str(exc)[:300]
                req.completed_at = utc_now()
                db.add(UsageEventModel(
                    request_id=request_id,
                    provider_status="failed",
                    duration_ms=duration_ms,
                ))
                db.commit()
        except Exception as db_exc:
            logger.error("Failed updating error status in DB: %s", db_exc)
    finally:
        db.close()
