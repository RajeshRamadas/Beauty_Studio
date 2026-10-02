"""Scores a generated look against the user's photo and the requested style.

A vision model compares the original photo, the style reference (or the style's
description) and the result, and scores each criterion 0-100:
  identity        the same person: face, features, skin tone, age appearance
  style_match     the requested areas match the reference / description
  unchanged       areas that were not selected (and the background, pose) are unchanged
  realism         a natural photo with no artefacts, distortions or extra people
The overall accuracy is the lowest criterion, so one bad aspect fails the result.
"""
import base64
import json
from typing import Dict, List, Optional

from openai import OpenAI

from app.core.config import settings

CRITERIA = ["identity", "style_match", "unchanged", "realism"]
LABELS = {
    "identity": "Face kept",
    "style_match": "Style match",
    "unchanged": "Everything else unchanged",
    "realism": "Natural result",
}

AREA_NAMES = {
    "Hairstyle": "hair style (cut, length, shape)",
    "Hair colour": "hair colour",
    "Makeup": "makeup",
    "Nail art": "nails",
    "Beard & grooming": "beard and facial hair",
    "Overall beauty look": "overall hair, makeup and grooming look",
}

SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": CRITERIA + ["issues"],
    "properties": {
        **{c: {"type": "integer"} for c in CRITERIA},
        "issues": {"type": "array", "items": {"type": "string"}},
    },
}

INSTRUCTIONS = """You are a strict quality inspector for a beauty try-on app.
You get the ORIGINAL photo of a person, the requested STYLE (a reference photo and/or a description) and the RESULT.
Score each criterion from 0 to 100, where 90+ means a customer would accept it without hesitation:
- identity: is the RESULT clearly the same person as the ORIGINAL (face shape, eyes, nose, mouth, skin tone, age appearance)? Any change to facial features is a big deduction.
- style_match: do the requested areas in the RESULT match the requested style? Judge only the requested areas.
- unchanged: are areas that were NOT requested, plus pose, framing, clothing and background, the same as the ORIGINAL?
- realism: does the RESULT look like a real, natural photo with no artefacts, warped hands or hair, blur, extra people or text?
List each concrete problem in issues as a short phrase a stylist would say (e.g. "nose shape changed", "hair colour changed although not requested"). Empty list if none.
Be strict and consistent. Do not mention or speculate about gender, age, ethnicity or attractiveness."""


class JudgeFailed(Exception):
    """The quality check couldn't run."""


def _img(data: bytes, mime: str) -> Dict:
    return {"type": "input_image", "image_url": f"data:{mime};base64," + base64.b64encode(data).decode("ascii"), "detail": "high"}


def judge_result(person: bytes, person_mime: str, style: Optional[bytes], style_mime: Optional[str],
                 result: bytes, areas: List[str], style_text: str = "") -> Dict:
    requested = ", ".join(AREA_NAMES.get(a, a) for a in areas)
    content = [
        {"type": "input_text", "text": f"Requested areas to change: {requested}."
                                       + (f" Requested style: {style_text}." if style_text else "")},
        {"type": "input_text", "text": "ORIGINAL photo:"}, _img(person, person_mime),
    ]
    if style is not None:
        content += [{"type": "input_text", "text": "STYLE reference photo (use only for the requested areas):"}, _img(style, style_mime)]
    content += [{"type": "input_text", "text": "RESULT:"}, _img(result, "image/png")]
    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY, timeout=90, max_retries=1)
        resp = client.responses.create(
            model=settings.OPENAI_VISION_MODEL,
            instructions=INSTRUCTIONS,
            input=[{"role": "user", "content": content}],
            text={"format": {"type": "json_schema", "name": "result_quality", "schema": SCHEMA, "strict": True}},
        )
        raw = json.loads(resp.output_text)
    except Exception as exc:
        raise JudgeFailed(str(exc)[:200]) from exc

    scores = {c: max(0, min(100, int(raw.get(c, 0)))) for c in CRITERIA}
    overall = min(scores.values())
    return {
        "overall": overall,
        "scores": scores,
        "issues": [str(i)[:120] for i in (raw.get("issues") or [])][:5],
        "passed": overall >= settings.QUALITY_MIN_SCORE,
    }
