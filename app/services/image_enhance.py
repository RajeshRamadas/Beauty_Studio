"""Gentle, automatic corrections for the user's photo before the AI sees it.

Only global, deterministic adjustments that don't invent detail, so identity and
skin tone are kept (no AI upscaling or "face restoration", which change faces):
- exposure: brighten a dark photo or tone down an over-bright one (gamma curve);
- contrast: stretch a flat, washed-out histogram slightly;
- colour cast: reduce a strong colour cast (e.g. yellow indoor light), at half strength,
  so undertone estimates aren't thrown off by the lighting;
- sharpness: a light unsharp mask on slightly soft photos.
Each step runs only when the photo needs it, and the steps applied are reported.
"""
import io
import math
from typing import List, Tuple

from PIL import Image, ImageFilter, ImageOps, ImageStat

from app.core.config import settings

# Thresholds calibrated on the sample portraits (normal ones are left untouched).
TARGET_BRIGHTNESS = 120
DARK_BELOW = 80          # mean brightness of the face area (centre of the frame)
BRIGHT_ABOVE = 190
FLAT_STDDEV_BELOW = 42
# Portraits are naturally warm (skin, hair): their gray-world gains are about R 0.89, G 1.0, B 1.15.
# Only a clear departure from that is treated as a colour cast from the light.
PORTRAIT_GAINS = (0.89, 1.0, 1.15)
CAST_ABOVE = 0.15
CAST_STRENGTH = 0.5      # correct half of the cast
MAX_GAIN = 0.15
SOFT_EDGES_BELOW = 450   # edge variance (256 px thumbnail) under this gets light sharpening

LABELS = {
    "brightened": "Brightened",
    "darkened": "Toned down bright light",
    "contrast": "Improved contrast",
    "colour_balance": "Balanced the colour of the light",
    "sharpened": "Sharpened slightly",
}


def _stats(img: Image.Image):
    small = img.convert("RGB")
    small.thumbnail((256, 256))
    grey = small.convert("L")
    return small, grey, ImageStat.Stat(grey)


def _centre_brightness(grey: Image.Image) -> float:
    w, h = grey.size
    return ImageStat.Stat(grey.crop((int(w * .25), int(h * .15), int(w * .75), int(h * .65)))).mean[0]


def _gamma(img: Image.Image, mean: float) -> Image.Image:
    g = math.log(TARGET_BRIGHTNESS / 255) / math.log(max(1.0, min(254.0, mean)) / 255)
    g = max(0.55, min(1.6, g))
    lut = [round(255 * (i / 255) ** g) for i in range(256)]
    return img.point(lut * 3)


def enhance(img: Image.Image) -> Tuple[Image.Image, List[str]]:
    """Returns the corrected RGB image and the codes of the corrections applied."""
    img = img.convert("RGB")
    applied: List[str] = []

    _small, grey, st = _stats(img)
    mean, std = _centre_brightness(grey), st.stddev[0]
    if mean < DARK_BELOW:
        img = _gamma(img, mean)
        applied.append("brightened")
    elif mean > BRIGHT_ABOVE:
        img = _gamma(img, mean)
        applied.append("darkened")

    if std < FLAT_STDDEV_BELOW:
        img = ImageOps.autocontrast(img, cutoff=0.5, preserve_tone=True)
        applied.append("contrast")

    small, _grey, _st = _stats(img)
    r, g, b = ImageStat.Stat(small).mean
    grey_mean = (r + g + b) / 3
    gains = [grey_mean / max(c, 1) for c in (r, g, b)]
    if max(abs(x - p) for x, p in zip(gains, PORTRAIT_GAINS)) > CAST_ABOVE:
        # Move each channel part of the way towards a normally lit portrait.
        gains = [1 + max(-MAX_GAIN, min(MAX_GAIN, (x / p - 1) * CAST_STRENGTH)) for x, p in zip(gains, PORTRAIT_GAINS)]
        bands = [band.point(lambda v, k=k: min(255, round(v * k))) for band, k in zip(img.split(), gains)]
        img = Image.merge("RGB", bands)
        applied.append("colour_balance")

    _small, grey, _st = _stats(img)
    edges = grey.filter(ImageFilter.FIND_EDGES)
    w, h = edges.size
    if w > 8 and h > 8 and ImageStat.Stat(edges.crop((2, 2, w - 2, h - 2))).var[0] < SOFT_EDGES_BELOW:
        img = img.filter(ImageFilter.UnsharpMask(radius=1.2, percent=45, threshold=3))
        applied.append("sharpened")
    return img, applied


def enhance_bytes(data: bytes) -> Tuple[bytes, List[str]]:
    """Enhance an already validated JPEG/PNG from process_image. PNGs with transparency are left alone."""
    if not settings.PHOTO_ENHANCE:
        return data, []
    img = Image.open(io.BytesIO(data))
    if img.mode in ("RGBA", "LA", "P"):
        return data, []
    out_img, applied = enhance(img)
    if not applied:
        return data, []
    out = io.BytesIO()
    out_img.save(out, format="JPEG", quality=92)
    return out.getvalue(), applied


def describe(codes: List[str]) -> List[str]:
    return [LABELS[c] for c in codes if c in LABELS]
