"""Face analysis with a vision model.

Looks at the user's photo and returns face shape, skin tone and undertone, hair
texture/length/thickness/colour, and recommendations drawn from the style
catalogue so each one can be opened as a try-on preset.

Which section of the catalogue to recommend from (women's or men's styles) comes
from the user's choice when given. Otherwise the model suggests one from visible
styling cues such as facial hair and current haircut, and the user can switch.
"""
import base64
import json
import re
from typing import Optional

from openai import OpenAI

from app.core.config import settings
from app.core.logging import logger
from app.services.style_catalogue import STYLES, get_style


class FaceAnalysisUnavailable(Exception):
    """No provider key is configured."""


class FaceAnalysisFailed(Exception):
    """The provider call failed or returned something unusable."""


FACE_SHAPES = ["Oval", "Round", "Square", "Heart", "Diamond", "Oblong", "Triangle"]
SKIN_TONES = ["Fair", "Light", "Medium", "Tan", "Deep"]
UNDERTONES = ["Cool", "Neutral", "Warm", "Olive"]
NOT_VISIBLE = "Not visible"

# Recommendation groups: response key -> catalogue category, and how many to return.
GROUPS = {
    "hairstyles": ("Hairstyle", 4),
    "makeup": ("Makeup", 3),
    "grooming": ("Beard & grooming", 3),
    "full_looks": ("Overall beauty look", 2),
}


def _names(category):
    return [s["name"] for s in STYLES if s["category"] == category]


def _pick_schema(category):
    """Personalised suggestions: free-form, with the closest catalogue style (or "none") for reference."""
    return {
        "type": "array",
        "items": {
            "type": "object",
            "additionalProperties": False,
            "required": ["name", "description", "reason", "closest_catalogue"],
            "properties": {
                "name": {"type": "string"},
                "description": {"type": "string"},
                "reason": {"type": "string"},
                "closest_catalogue": {"type": "string", "enum": _names(category) + ["none"]},
            },
        },
    }


SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "face_detected", "issue", "style_section", "face_shape", "face_shape_reason", "skin_tone", "undertone",
        "hair_texture", "hair_length", "hair_thickness", "hair_colour", "facial_hair", "summary",
        "hairstyles", "makeup", "grooming", "full_looks", "hair_colours", "tips", "avoid",
    ],
    "properties": {
        "face_detected": {"type": "boolean"},
        "issue": {"type": "string"},
        "style_section": {"type": "string", "enum": ["women", "men", "unsure"]},
        "face_shape": {"type": "string", "enum": FACE_SHAPES},
        "face_shape_reason": {"type": "string"},
        "skin_tone": {"type": "string", "enum": SKIN_TONES},
        "undertone": {"type": "string", "enum": UNDERTONES},
        "hair_texture": {"type": "string", "enum": ["Straight", "Wavy", "Curly", "Coily", NOT_VISIBLE]},
        "hair_length": {"type": "string", "enum": ["Short", "Medium", "Long", NOT_VISIBLE]},
        "hair_thickness": {"type": "string", "enum": ["Fine", "Medium", "Thick", NOT_VISIBLE]},
        "hair_colour": {"type": "string"},
        "facial_hair": {"type": "string"},
        "summary": {"type": "string"},
        **{key: _pick_schema(cat) for key, (cat, _n) in GROUPS.items()},
        "hair_colours": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["name", "hex", "reason"],
                "properties": {"name": {"type": "string"}, "hex": {"type": "string"}, "reason": {"type": "string"}},
            },
        },
        "tips": {"type": "array", "items": {"type": "string"}},
        "avoid": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["name", "reason"],
                "properties": {"name": {"type": "string"}, "reason": {"type": "string"}},
            },
        },
    },
}


def _catalogue_text():
    lines = []
    for section in ("women", "men"):
        for cat in ("Hairstyle", "Makeup", "Beard & grooming", "Overall beauty look"):
            names = [s["name"] for s in STYLES if s["category"] == cat and s["audience"] in (section, "all")]
            if names:
                lines.append(f"- {section} / {cat}: {', '.join(names)}")
    return "\n".join(lines)


INSTRUCTIONS = f"""You are a professional hairstylist, barber and makeup artist giving a consultation from one photo.

Look at the person's face and hair and describe only what is visible:
- face_shape: judge from the proportions of forehead, cheekbones, jawline and face length; explain briefly in face_shape_reason.
- skin_tone and undertone: for choosing makeup, grooming and hair colour shades. Allow for the photo's lighting.
- hair texture, length, thickness and colour; use "Not visible" if hidden.
- facial_hair: describe any beard, moustache or stubble, or "None".

The app's style catalogue has two sections:
{_catalogue_text()}

SECTION TO RECOMMEND FROM: {{section_rule}}
Set style_section to the section you used.

Then recommend styles PERSONALISED to this person. You are NOT limited to the catalogue: design the
specific styles a top stylist would suggest for exactly this face shape, hair texture, density, length,
hairline and facial hair. Two different people must get different suggestions.
- hairstyles: 4 suggestions, best first, and make them genuinely different from each other:
  one that works with their current hair with minimal change, one polished/professional option,
  one bolder change, and one low-maintenance option.
- women's section: makeup = 3 suggestions; grooming = [].
- men's section: grooming = 3 suggestions (beard, moustache, stubble, brows); makeup = [].
- full_looks: 2 complete looks combining hair and makeup/grooming.
For each suggestion:
  name: a short, specific style name (max 5 words), e.g. "Curly taper fade", "Short boxed beard".
  description: one sentence a stylist or image editor could follow exactly: lengths (cm or clipper
    grade), fade/taper type and height, parting, fringe, texture and finish, shape lines. It is used to
    generate the try-on image, so be concrete and visual.
  reason: one sentence tied to what you saw (face shape, hair texture/density, facial hair, tone).
  closest_catalogue: the most similar style from the catalogue list for that category, or "none".
- avoid: 2 styles this person should avoid, each with a one-sentence reason.
- hair_colours: 3 shades that suit the skin tone and undertone, each with a #RRGGBB hex.
- tips: 2-4 short, practical hair, grooming or makeup tips.
summary is 1-2 friendly sentences.

Rules:
- Do not mention or speculate about the person's gender, age, race, ethnicity, health or attractiveness; talk only about features and styles.
- If there is no clear single human face (no face, several faces, too blurry, face mostly hidden),
  set face_detected to false, explain in issue, and fill the other fields with neutral defaults.
  Otherwise set issue to an empty string.
- Write in plain, kind English."""

SECTION_RULES = {
    "women": "The user chose the women's section. Use it.",
    "men": "The user chose the men's section. Use it.",
    "auto": ("The user did not choose. Pick the section whose styles best fit the person's current presentation, "
             "judging only from visible styling cues such as facial hair, current haircut and makeup. "
             "If the cues are mixed or unclear, use \"unsure\" and recommend from the women's section."),
}

HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")


def _clean_picks(picks, category, section, limit):
    out, seen = [], set()
    for p in picks or []:
        name = str(p.get("name", "")).strip()[:60]
        description = str(p.get("description", "")).strip()[:400]
        if not name or not description or name.lower() in seen:
            continue
        seen.add(name.lower())
        match = get_style(p.get("closest_catalogue"))
        if match and (match["category"] != category or
                      (section in ("women", "men") and match["audience"] not in (section, "all"))):
            match = None
        exact = match if match and match["name"].lower() == name.lower() else None
        out.append({
            "name": name,
            "category": category,
            "description": description,
            "reason": str(p.get("reason", ""))[:240],
            # Only show a photo when the suggestion IS that catalogue style; a similar style's photo would mislead.
            "image_url": exact["image"] if exact else None,
            "closest_catalogue": match["name"] if match else None,
        })
    return out[:limit]


def _normalise(raw: dict, requested: str) -> dict:
    if requested in ("women", "men"):
        section, source = requested, "you"
    else:
        model_section = raw.get("style_section")
        section = model_section if model_section in ("women", "men") else "women"
        source = "photo" if model_section in ("women", "men") else "default"

    colours = [
        {"name": str(c.get("name", ""))[:40], "hex": c["hex"], "reason": str(c.get("reason", ""))[:240]}
        for c in raw.get("hair_colours") or []
        if isinstance(c.get("hex"), str) and HEX.match(c["hex"])
    ][:4]
    recs = {key: _clean_picks(raw.get(key), cat, section, n) for key, (cat, n) in GROUPS.items()}
    if section == "men":
        recs["makeup"] = []
    else:
        recs["grooming"] = []
    return {
        "face_detected": bool(raw.get("face_detected")),
        "issue": str(raw.get("issue", ""))[:240],
        "style_section": section,
        "style_section_source": source,
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
        "facial_hair": str(raw.get("facial_hair", ""))[:80],
        "summary": str(raw.get("summary", ""))[:400],
        "recommendations": recs,
        "hair_colours": colours,
        "tips": [str(t)[:200] for t in (raw.get("tips") or [])][:4],
        "avoid": [{"name": str(a.get("name", ""))[:60], "reason": str(a.get("reason", ""))[:200]}
                  for a in (raw.get("avoid") or []) if a.get("name")][:3],
    }


def analyze_face(image_bytes: bytes, mime: str, section: Optional[str] = "auto") -> dict:
    """Analyse a validated, downscaled image. Raises FaceAnalysisUnavailable/FaceAnalysisFailed."""
    api_key = settings.OPENAI_API_KEY
    if not api_key or "your_" in api_key.lower() or "dummy" in api_key.lower():
        raise FaceAnalysisUnavailable("Face analysis needs OPENAI_API_KEY to be set on the server.")
    requested = section if section in ("women", "men") else "auto"

    data_url = f"data:{mime};base64," + base64.b64encode(image_bytes).decode("ascii")
    try:
        client = OpenAI(api_key=api_key, timeout=60, max_retries=1)
        resp = client.responses.create(
            model=settings.OPENAI_VISION_MODEL,
            instructions=INSTRUCTIONS.replace("{section_rule}", SECTION_RULES[requested]),
            input=[{
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "Analyse this photo for a beauty and grooming consultation."},
                    {"type": "input_image", "image_url": data_url, "detail": "high"},
                ],
            }],
            text={"format": {"type": "json_schema", "name": "face_analysis", "schema": SCHEMA, "strict": True}},
        )
        raw = json.loads(resp.output_text)
    except Exception as exc:
        logger.warning("Face analysis failed: %s", exc)
        raise FaceAnalysisFailed("Face analysis is unavailable right now. Please try again.") from exc

    result = _normalise(raw, requested)
    result["model"] = settings.OPENAI_VISION_MODEL
    return result
