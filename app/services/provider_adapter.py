import os
import io
import base64
from PIL import Image, ImageEnhance, ImageFilter
from openai import OpenAI
from app.core.config import settings
from app.core.logging import logger

class MockData:
    def __init__(self, b64_json):
        self.b64_json = b64_json

class MockOpenAIResult:
    def __init__(self, b64_json):
        self.data = [MockData(b64_json)]
        self.usage = None

def calculate_tier_cost(model: str, quality: str, size: str) -> float:
    if settings.CUSTOM_IMAGE_COST_USD:
        try:
            return float(settings.CUSTOM_IMAGE_COST_USD)
        except ValueError:
            pass

    model_lower = model.lower()
    quality_lower = quality.lower()
    is_square = (size == "1024x1024")

    if "dall-e-3" in model_lower:
        if quality_lower == "hd":
            return 0.080 if is_square else 0.120
        return 0.040 if is_square else 0.080

    if "dall-e-2" in model_lower:
        if size == "256x256":
            return 0.016
        if size == "512x512":
            return 0.018
        return 0.020

    # Default GPT Image pricing
    if quality_lower == "low":
        return 0.015 if is_square else 0.020
    elif quality_lower == "high":
        return 0.080 if is_square else 0.100
    else:  # medium or auto
        return 0.040 if is_square else 0.050

def extract_cost_data(result, model: str, quality: str, size: str) -> dict:
    usage_info = getattr(result, "usage", None)
    if usage_info and getattr(usage_info, "input_tokens", None) is not None:
        in_tok = getattr(usage_info, "input_tokens", 0) or 0
        out_tok = getattr(usage_info, "output_tokens", 0) or 0
        total_tok = getattr(usage_info, "total_tokens", 0) or (in_tok + out_tok)

        in_rate = settings.INPUT_TOKEN_RATE_PER_M
        out_rate = settings.OUTPUT_TOKEN_RATE_PER_M

        cost = (in_tok * (in_rate / 1_000_000)) + (out_tok * (out_rate / 1_000_000))
        return {
            "is_exact": True,
            "cost_usd": round(cost, 4),
            "cost_formatted": f"${cost:.4f} USD",
            "usage": {
                "input_tokens": in_tok,
                "output_tokens": out_tok,
                "total_tokens": total_tok,
            },
        }

    estimated = calculate_tier_cost(model, quality, size)
    return {
        "is_exact": False,
        "cost_usd": round(estimated, 3),
        "cost_formatted": f"~${estimated:.3f} USD (Demo Mode)",
        "usage": None,
    }

def generate_demo_beauty_blend(person, style, prompt, size):
    """
    Fallback processor when OPENAI_API_KEY is not configured or unavailable.
    Performs high-quality Pillow image blending & enhancement to simulate AI style transfer.
    """
    logger.info("Running Demo AI Beauty Processor fallback.")
    try:
        dim = (1024, 1024)
        if "512" in size:
            dim = (512, 512)
        elif "256" in size:
            dim = (256, 256)

        person_img = Image.open(io.BytesIO(person[0])).convert("RGB").resize(dim)
        if style is not None:
            style_img = Image.open(io.BytesIO(style[0])).convert("RGB").resize(dim)
            # Smooth style blend maintaining target facial structure
            blended = Image.blend(person_img, style_img, 0.40)
        else:
            blended = person_img
        
        # Color & Contrast enhancement
        enhancer = ImageEnhance.Color(blended)
        blended = enhancer.enhance(1.15)
        
        sharpener = ImageEnhance.Sharpness(blended)
        blended = sharpener.enhance(1.10)

        out = io.BytesIO()
        blended.save(out, format="PNG")
        b64_str = base64.b64encode(out.getvalue()).decode("utf-8")
        return MockOpenAIResult(b64_str)
    except Exception as e:
        logger.error("Failed demo beauty blend: %s", e)
        # Final fallback to raw person image
        b64_str = base64.b64encode(person[0]).decode("utf-8")
        return MockOpenAIResult(b64_str)

DEMO_MODEL_NAME = "demo (no AI)"


class ProviderError(Exception):
    """The image provider could not produce a result. The message is safe to show to users."""


def key_configured() -> bool:
    key = settings.OPENAI_API_KEY
    return bool(key) and "your_" not in key.lower() and "dummy" not in key.lower()


def explain_openai_error(exc: Exception) -> str:
    """Turn an OpenAI SDK error into a short, user-safe explanation."""
    status = getattr(exc, "status_code", None)
    body = getattr(exc, "body", None) or {}
    err = body.get("error", body) if isinstance(body, dict) else {}
    code = (err.get("code") or err.get("type") or "") if isinstance(err, dict) else ""
    detail = (err.get("message") if isinstance(err, dict) else None) or str(exc)
    detail = detail.replace(settings.OPENAI_API_KEY, "***") if settings.OPENAI_API_KEY else detail
    if status == 401 or code == "invalid_api_key":
        return "OpenAI rejected the API key. Check OPENAI_API_KEY on the server."
    if code in ("insufficient_quota", "billing_hard_limit_reached") or status == 402:
        return "The OpenAI account has no credit left or hit its billing limit."
    if status == 404 or code == "model_not_found":
        return f"OpenAI model '{settings.OPENAI_IMAGE_MODEL}' isn't available to this account. Check OPENAI_IMAGE_MODEL."
    if status == 403:
        return f"This OpenAI account can't use '{settings.OPENAI_IMAGE_MODEL}' (it may need organisation verification). {detail[:160]}"
    if code == "moderation_blocked" or "safety" in detail.lower():
        return "OpenAI's safety system declined this edit. Try a different photo or style."
    if status == 429:
        return "OpenAI is rate limiting this account. Wait a minute and try again."
    if status == 400:
        return f"OpenAI couldn't process this request: {detail[:200]}"
    if exc.__class__.__name__ in ("APITimeoutError", "APIConnectionError"):
        return "Couldn't reach OpenAI (timeout or network problem). Try again."
    return f"OpenAI request failed: {detail[:200]}"


def call_openai_image_edit(person, style, prompt, size):
    """Returns the provider result. Raises ProviderError with a user-safe message on failure.
    Uses the local demo blend only when DEMO_MODE is on."""
    if settings.DEMO_MODE:
        logger.warning("DEMO_MODE is on: blending photos locally instead of calling OpenAI.")
        result = generate_demo_beauty_blend(person, style, prompt, size)
        result.demo = True
        return result
    if not key_configured():
        raise ProviderError("OPENAI_API_KEY is not set on the server, so no AI edit was made.")

    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY, timeout=180, max_retries=1)
        kwargs = dict(
            model=settings.OPENAI_IMAGE_MODEL,
            image=[(f"person.{person[2]}", person[0], person[1])]
            + ([(f"style.{style[2]}", style[0], style[1])] if style is not None else []),
            prompt=prompt,
            size=size,
            quality=settings.OPENAI_IMAGE_QUALITY,
            output_format="png",
        )
        if settings.OPENAI_INPUT_FIDELITY:
            kwargs["input_fidelity"] = settings.OPENAI_INPUT_FIDELITY
        try:
            return client.images.edit(**kwargs)
        except Exception as exc:
            # High input fidelity keeps faces closer to the photo, but not every model accepts it:
            # if this one doesn't, retry once without it rather than failing.
            if "input_fidelity" in kwargs and "input_fidelity" in str(exc):
                logger.warning("Model %s doesn't accept input_fidelity; retrying without it.", settings.OPENAI_IMAGE_MODEL)
                kwargs.pop("input_fidelity")
                return client.images.edit(**kwargs)
            raise
    except Exception as exc:
        message = explain_openai_error(exc)
        logger.error("OpenAI image edit failed (model=%s): %s | %r", settings.OPENAI_IMAGE_MODEL, message, exc)
        raise ProviderError(message) from exc
