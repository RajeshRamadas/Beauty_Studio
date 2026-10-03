"""Builds the image-edit prompt for a look.

A look is a list of specs, one per area to change (requirements 9 and 16):
  {"area": "Hairstyle", "source": "template", "template": {...}}   a catalogue template
  {"area": "Makeup", "source": "custom", "template": {"name", "prompt"}}  a personalised style in words
  {"area": "Hair colour", "source": "reference"}                     taken from the reference photo (IMAGE 2)
plus an intensity (subtle | medium | bold) and, for hair colour, whether to keep natural roots.
Prompt text comes from the server's catalogue, never from the client, except free-form notes.
"""
from typing import Dict, List, Optional

from fastapi import HTTPException

from app.core.config import settings

AREA_LABEL = {
    "Hairstyle": "Hair style",
    "Hair colour": "Hair colour",
    "Makeup": "Makeup",
    "Nail art": "Nails",
    "Beard & grooming": "Beard and grooming",
    "Overall beauty look": "Overall look",
}

# Wording when the area comes from the reference image (IMAGE 2).
WITH_REFERENCE = {
    "Hairstyle": "apply the haircut, length, shape and styling from IMAGE 2",
    "Hair colour": "apply the hair colour, tone and any highlights from IMAGE 2",
    "Makeup": "apply the makeup look, colours, finish and placement from IMAGE 2",
    "Nail art": "apply the nail design, colours, pattern and finish from IMAGE 2 to any visible nails",
    "Beard & grooming": "apply the beard, moustache and facial-hair shape from IMAGE 2",
    "Overall beauty look": "use IMAGE 2 as inspiration for the complete hair, makeup and grooming styling",
}

# How each area must be applied, whatever its source (requirements 9).
RULES = {
    "Hairstyle": ("Adapt it to the person's head orientation, perspective, visible hairline, head shape and hair "
                  "texture; where the head or hair is hidden, keep the change conservative."),
    "Hair colour": ("Colour only the visible hair; keep the hairstyle and hair texture; do not recolour skin, "
                    "eyebrows, facial hair or the background."),
    "Makeup": ("Apply it only to the visible facial regions it covers; preserve the face structure, expression, "
               "skin texture and skin tone; apply only these makeup elements."),
    "Nail art": "Apply it only to visible nails.",
    "Beard & grooming": "Adapt it to the person's jawline, growth pattern and hair colour.",
    "Overall beauty look": "",
}

# What to keep when an area is NOT selected, so unselected areas stay untouched.
KEEP = {
    "Hairstyle": "the person's haircut, length and styling",
    "Hair colour": "the person's natural hair colour",
    "Makeup": "the person's makeup (or lack of it)",
    "Nail art": "the person's nails",
    "Beard & grooming": "the person's facial hair",
}

INTENSITY = {
    "subtle": "Keep the colour and makeup changes subtle and close to natural.",
    "medium": "",
    "bold": "Make the colour and makeup changes bold and clearly visible, still realistic.",
}

PRESERVE = ("Preserve the person's identity, facial features, face shape, skin tone, expression, age appearance, "
            "pose, camera angle, clothing and background as closely as possible.")

MAX_AREAS = 4


def parse_areas(raw: str, required: bool = True) -> List[str]:
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
    if not seen and required:
        raise HTTPException(400, "Choose at least one area to change.")
    if "Overall beauty look" in seen and len(seen) > 1:
        seen.remove("Overall beauty look")
    if len(seen) > MAX_AREAS:
        raise HTTPException(400, f"Choose up to {MAX_AREAS} areas to change.")
    return seen


def _line(spec: Dict, intensity: str, keep_roots: bool) -> str:
    area = spec["area"]
    if spec["source"] == "reference":
        text = WITH_REFERENCE[area]
    else:
        t = spec["template"]
        text = f"{t['name']}: {t['prompt']}"
        if spec.get("uses_reference"):
            text += " (IMAGE 2 shows this style)"
    line = f"{AREA_LABEL[area]}: {text}. {RULES[area]}".strip()
    if area == "Hair colour" and keep_roots:
        line += " Keep the natural colour at the roots (about 1-2 cm) for a grown-in, lived-in effect."
    return line


def compose_prompt(specs: List[Dict], intensity: str = "medium", keep_roots: bool = False, notes: str = "") -> str:
    areas = [s["area"] for s in specs]
    from_image = [s for s in specs if s["source"] == "reference" or s.get("uses_reference")]
    changes = " ".join(_line(s, intensity, keep_roots) for s in specs)
    keep = [KEEP[a] for a in KEEP if a not in areas and "Overall beauty look" not in areas]

    if from_image:
        ref_areas = ", ".join(AREA_LABEL[s["area"]].lower() for s in from_image)
        prompt = (
            "You are editing two input images. IMAGE 1 is the target photo of the person and must remain the base image. "
            f"IMAGE 2 is a style reference, to be used only for: {ref_areas}. "
            "Change only these areas on the person in IMAGE 1: " + changes + " "
            "Do not copy the reference person's identity, face, body, pose or background. "
        )
    else:
        prompt = ("You are editing a photo of a person. Keep it as the base image and change only these areas: "
                  + changes + " ")
    if keep:
        prompt += "Keep unchanged: " + "; ".join(keep) + ". "
    if INTENSITY.get(intensity):
        prompt += INTENSITY[intensity] + " "
    prompt += PRESERVE
    if notes.strip():
        prompt += f" User notes: {notes.strip()[:500]}."
    return prompt


def build_prompt(areas: List[str], has_reference: bool, catalogue_style: Optional[Dict],
                 style: str = "", notes: str = "") -> str:
    """One style for all areas: from the reference image, or from a catalogue or personalised style."""
    if has_reference:
        specs = [{"area": a, "source": "reference"} for a in areas]
    else:
        t = dict(catalogue_style)
        t.setdefault("prompt", t.get("description", ""))
        specs = [{"area": a, "source": "template", "template": t} for a in areas]
    prompt = compose_prompt(specs, notes=notes)
    if style.strip() and not (catalogue_style and style.strip() == catalogue_style["name"]):
        prompt += f" Additional style description: {style.strip()[:300]}."
    return prompt


def summary(specs: List[Dict], intensity: str = "medium", notes: str = "") -> str:
    """Short description of the requested look for the accuracy check."""
    parts = []
    for s in specs:
        if s["source"] == "reference":
            parts.append(f"{AREA_LABEL[s['area']]} from the reference photo")
        else:
            parts.append(f"{AREA_LABEL[s['area']]}: {s['template']['name']} ({s['template']['prompt']})")
    text = "; ".join(parts) + (f"; intensity {intensity}" if intensity != "medium" else "")
    return text + (f". Notes: {notes.strip()[:300]}" if notes.strip() else "")
