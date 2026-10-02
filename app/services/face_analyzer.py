"""Face analysis with a vision model.

Looks at the user's photo and returns face shape, skin tone and undertone, hair
texture/length/thickness/colour, and recommendations drawn from the styles the
app can try on. Recommendations use the app's own catalogue so each one can be
opened as a try-on preset.
"""
import base64
import json
import re

from openai import OpenAI

from app.core.config import settings
from app.core.logging import logger


class FaceAnalysisUnavailable(Exception):
    """No provider key is configured."""


class FaceAnalysisFailed(Exception):
    """The provider call failed or returned something unusable."""


# Styles the app can try on, with the sample image used as the reference.
CATALOGUE = {
    "Hairstyle": {
        "Glamour Waves": "sample_glamour_waves.jpg",
        "Beach Waves": "sample_beach_waves.jpg",
        "Short Bob": "sample_short_bob.jpg",
        "Braided Updo": "sample_braided_updo.jpg",
        "Curtain Bangs": "sample_short_bob.jpg",
        "Volumetric Curls": "sample_glamour_waves.jpg",
    },
    "Makeup": {
        "Natural Glow": "sample_glamour_waves.jpg",
        "Soft Glam": "sample_beach_waves.jpg",
        "Smoky Eyes": "sample_short_bob.jpg",
        "Bridal Velvet": "sample_braided_updo.jpg",
        "Bold Lip": "sample_glamour_waves.jpg",
        "Party Bronze": "sample_beach_waves.jpg",
    },
    "Overall beauty look": {
        "Red Carpet": "sample_glamour_waves.jpg",
        "Evening Gala": "sample_braided_updo.jpg",
        "Korean Glass Skin": "sample_beach_waves.jpg",
        "Bridal Luxe": "sample_short_bob.jpg",
    },
}

FACE_SHAPES = ["Oval", "Round", "Square", "Heart", "Diamond", "Oblong", "Triangle"]
SKIN_TONES = ["Fair", "Light", "Medium", "Tan", "Deep"]
UNDERTONES = ["Cool", "Neutral", "Warm", "Olive"]
NOT_VISIBLE = "Not visible"


def _pick(names):
    return {
        "type": "array",
        "items": {
            "type": "object",
            "additionalProperties": False,
            "required": ["name", "reason"],
            "properties": {
                "name": {"type": "string", "enum": list(names)},
                "reason": {"type": "string"},
            },
        },
    }


SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "face_detected", "issue", "face_shape", "face_shape_reason", "skin_tone", "undertone",
        "hair_texture", "hair_length", "hair_thickness", "hair_colour", "summary",
        "hairstyles", "makeup", "full_looks", "hair_colours", "tips",
    ],
    "properties": {
        "face_detected": {"type": "boolean"},
        "issue": {"type": "string"},
        "face_shape": {"type": "string", "enum": FACE_SHAPES},
        "face_shape_reason": {"type": "string"},
        "skin_tone": {"type": "string", "enum": SKIN_TONES},
        "undertone": {"type": "string", "enum": UNDERTONES},
        "hair_texture": {"type": "string", "enum": ["Straight", "Wavy", "Curly", "Coily", NOT_VISIBLE]},
        "hair_length": {"type": "string", "enum": ["Short", "Medium", "Long", NOT_VISIBLE]},
        "hair_thickness": {"type": "string", "enum": ["Fine", "Medium", "Thick", NOT_VISIBLE]},
        "hair_colour": {"type": "string"},
        "summary": {"type": "string"},
        "hairstyles": _pick(CATALOGUE["Hairstyle"]),
        "makeup": _pick(CATALOGUE["Makeup"]),
        "full_looks": _pick(CATALOGUE["Overall beauty look"]),
        "hair_colours": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["name", "hex", "reason"],
                "properties": {
                    "name": {"type": "string"},
                    "hex": {"type": "string"},
                    "reason": {"type": "string"},
                },
            },
        },
        "tips": {"type": "array", "items": {"type": "string"}},
    },
}

INSTRUCTIONS = """You are a professional hairstylist and makeup artist giving a consultation from one photo.

Look at the person's face and hair and describe only what is visible:
- face_shape: judge from the proportions of forehead, cheekbones, jawline and face length; explain briefly in face_shape_reason.
- skin_tone and undertone: for choosing makeup and hair colour shades. Allow for the photo's lighting.
- hair texture, length, thickness and colour. Use "Not visible" if the hair is covered or out of frame.

Then recommend, choosing names only from the allowed lists:
- hairstyles: the 3 best, best first.
- makeup: the 3 best, best first.
- full_looks: the 1-2 best.
- hair_colours: 3 shades that suit the skin tone and undertone, each with a #RRGGBB hex.
- tips: 2-4 short, practical styling or makeup tips.
Each reason is one short sentence tied to what you saw (face shape, tone, hair type).
summary is 1-2 friendly sentences.

Rules:
- Do not guess or mention age, gender, race, ethnicity, health or attractiveness.
- If there is no clear single human face (no face, several faces, too blurry, face mostly hidden),
  set face_detected to false, explain in issue, and fill the other fields with your best neutral defaults.
  Otherwise set issue to an empty string.
- Write in plain, kind English."""

HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")


def _clean_picks(picks, category, limit):
    out, seen = [], set()
    for p in picks or []:
        name = p.get("name")
        if name in CATALOGUE[category] and name not in seen:
            seen.add(name)
            out.append({
                "name": name,
                "category": category,
                "reason": str(p.get("reason", ""))[:240],
                "image_url": CATALOGUE[category][name],
            })
    return out[:limit]


def _normalise(raw: dict) -> dict:
    colours = [
        {"name": str(c.get("name", ""))[:40], "hex": c["hex"], "reason": str(c.get("reason", ""))[:240]}
        for c in raw.get("hair_colours") or []
        if isinstance(c.get("hex"), str) and HEX.match(c["hex"])
    ][:4]
    return {
        "face_detected": bool(raw.get("face_detected")),
        "issue": str(raw.get("issue", ""))[:240],
        "face_shape": raw.get("face_shape"),
        "face_shape_reason": str(raw.get("face_shape_reason", ""))[:300],
        "skin_tone": raw.get("skin_tone"),
        "undertone": raw.get("undertone"),
        "hair": {
            "texture": raw.get("hair_texture"),
            "length": raw.get("hair_length"),
            "thickness": raw.get("hair_thickness"),
            "colour": str(raw.get("hair_colour", ""))[:60],
        },
        "summary": str(raw.get("summary", ""))[:400],
        "recommendations": {
            "hairstyles": _clean_picks(raw.get("hairstyles"), "Hairstyle", 3),
            "makeup": _clean_picks(raw.get("makeup"), "Makeup", 3),
            "full_looks": _clean_picks(raw.get("full_looks"), "Overall beauty look", 2),
        },
        "hair_colours": colours,
        "tips": [str(t)[:200] for t in (raw.get("tips") or [])][:4],
    }


def analyze_face(image_bytes: bytes, mime: str) -> dict:
    """Analyse a validated, downscaled image. Raises FaceAnalysisUnavailable/FaceAnalysisFailed."""
    api_key = settings.OPENAI_API_KEY
    if not api_key or "your_" in api_key.lower() or "dummy" in api_key.lower():
        raise FaceAnalysisUnavailable("Face analysis needs OPENAI_API_KEY to be set on the server.")

    data_url = f"data:{mime};base64," + base64.b64encode(image_bytes).decode("ascii")
    try:
        client = OpenAI(api_key=api_key, timeout=60, max_retries=1)
        resp = client.responses.create(
            model=settings.OPENAI_VISION_MODEL,
            instructions=INSTRUCTIONS,
            input=[{
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "Analyse this photo for a beauty consultation."},
                    {"type": "input_image", "image_url": data_url, "detail": "high"},
                ],
            }],
            text={"format": {"type": "json_schema", "name": "face_analysis", "schema": SCHEMA, "strict": True}},
        )
        raw = json.loads(resp.output_text)
    except Exception as exc:
        logger.warning("Face analysis failed: %s", exc)
        raise FaceAnalysisFailed("Face analysis is unavailable right now. Please try again.") from exc

    result = _normalise(raw)
    result["model"] = settings.OPENAI_VISION_MODEL
    return result
