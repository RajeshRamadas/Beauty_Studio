"""Builds the image-edit prompt for one or more areas to change."""
from typing import Dict, List, Optional

from fastapi import HTTPException

from app.core.config import settings

# Wording when a reference image (IMAGE 2) is supplied.
WITH_REFERENCE = {
    "Hairstyle": "Hair style: apply the haircut, length, shape and styling from IMAGE 2, adapted naturally to the person's hairline, head shape and hair texture.",
    "Hair colour": "Hair colour: apply the hair colour, tone and any highlights from IMAGE 2.",
    "Makeup": "Makeup: apply the makeup look, colours, finish and placement from IMAGE 2, adapted to the person's face and skin tone.",
    "Nail art": "Nails: apply the nail design, colours, pattern and finish from IMAGE 2 to any visible nails.",
    "Beard & grooming": "Beard and grooming: apply the beard, moustache and facial-hair shape from IMAGE 2, adapted to the person's jawline and hair colour.",
    "Overall beauty look": "Overall look: use IMAGE 2 as inspiration for the complete hair, makeup and grooming styling.",
}

# Wording when the style is described in text only (catalogue style, no reference image).
TEXT_ONLY = {
    "Hairstyle": "Hair style: change the haircut and styling to match the style described, adapted to the person's hairline, head shape and hair texture.",
    "Hair colour": "Hair colour: change the hair colour to suit the style described.",
    "Makeup": "Makeup: apply the makeup described, adapted to the person's face and skin tone.",
    "Nail art": "Nails: apply the nail design described to any visible nails.",
    "Beard & grooming": "Beard and grooming: change the facial hair to match the style described, adapted to the person's jawline and hair colour.",
    "Overall beauty look": "Overall look: apply the hair and grooming described as one cohesive look.",
}

# What to keep when an area is NOT selected, so unselected areas stay untouched.
KEEP = {
    "Hairstyle": "the person's haircut, length and styling",
    "Hair colour": "the person's natural hair colour",
    "Makeup": "the person's makeup (or lack of it)",
    "Nail art": "the person's nails",
    "Beard & grooming": "the person's facial hair",
}

PRESERVE = ("Preserve the person's identity, facial features, face shape, skin tone, expression, age appearance, "
            "pose, camera angle, clothing and background as closely as possible.")

MAX_AREAS = 4


def parse_areas(raw: str) -> List[str]:
    """Parse a comma-separated list of categories, validated and de-duplicated, in a stable order."""
    seen: List[str] = []
    for part in (raw or "").split(","):
        name = part.strip()
        if not name:
            continue
        if name not in settings.CATEGORIES:
            raise HTTPException(400, f"Unsupported beauty category: {name[:40]}.")
        if name not in seen:
            seen.append(name)
    if not seen:
        raise HTTPException(400, "Choose at least one area to change.")
    if "Overall beauty look" in seen and len(seen) > 1:
        seen.remove("Overall beauty look")
    if len(seen) > MAX_AREAS:
        raise HTTPException(400, f"Choose up to {MAX_AREAS} areas to change.")
    return seen


def build_prompt(areas: List[str], has_reference: bool, catalogue_style: Optional[Dict],
                 style: str = "", notes: str = "") -> str:
    wording = WITH_REFERENCE if has_reference else TEXT_ONLY
    changes = " ".join(wording[a] for a in areas)
    keep = [KEEP[a] for a in KEEP if a not in areas and "Overall beauty look" not in areas]

    if has_reference:
        prompt = (
            "You are editing two input images. IMAGE 1 is the target photo of the person and must remain the base image. "
            "IMAGE 2 is a style reference. Change only these areas on the person in IMAGE 1: " + changes + " "
            "Use IMAGE 2 as a visual reference for style only; do not copy the reference person's identity, face, body, pose or background. "
        )
    else:
        prompt = (
            "You are editing a photo of a person. Keep it as the base image and change only these areas: " + changes + " "
            f"The style is {catalogue_style['name']}: {catalogue_style['description']}. "
        )
    if keep:
        prompt += "Keep unchanged: " + "; ".join(keep) + ". "
    prompt += PRESERVE
    if style.strip() and not (catalogue_style and style.strip() == catalogue_style["name"]):
        prompt += f" Additional style description: {style.strip()[:300]}."
    if notes.strip():
        prompt += f" User notes: {notes.strip()[:500]}."
    return prompt
