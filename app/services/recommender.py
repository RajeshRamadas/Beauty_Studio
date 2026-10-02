"""Ranks catalogue templates against a face analysis and the user's preferences.

The method (requirements 8, "Recommendation flow"):
1. Take the published templates of the category, in the chosen catalogue group.
2. Keep only those that match every preference the user selected (length, maintenance, occasion).
3. Score each template from the analysis, counting only estimates the analysis is confident about:
     face shape in the template's face-shape tags    +3 high confidence, +2 medium, +1 low, 0 uncertain
     visible hair texture in the template's textures +2
     template keeps the visible hair length          +1
     undertone in a hair colour's or makeup's tags   +3 high, +2 medium, +1 low, 0 uncertain
     preferred occasion (makeup)                     +2
     featured template                               +0.25 (tie-break)
4. Sort by score, then catalogue order. Templates scoring 2 or more are "Suggested", the rest
   "Another option"; when the user set preferences, matches say so.
5. Each result carries short reasons built from what matched, never a judgement of other styles.
6. Nothing is hidden: the full catalogue stays available to browse.
"""
from typing import Dict, List, Optional

from app.services import catalog

CONFIDENCE_WEIGHT = {"high": 3, "medium": 2, "low": 1}
LENGTH_ORDER = ["very short", "short", "medium", "long"]
SUGGESTED_MIN_SCORE = 2


def _estimate(analysis: Dict, key: str) -> (Optional[str], int):
    """The value of an estimate and its weight; 0 when missing or uncertain."""
    est = (analysis or {}).get(key) or {}
    value = str(est.get("value") or "").lower()
    if not value or value in ("uncertain", "not visible", "unknown"):
        return None, 0
    return value, CONFIDENCE_WEIGHT.get(str(est.get("confidence") or "").lower(), 0)


def _hair(analysis: Dict, key: str) -> Optional[str]:
    v = str(((analysis or {}).get("hair") or {}).get(key) or "").lower()
    return None if not v or v in ("not visible", "unknown", "uncertain") else v


def _passes(t: Dict, prefs: Dict) -> bool:
    if prefs.get("length") and t.get("lengths") and prefs["length"] not in t["lengths"]:
        return False
    if prefs.get("maintenance") and t.get("maintenance") and prefs["maintenance"] != t["maintenance"]:
        return False
    if prefs.get("occasion") and t.get("occasions") and prefs["occasion"] not in t["occasions"]:
        return False
    return True


def _score(t: Dict, analysis: Dict, prefs: Dict):
    score, reasons = 0.0, []
    shape, shape_w = _estimate(analysis, "face_shape")
    if shape and shape_w and shape in (t.get("face_shapes") or []):
        score += shape_w
        reasons.append(f"Often chosen for {shape} face shapes" + (" (low-confidence estimate)" if shape_w == 1 else ""))
    texture = _hair(analysis, "texture")
    if texture and texture in (t.get("textures") or []):
        score += 2
        reasons.append(f"Works with {texture} hair")
    length = _hair(analysis, "visible_length")
    if length and length in (t.get("lengths") or []):
        score += 1
        reasons.append("Close to your current length")
    tone, tone_w = _estimate(analysis, "undertone")
    if tone and tone_w and tone in (t.get("undertones") or []):
        score += tone_w
        reasons.append(f"Often chosen for {tone} undertones" + (" (low-confidence estimate)" if tone_w == 1 else ""))
    if prefs.get("occasion") and prefs["occasion"] in (t.get("occasions") or []) and t["category"] == "Makeup":
        score += 2
    chosen = [f"{v} {k}" if k == "maintenance" else v for k, v in prefs.items() if v]
    if chosen:
        reasons.append("Matches your selected preference: " + ", ".join(chosen))
    if t.get("featured"):
        score += 0.25
    return score, reasons


def rank(category: str, group: str, analysis: Optional[Dict] = None, prefs: Optional[Dict] = None,
         limit: int = 6) -> List[Dict]:
    prefs = {k: v for k, v in (prefs or {}).items() if v}
    candidates = [t for t in catalog.published(category, group) if _passes(t, prefs)]
    scored = []
    for order, t in enumerate(candidates):
        score, reasons = _score(t, analysis or {}, prefs)
        scored.append((-score, order, t, reasons, score))
    scored.sort(key=lambda x: (x[0], x[1]))
    out = []
    for _neg, _order, t, reasons, score in scored[:limit]:
        item = catalog.public_view(t)
        item["label"] = "Suggested" if score >= SUGGESTED_MIN_SCORE else (
            "Matches your selected preference" if prefs else "Another option")
        item["reasons"] = reasons[:4]
        item["score"] = round(score, 2)
        out.append(item)
    return out


def colour_note(analysis: Optional[Dict]) -> Optional[str]:
    tone, weight = _estimate(analysis or {}, "undertone")
    if not tone or weight < 2:
        return ("We couldn't estimate your undertone reliably from this photo, so no colour is singled out. "
                "Browse all colours and pick what you like.")
    return None


def recommend(group: str, analysis: Optional[Dict] = None, prefs: Optional[Dict] = None) -> Dict:
    """Catalogue suggestions for every category that fits the chosen group."""
    group = group if group in ("women", "men", "all") else "all"
    note = colour_note(analysis)
    result = {
        "method": "catalogue tags matched to the analysis and your preferences",
        "hairstyles": rank("Hairstyle", group, analysis, prefs),
        "hair_colours": [] if note else [c for c in rank("Hair colour", group, analysis, {}, limit=4)
                                         if c["label"] == "Suggested"],
        "hair_colour_note": note,
        "makeup": rank("Makeup", group, analysis, {"occasion": (prefs or {}).get("occasion")}, limit=4),
        "beard": rank("Beard & grooming", group, analysis, {k: v for k, v in (prefs or {}).items()
                                                             if k in ("maintenance", "occasion")}, limit=3)
        if group in ("men", "all") else [],
    }
    return result
