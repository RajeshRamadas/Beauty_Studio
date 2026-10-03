"""Face analysis with a vision model.

Estimates only visible characteristics, each with a confidence, and allows
"Uncertain" (requirements 3 and 8): face shape, undertone, skin tone, visible
hair length, texture and colour, and the image quality. It never infers sensitive
attributes such as gender, age or ethnicity: the user chooses which catalogue
group (women, men or all) to get suggestions from.

The result has two kinds of suggestions:
- "catalogue": templates ranked by recommender.py from the analysis, so every
  suggestion can be tried on as is and the full catalogue stays available;
- "ideas": new styles a stylist would design for this person, described
  concretely enough to be generated, each linked to the closest catalogue template.
"""
import base64
import json
from typing import Dict, List, Optional, Tuple

from openai import OpenAI

from app.core.config import settings
from app.core.logging import logger
from app.services import catalog, recommender


class FaceAnalysisUnavailable(Exception):
    """No provider key is configured."""


class FaceAnalysisFailed(Exception):
    """The provider call failed or returned something unusable."""


UNCERTAIN = "Uncertain"
NOT_VISIBLE = "Not visible"
FACE_SHAPES = ["Oval", "Round", "Square", "Heart", "Diamond", "Oblong", UNCERTAIN]
SKIN_TONES = ["Fair", "Light", "Medium", "Tan", "Deep", UNCERTAIN]
UNDERTONES = ["Warm", "Cool", "Neutral", "Olive", UNCERTAIN]
CONFIDENCE = ["high", "medium", "low"]
LENGTHS = ["Very short", "Short", "Medium", "Long", NOT_VISIBLE]
TEXTURES = ["Straight", "Wavy", "Curly", "Coily", NOT_VISIBLE]
LIGHTING = ["good", "dim", "harsh", "uneven"]

# Personalised idea groups: response key -> catalogue category, how many, and which catalogue groups get them.
IDEAS = {
    "hairstyles": ("Hairstyle", 3, ("women", "men", "all")),
    "makeup": ("Makeup", 2, ("women", "all")),
    "grooming": ("Beard & grooming", 2, ("men", "all")),
}


def _estimate(values):
    return {
        "type": "object", "additionalProperties": False, "required": ["value", "confidence"],
        "properties": {"value": {"type": "string", "enum": values}, "confidence": {"type": "string", "enum": CONFIDENCE}},
    }


def _idea_schema(ids: List[str]):
    return {
        "type": "array",
        "items": {
            "type": "object", "additionalProperties": False,
            "required": ["name", "description", "reason", "closest_template_id"],
            "properties": {
                "name": {"type": "string"},
                "description": {"type": "string"},
                "reason": {"type": "string"},
                "closest_template_id": {"type": "string", "enum": ids + ["none"]},
            },
        },
    }


def _ids(category: str, group: str) -> List[str]:
    return [t["id"] for t in catalog.published(category, group)]


def build_schema(group: str) -> Dict:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["face_visible", "issue", "lighting", "suitable_for_tryon", "face_shape", "face_shape_reason",
                     "skin_tone", "undertone", "hair_length", "hair_texture", "hair_colour", "facial_hair",
                     "summary", "hairstyles", "makeup", "grooming", "tips"],
        "properties": {
            "face_visible": {"type": "boolean"},
            "issue": {"type": "string"},
            "lighting": {"type": "string", "enum": LIGHTING},
            "suitable_for_tryon": {"type": "boolean"},
            "face_shape": _estimate(FACE_SHAPES),
            "face_shape_reason": {"type": "string"},
            "skin_tone": _estimate(SKIN_TONES),
            "undertone": _estimate(UNDERTONES),
            "hair_length": {"type": "string", "enum": LENGTHS},
            "hair_texture": {"type": "string", "enum": TEXTURES},
            "hair_colour": {"type": "string"},
            "facial_hair": {"type": "string"},
            "summary": {"type": "string"},
            **{key: _idea_schema(_ids(cat, group)) for key, (cat, _n, _g) in IDEAS.items()},
            "tips": {"type": "array", "items": {"type": "string"}},
        },
    }


def _catalogue_text(group: str) -> str:
    lines = []
    for cat in ("Hairstyle", "Makeup", "Beard & grooming"):
        items = catalog.published(cat, group)
        if items:
            lines.append(f"- {cat}: " + ", ".join(f"{t['name']} [{t['id']}]" for t in items))
    return "\n".join(lines)


GROUP_TEXT = {
    "women": "the women's catalogue",
    "men": "the men's catalogue",
    "all": "the whole catalogue (women's and men's styles)",
}

INSTRUCTIONS = """You are a professional hairstylist, barber and makeup artist giving a consultation from one photo.

Describe only what is visible, as estimates with a confidence (high, medium or low):
- face_shape: judge from the proportions of forehead, cheekbones, jawline and face length; explain briefly in
  face_shape_reason. Use "Uncertain" when the photo is angled, occluded, cropped or the proportions are ambiguous;
  never force a shape.
- skin_tone and undertone: for choosing makeup and hair colour shades. Lighting, white balance, camera processing
  and makeup change how skin looks: use "Uncertain" or low confidence unless the light is neutral and even.
- hair_length, hair_texture and hair_colour as visible; "Not visible" if hidden.
- facial_hair: describe any beard, moustache or stubble, or "None".
- lighting and suitable_for_tryon describe the photo; face_visible is false when there is no single clear face.

The user asked for suggestions from {group_text}:
{catalogue}

Then suggest NEW style ideas personalised to this person, designed for this face, hair texture, density, length,
hairline and facial hair. They may go beyond the catalogue. Two different people must get different ideas.
- hairstyles: 3 genuinely different ideas: one that works with the current hair, one polished option and one bolder change.
- makeup: {makeup_rule}
- grooming: {grooming_rule}
For each idea:
  name: a short, specific style name (max 5 words).
  description: one sentence an image editor could follow exactly: lengths (cm or clipper grade), fade or taper type
    and height, parting, fringe, texture and finish, shape lines, colours and placement for makeup.
  reason: one short, kind sentence tied to what you saw. Never say a style is bad or unsuitable.
  closest_template_id: the ID in brackets of the most similar catalogue template in that category, or "none".
- tips: 2-4 short, practical hair, grooming or makeup tips.
summary is 1-2 friendly sentences.

Rules:
- Do not mention or guess the person's gender, age, race, ethnicity, health or attractiveness; talk only about
  visible features and styles.
- If there is no clear single human face (no face, several faces, too blurry, face mostly hidden), set face_visible to
  false, explain in issue, use "Uncertain"/"Not visible" with low confidence and leave the idea lists empty.
  Otherwise set issue to an empty string.
- Write in plain, kind English."""

SIDE_PHOTO_NOTE = ("A second photo of the same person from the side (profile) follows. Use it together with the "
                   "front photo to judge jawline, chin, forehead and face length, and the hair's length, volume "
                   "and texture at the back and sides. Suggest only from what both photos show.")


def _data_url(data: bytes, mime: str) -> str:
    return f"data:{mime};base64," + base64.b64encode(data).decode("ascii")


def build_instructions(group: str) -> str:
    return (INSTRUCTIONS
            .replace("{group_text}", GROUP_TEXT[group])
            .replace("{catalogue}", _catalogue_text(group))
            .replace("{makeup_rule}", "2 ideas." if group in IDEAS["makeup"][2] else "[] (an empty list).")
            .replace("{grooming_rule}", "2 ideas (beard, moustache, stubble or brows)." if group in IDEAS["grooming"][2]
                     else "[] (an empty list)."))


def _est(raw: Dict, key: str, allowed: List[str]) -> Dict:
    e = raw.get(key) or {}
    value = e.get("value") if e.get("value") in allowed else UNCERTAIN
    confidence = e.get("confidence") if e.get("confidence") in CONFIDENCE else "low"
    if value == UNCERTAIN:
        confidence = "low"
    return {"value": value, "confidence": confidence}


def _clean_ideas(items, category: str, group: str, limit: int) -> List[Dict]:
    out, seen = [], set()
    allowed = {t["id"]: t for t in catalog.published(category, group)}
    for p in items or []:
        name = str(p.get("name", "")).strip()[:60]
        description = str(p.get("description", "")).strip()[:400]
        if not name or not description or name.lower() in seen:
            continue
        seen.add(name.lower())
        match = allowed.get(p.get("closest_template_id"))
        out.append({
            "name": name,
            "category": category,
            "description": description,
            "reason": str(p.get("reason", ""))[:240],
            "closest_template": {"id": match["id"], "name": match["name"]} if match else None,
        })
    return out[:limit]


def normalise(raw: Dict, group: str) -> Dict:
    pick = lambda v, allowed: v if v in allowed else NOT_VISIBLE  # noqa: E731
    analysis = {
        "face_shape": _est(raw, "face_shape", FACE_SHAPES),
        "skin_tone": _est(raw, "skin_tone", SKIN_TONES),
        "undertone": _est(raw, "undertone", UNDERTONES),
        "hair": {
            "visible_length": pick(raw.get("hair_length"), LENGTHS),
            "texture": pick(raw.get("hair_texture"), TEXTURES),
            "natural_color_estimate": str(raw.get("hair_colour", ""))[:60],
        },
        "image_quality": {
            "face_visible": bool(raw.get("face_visible")),
            "lighting": raw.get("lighting") if raw.get("lighting") in LIGHTING else "uneven",
            "suitable_for_tryon": bool(raw.get("suitable_for_tryon")) and bool(raw.get("face_visible")),
        },
    }
    ideas = {}
    for key, (cat, n, groups) in IDEAS.items():
        ideas[key] = _clean_ideas(raw.get(key), cat, group, n) if group in groups else []
    return {
        "face_detected": analysis["image_quality"]["face_visible"],
        "issue": str(raw.get("issue", ""))[:240],
        "group": group,
        **analysis,
        "face_shape_reason": str(raw.get("face_shape_reason", ""))[:300],
        "facial_hair": str(raw.get("facial_hair", ""))[:80],
        "summary": str(raw.get("summary", ""))[:400],
        "ideas": ideas,
        "tips": [str(t)[:200] for t in (raw.get("tips") or [])][:4],
    }


def analysis_for_ranking(result: Dict) -> Dict:
    """The parts of an analysis the recommender uses, lower-cased."""
    hair = result.get("hair") or {}
    return {
        "face_shape": {k: str(v).lower() for k, v in (result.get("face_shape") or {}).items()},
        "undertone": {k: str(v).lower() for k, v in (result.get("undertone") or {}).items()},
        "hair": {"visible_length": str(hair.get("visible_length", "")).lower(),
                 "texture": str(hair.get("texture", "")).lower()},
    }


def analyze_face(image_bytes: bytes, mime: str, group: Optional[str] = "all", prefs: Optional[Dict] = None,
                 side: Optional[Tuple[bytes, str]] = None) -> Dict:
    """Analyse a validated, downscaled image. Raises FaceAnalysisUnavailable/FaceAnalysisFailed."""
    api_key = settings.OPENAI_API_KEY
    if not api_key or "your_" in api_key.lower() or "dummy" in api_key.lower():
        raise FaceAnalysisUnavailable("Face analysis needs OPENAI_API_KEY to be set on the server.")
    group = group if group in ("women", "men", "all") else "all"

    content = [
        {"type": "input_text", "text": "Analyse this photo for a beauty and grooming consultation."},
        {"type": "input_image", "image_url": _data_url(image_bytes, mime), "detail": "high"},
    ]
    if side:
        content += [
            {"type": "input_text", "text": SIDE_PHOTO_NOTE},
            {"type": "input_image", "image_url": _data_url(*side), "detail": "high"},
        ]
    try:
        client = OpenAI(api_key=api_key, timeout=60, max_retries=1)
        resp = client.responses.create(
            model=settings.OPENAI_VISION_MODEL,
            instructions=build_instructions(group),
            input=[{
                "role": "user",
                "content": content,
            }],
            text={"format": {"type": "json_schema", "name": "face_analysis", "schema": build_schema(group),
                             "strict": True}},
        )
        raw = json.loads(resp.output_text)
    except Exception as exc:
        logger.warning("Face analysis failed: %s", exc)
        raise FaceAnalysisFailed("Face analysis is unavailable right now. Please try again.") from exc

    result = normalise(raw, group)
    result["photos_used"] = 2 if side else 1
    result["catalogue"] = (recommender.recommend(group, analysis_for_ranking(result), prefs)
                           if result["face_detected"] else None)
    result["model"] = settings.OPENAI_VISION_MODEL
    return result
