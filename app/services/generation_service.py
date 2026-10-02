import base64
from typing import Optional
import io
import time
from datetime import datetime, timezone
from PIL import Image

from app.core.config import settings
from app.core.logging import logger
from app.db.session import SessionLocal
from app.db.models import GenerationRequestModel, ImageAssetModel, UsageEventModel
from app.services.provider_adapter import call_openai_image_edit, extract_cost_data
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

        # Call OpenAI provider
        person_tuple = (person_b, person_mime, person_ext)
        style_tuple = (style_b, style_mime, style_ext) if style_b is not None else None
        result = call_openai_image_edit(person_tuple, style_tuple, prompt, size)

        encoded = result.data[0].b64_json
        if not encoded:
            raise RuntimeError("Provider returned empty image payload.")

        raw_result = base64.b64decode(encoded)
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

        cost_data = extract_cost_data(result, settings.OPENAI_IMAGE_MODEL, settings.OPENAI_IMAGE_QUALITY, size)
        duration_ms = int((time.time() - start_time) * 1000)

        req.status = "succeeded"
        req.model_name = settings.OPENAI_IMAGE_MODEL
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
