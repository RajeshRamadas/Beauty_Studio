import io
import os
import logging

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from openai import OpenAI, APIStatusError
from PIL import Image, ImageOps

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("beauty-studio")

app = FastAPI(title="AI Beauty Studio — Style Reference Try-on")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

MAX_BYTES = 12 * 1024 * 1024
MIN_SIDE = int(os.getenv("MIN_IMAGE_SIDE", "256"))
MAX_SIDE = 1536  # downscale larger uploads to cut input cost
MODEL = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-2.5-flare")
QUALITY = os.getenv("OPENAI_IMAGE_QUALITY", "medium")  # low | medium | high | auto
FIDELITY = os.getenv("OPENAI_INPUT_FIDELITY", "")  # optional: "high" if your model supports it
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}
CATEGORIES = {"Hairstyle", "Makeup", "Nail art", "Overall beauty look"}

if QUALITY not in {"low", "medium", "high", "auto"}:
    raise RuntimeError("OPENAI_IMAGE_QUALITY must be low, medium, high or auto.")


@app.get("/")
def index():
    return FileResponse("index.html")


def calculate_cost(model: str, quality: str, size: str) -> float:
    """Calculate fallback estimated cost in USD based on OpenAI model, quality, and resolution pricing."""
    custom_cost = os.getenv("CUSTOM_IMAGE_COST_USD")
    if custom_cost:
        try:
            return float(custom_cost)
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

    # Default model pricing tiers (e.g. gpt-image models)
    if quality_lower == "low":
        return 0.015 if is_square else 0.020
    elif quality_lower == "high":
        return 0.080 if is_square else 0.100
    else:  # medium or auto
        return 0.040 if is_square else 0.050


def extract_usage_and_cost(result, model: str, quality: str, size: str) -> dict:
    """Extract exact usage tokens if returned by API provider, or compute tier estimate."""
    usage_info = getattr(result, "usage", None)
    if usage_info and getattr(usage_info, "input_tokens", None) is not None:
        in_tok = getattr(usage_info, "input_tokens", 0) or 0
        out_tok = getattr(usage_info, "output_tokens", 0) or 0
        total_tok = getattr(usage_info, "total_tokens", 0) or (in_tok + out_tok)

        in_rate = float(os.getenv("INPUT_TOKEN_RATE_PER_M", "8.00"))
        out_rate = float(os.getenv("OUTPUT_TOKEN_RATE_PER_M", "30.00"))

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

    estimated = calculate_cost(model, quality, size)
    return {
        "is_exact": False,
        "cost_usd": round(estimated, 3),
        "cost_formatted": f"~${estimated:.3f} USD (estimated)",
        "usage": None,
    }


@app.get("/health")
def health():
    est_cost = calculate_cost(MODEL, QUALITY, "1024x1024")
    return {
        "ok": True,
        "model": MODEL,
        "quality": QUALITY,
        "estimated_cost_per_image": f"~${est_cost:.3f} USD",
        "api_key_configured": bool(os.getenv("OPENAI_API_KEY")),
    }


async def read_limited(upload: UploadFile, label: str) -> bytes:
    raw = await upload.read(MAX_BYTES + 1)
    if not raw:
        raise HTTPException(400, f"{label} image is empty.")
    if len(raw) > MAX_BYTES:
        raise HTTPException(413, f"{label} image must be 12 MB or smaller.")
    return raw


def process_image(raw: bytes, label: str):
    """Validate, fix orientation, downscale and re-encode. Returns (bytes, mime, (w, h))."""
    try:
        probe = Image.open(io.BytesIO(raw))
        probe.verify()
        img = Image.open(io.BytesIO(raw))
        fmt = img.format
        img.load()
    except Exception:
        raise HTTPException(400, f"{label} is not a valid or complete image.")

    if fmt not in ALLOWED_FORMATS:
        raise HTTPException(400, f"{label}: use JPG, PNG, or WEBP.")

    img = ImageOps.exif_transpose(img)
    w, h = img.size
    if w < MIN_SIDE or h < MIN_SIDE:
        raise HTTPException(
            400, f"{label} image is {w} × {h} px; it must be at least {MIN_SIDE} × {MIN_SIDE} px."
        )

    img.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
    out = io.BytesIO()
    if img.mode in ("RGBA", "LA", "P"):
        img.convert("RGBA").save(out, format="PNG")
        mime, ext = "image/png", "png"
    else:
        img.convert("RGB").save(out, format="JPEG", quality=92)
        mime, ext = "image/jpeg", "jpg"
    return out.getvalue(), mime, ext, img.size


def pick_size(w: int, h: int) -> str:
    ratio = w / h
    if ratio > 1.2:
        return "1536x1024"
    if ratio < 0.83:
        return "1024x1536"
    return "1024x1024"


def call_provider(person, style, prompt, size):
    client = OpenAI(timeout=120, max_retries=1)
    kwargs = dict(
        model=MODEL,
        image=[
            (f"person.{person[2]}", person[0], person[1]),
            (f"style.{style[2]}", style[0], style[1]),
        ],
        prompt=prompt,
        size=size,
        quality=QUALITY,
        output_format="png",
    )
    if FIDELITY:
        kwargs["input_fidelity"] = FIDELITY
    return client.images.edit(**kwargs)


@app.post("/api/transform")
async def transform(
    person_image: UploadFile = File(...),
    style_image: UploadFile = File(...),
    category: str = Form(...),
    style: str = Form(""),
    notes: str = Form(""),
):
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(503, "OPENAI_API_KEY is not configured on the backend.")
    if category not in CATEGORIES:
        raise HTTPException(400, "Unsupported beauty category.")

    person_raw = await read_limited(person_image, "Your photo")
    style_raw = await read_limited(style_image, "Style reference")
    person_b, person_mime, person_ext, person_size = process_image(person_raw, "Your photo")
    style_b, style_mime, style_ext, _ = process_image(style_raw, "Style reference")

    category_instructions = {
        "Hairstyle": "Apply the hairstyle, cut, styling, and hair-color cues shown in the reference, while adapting naturally to the person's own hairline, head shape, and hair texture.",
        "Makeup": "Apply the makeup look, colors, finish, and placement shown in the reference, adapted naturally to the person's face and skin tone.",
        "Nail art": "Apply the nail-art design, colors, pattern, and finish shown in the reference. If the person's nails are not visible in the original photo, do not invent a misleading nail result; create a tasteful close-up consistent with the person only if feasible.",
        "Overall beauty look": "Use the reference as inspiration for the overall beauty styling, applying its visible hairstyle and/or makeup cues appropriately.",
    }
    prompt = (
        "You are editing two input images. IMAGE 1 is the target photo of the person and must remain the base image. "
        "IMAGE 2 is a style reference showing the desired look. Transfer the relevant style from IMAGE 2 onto the person in IMAGE 1. "
        f"Requested category: {category}. {category_instructions[category]} "
        "Use IMAGE 2 as a visual reference for style only; do not copy the reference person's identity, face, body, pose, or background. "
        "Preserve the target person's identity, facial features, face shape, skin tone, expression, age appearance, pose, camera angle, clothing, and background from IMAGE 1 as closely as possible. "
        "Make a natural-looking photorealistic preview. Do not add text, watermarks, extra people, or collage panels. "
        "If the requested styling conflicts with the target photo, adapt the style to fit the target person rather than replacing the person."
    )
    if style.strip():
        prompt += f" Additional style description: {style.strip()[:300]}."
    if notes.strip():
        prompt += f" User notes: {notes.strip()[:500]}."

    size = pick_size(*person_size)
    try:
        result = await run_in_threadpool(
            call_provider,
            (person_b, person_mime, person_ext),
            (style_b, style_mime, style_ext),
            prompt,
            size,
        )
        encoded = result.data[0].b64_json
        if not encoded:
            raise RuntimeError("Image provider returned no image data.")

        cost_data = extract_usage_and_cost(result, MODEL, QUALITY, size)
        log.info(
            "Transformation complete: model=%s size=%s cost=%s exact=%s",
            MODEL,
            size,
            cost_data["cost_formatted"],
            cost_data["is_exact"],
        )

        return {
            "image": encoded,
            "model": MODEL,
            "quality": QUALITY,
            "size": size,
            "cost_usd": cost_data["cost_usd"],
            "cost_formatted": cost_data["cost_formatted"],
            "is_exact_cost": cost_data["is_exact"],
            "usage": cost_data["usage"],
        }
    except APIStatusError as exc:
        log.exception("Provider returned HTTP %s", exc.status_code)
        raise HTTPException(
            502, f"Provider error {exc.status_code} ({type(exc).__name__}): {str(exc.message)[:300]}"
        )
    except Exception as exc:
        log.exception("Image edit failed")
        raise HTTPException(502, f"Image provider request failed ({type(exc).__name__}): {str(exc)[:300]}")


