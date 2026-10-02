"""Checks that a face photo is complete and clear enough to use.

Two layers:
- Local checks (always, free): resolution, brightness and blur, using Pillow.
- A vision-model check (when OPENAI_API_KEY is set): one clear face, face and
  hair fully in frame, not covered, close enough, facing the camera, no heavy
  filters. It uses low image detail to keep it fast and cheap.
"""
import base64
import io
import json
from typing import Dict, List

from openai import OpenAI
from PIL import Image, ImageFilter, ImageStat

from app.core.config import settings
from app.core.logging import logger

# Thresholds calibrated on the sample photos: sharp portraits score 400+,
# a light blur ~50-100, a heavy blur <15. Normal portraits average 80-160 brightness.
MIN_SHORT_SIDE = 400
DARK_BELOW = 45
BRIGHT_ABOVE = 230
BLURRY_BELOW = 30

MESSAGES: Dict[str, str] = {
    "low_resolution": "The photo is too small. Use a larger, higher-quality photo.",
    "too_dark": "The photo is too dark. Face a window or a bright light and try again.",
    "too_bright": "The photo is too bright or washed out. Move away from direct light.",
    "too_blurry": "The photo is blurry. Hold the phone steady and tap to focus on your face.",
    "no_face": "We can't see a face. Take a photo facing the camera.",
    "multiple_faces": "There's more than one person. Use a photo with only you in it.",
    "face_cut_off": "Part of your face is cut off. Fit your whole face in the frame.",
    "hair_cut_off": "Your hair is cut off. Include your whole head and hair, with a little space above.",
    "face_covered": "Your face is partly covered. Remove sunglasses, masks or hands from your face.",
    "face_too_small": "You're too far away. Move closer so your face and hair fill most of the frame.",
    "not_front_facing": "Your face is turned away. Look straight at the camera.",
    "heavy_filter": "The photo looks filtered or edited. Use an unfiltered photo.",
}
MODEL_CODES = [c for c in MESSAGES if c not in ("low_resolution", "too_dark", "too_bright")]

SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["problems"],
    "properties": {"problems": {"type": "array", "items": {"type": "string", "enum": MODEL_CODES}}},
}

INSTRUCTIONS = """You check selfies before a hair and makeup try-on. The photo must show exactly one person,
with the whole face and the whole head of hair in frame (top of the hair, both sides, chin and jaw),
nothing covering the face, the face large enough to see clearly, facing the camera, in focus and unfiltered.
List every problem you see using the allowed codes. Return an empty list if the photo is good.
Be strict about hair_cut_off and face_cut_off: if the top of the head or the chin touches or goes past the edge, report it.
Ignore clothing, background and expression."""


def local_problems(img: Image.Image) -> List[str]:
    problems = []
    if min(img.size) < MIN_SHORT_SIDE:
        problems.append("low_resolution")
    grey = img.convert("L")
    grey.thumbnail((512, 512))
    brightness = ImageStat.Stat(grey).mean[0]
    if brightness < DARK_BELOW:
        problems.append("too_dark")
    elif brightness > BRIGHT_ABOVE:
        problems.append("too_bright")
    edges = grey.filter(ImageFilter.FIND_EDGES)
    w, h = edges.size
    if w > 8 and h > 8 and ImageStat.Stat(edges.crop((2, 2, w - 2, h - 2))).var[0] < BLURRY_BELOW:
        problems.append("too_blurry")
    return problems


def model_problems(image_bytes: bytes, mime: str) -> List[str]:
    """Returns problem codes, or raises on provider failure."""
    client = OpenAI(api_key=settings.OPENAI_API_KEY, timeout=30, max_retries=1)
    data_url = f"data:{mime};base64," + base64.b64encode(image_bytes).decode("ascii")
    resp = client.responses.create(
        model=settings.OPENAI_VISION_MODEL,
        instructions=INSTRUCTIONS,
        input=[{"role": "user", "content": [
            {"type": "input_text", "text": "Check this photo."},
            {"type": "input_image", "image_url": data_url, "detail": "low"},
        ]}],
        text={"format": {"type": "json_schema", "name": "photo_check", "schema": SCHEMA, "strict": True}},
    )
    codes = json.loads(resp.output_text).get("problems") or []
    return [c for c in codes if c in MODEL_CODES]


def _key_configured() -> bool:
    key = settings.OPENAI_API_KEY
    return bool(key) and "your_" not in key.lower() and "dummy" not in key.lower()


def check_photo(image_bytes: bytes, mime: str) -> dict:
    img = Image.open(io.BytesIO(image_bytes))
    problems = local_problems(img)
    level = "basic"
    if _key_configured():
        try:
            for code in model_problems(image_bytes, mime):
                if code not in problems:
                    problems.append(code)
            level = "full"
        except Exception as exc:  # the basic result is still useful
            logger.warning("Photo check model call failed: %s", exc)
    return {
        "usable": not problems,
        "problems": [{"code": c, "message": MESSAGES[c]} for c in problems],
        "level": level,
    }
