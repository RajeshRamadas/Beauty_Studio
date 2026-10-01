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
        style_img = Image.open(io.BytesIO(style[0])).convert("RGB").resize(dim)

        # Smooth style blend maintaining target facial structure
        blended = Image.blend(person_img, style_img, 0.40)
        
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

def call_openai_image_edit(person, style, prompt, size):
    api_key = settings.OPENAI_API_KEY
    if not api_key or "your_" in api_key.lower() or "dummy" in api_key.lower():
        logger.warning("OPENAI_API_KEY not set. Using Demo AI Beauty Processor fallback.")
        return generate_demo_beauty_blend(person, style, prompt, size)

    try:
        client = OpenAI(api_key=api_key, timeout=120, max_retries=1)
        kwargs = dict(
            model=settings.OPENAI_IMAGE_MODEL,
            image=[
                (f"person.{person[2]}", person[0], person[1]),
                (f"style.{style[2]}", style[0], style[1]),
            ],
            prompt=prompt,
            size=size,
            quality=settings.OPENAI_IMAGE_QUALITY,
            output_format="png",
        )
        if settings.OPENAI_INPUT_FIDELITY:
            kwargs["input_fidelity"] = settings.OPENAI_INPUT_FIDELITY
        return client.images.edit(**kwargs)
    except Exception as exc:
        logger.warning("OpenAI API invocation failed (%s). Falling back to Demo AI Beauty Processor.", exc)
        return generate_demo_beauty_blend(person, style, prompt, size)
