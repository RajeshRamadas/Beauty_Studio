"""Styles the app can try on.

One list drives the Styles screens (via /api/v1/styles), face-analysis
recommendations and generation prompts. A style with an `image` uses that
photo as the try-on reference; a style without one is generated from its
`description`, so add images here (served from the app root) when you have them.

audience: "women", "men" or "all" (shown in both).
"""
from typing import Dict, List, Optional

AUDIENCES = ("women", "men")

STYLES: List[Dict] = [
    # ── Women: hairstyles ──
    {"name": "Glamour Waves", "category": "Hairstyle", "audience": "women", "image": "sample_glamour_waves.jpg",
     "description": "long, glossy, voluminous S-shaped waves with soft face-framing layers"},
    {"name": "Beach Waves", "category": "Hairstyle", "audience": "women", "image": "sample_beach_waves.jpg",
     "description": "loose, tousled, textured beach waves with a relaxed, undone finish"},
    {"name": "Short Bob", "category": "Hairstyle", "audience": "women", "image": "sample_short_bob.jpg",
     "description": "a sleek chin-length bob with blunt ends and a polished finish"},
    {"name": "Braided Updo", "category": "Hairstyle", "audience": "women", "image": "sample_braided_updo.jpg",
     "description": "an elegant braided updo gathered at the back with soft loose tendrils"},
    {"name": "Curtain Bangs", "category": "Hairstyle", "audience": "women", "image": "sample_short_bob.jpg",
     "description": "soft curtain bangs parted in the centre, sweeping to frame the cheekbones"},
    {"name": "Volumetric Curls", "category": "Hairstyle", "audience": "women", "image": "sample_glamour_waves.jpg",
     "description": "big, bouncy, defined curls with lots of volume at the crown"},
    # ── Women: makeup ──
    {"name": "Natural Glow", "category": "Makeup", "audience": "women", "image": "sample_glamour_waves.jpg",
     "description": "fresh, dewy skin, light coverage, soft brows, rosy cheeks and a tinted lip"},
    {"name": "Soft Glam", "category": "Makeup", "audience": "women", "image": "sample_beach_waves.jpg",
     "description": "warm neutral eyeshadow, soft winged liner, defined lashes and a nude-pink lip"},
    {"name": "Smoky Eyes", "category": "Makeup", "audience": "women", "image": "sample_short_bob.jpg",
     "description": "blended charcoal smoky eyes, lined waterline, full lashes and a neutral lip"},
    {"name": "Bridal Velvet", "category": "Makeup", "audience": "women", "image": "sample_braided_updo.jpg",
     "description": "long-wear bridal makeup with soft-matte skin, shimmer lids and a rose lip"},
    {"name": "Bold Lip", "category": "Makeup", "audience": "women", "image": "sample_glamour_waves.jpg",
     "description": "clean skin and minimal eyes with a statement classic red lip"},
    {"name": "Party Bronze", "category": "Makeup", "audience": "women", "image": "sample_beach_waves.jpg",
     "description": "sun-kissed bronzed skin, golden shimmer eyes and a glossy nude lip"},
    # ── Women: nails ──
    {"name": "French Ombre", "category": "Nail art", "audience": "women", "image": "sample_beach_waves.jpg",
     "description": "a soft pink-to-white French ombre manicure"},
    {"name": "Rose Gold Chrome", "category": "Nail art", "audience": "women", "image": "sample_glamour_waves.jpg",
     "description": "mirror-finish rose gold chrome nails"},
    {"name": "Classic Nude", "category": "Nail art", "audience": "women", "image": "sample_short_bob.jpg",
     "description": "glossy classic nude almond nails"},
    {"name": "Marble", "category": "Nail art", "audience": "women", "image": "sample_braided_updo.jpg",
     "description": "white marble nail art with fine grey and gold veins"},
    # ── Women: full looks ──
    {"name": "Red Carpet", "category": "Overall beauty look", "audience": "women", "image": "sample_glamour_waves.jpg",
     "description": "Hollywood glamour waves, sculpted makeup and a classic red lip"},
    {"name": "Evening Gala", "category": "Overall beauty look", "audience": "women", "image": "sample_braided_updo.jpg",
     "description": "an elegant updo with smoky eyes and luminous skin"},
    {"name": "Korean Glass Skin", "category": "Overall beauty look", "audience": "women", "image": "sample_beach_waves.jpg",
     "description": "glass-like dewy skin, straight soft brows, gradient lips and soft waves"},
    {"name": "Bridal Luxe", "category": "Overall beauty look", "audience": "women", "image": "sample_short_bob.jpg",
     "description": "a polished bridal look with soft glam makeup and a refined hairstyle"},

    # ── Men: hairstyles ──
    {"name": "Classic Fade", "category": "Hairstyle", "audience": "men", "image": None,
     "description": "a men's classic taper fade: very short on the sides blending up to 3-4 cm on top, neatly combed"},
    {"name": "Textured Crop", "category": "Hairstyle", "audience": "men", "image": None,
     "description": "a men's textured French crop: short faded sides, choppy textured top with a short straight fringe"},
    {"name": "Quiff", "category": "Hairstyle", "audience": "men", "image": None,
     "description": "a men's modern quiff: short sides, longer top swept up and back with volume at the front"},
    {"name": "Side Part", "category": "Hairstyle", "audience": "men", "image": None,
     "description": "a men's classic side part: tapered sides, longer top combed neatly to one side with a defined part"},
    {"name": "Buzz Cut", "category": "Hairstyle", "audience": "men", "image": None,
     "description": "a men's even buzz cut of about 6 mm all over with a clean hairline"},
    {"name": "Curly Top", "category": "Hairstyle", "audience": "men", "image": None,
     "description": "a men's curly top: tight fade on the sides with natural defined curls on top"},
    {"name": "Long Layers", "category": "Hairstyle", "audience": "men", "image": None,
     "description": "men's shoulder-length layered hair, tucked behind the ears with a natural texture"},
    # ── Men: beard & grooming ──
    {"name": "Full Beard", "category": "Beard & grooming", "audience": "men", "image": None,
     "description": "a full, well-groomed beard about 2-3 cm long with a sharp cheek line and neckline"},
    {"name": "Boxed Beard", "category": "Beard & grooming", "audience": "men", "image": None,
     "description": "a short boxed beard about 1 cm long with crisp edges and a connected moustache"},
    {"name": "Designer Stubble", "category": "Beard & grooming", "audience": "men", "image": None,
     "description": "even designer stubble of a few days' growth with a tidy neckline"},
    {"name": "Clean Shave", "category": "Beard & grooming", "audience": "men", "image": None,
     "description": "a smooth, clean-shaven face with no facial hair"},
    # ── Men: full looks ──
    {"name": "Groom Look", "category": "Overall beauty look", "audience": "men", "image": None,
     "description": "a men's wedding look: neat side-part hair, groomed short beard and a fresh, even complexion"},
    {"name": "Smart Classic", "category": "Overall beauty look", "audience": "men", "image": None,
     "description": "a men's smart classic look: tidy taper cut, clean shave and well-groomed brows"},
]

_BY_NAME = {s["name"]: s for s in STYLES}


def get_style(name: str) -> Optional[Dict]:
    return _BY_NAME.get(name)


def styles_for(audience: Optional[str] = None) -> List[Dict]:
    if audience not in AUDIENCES:
        return list(STYLES)
    return [s for s in STYLES if s["audience"] in (audience, "all")]
