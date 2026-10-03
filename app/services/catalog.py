"""The style template catalogue, stored in the database.

Seed templates (catalog_seed.py) are inserted on start-up when missing. Admins
can edit, publish, archive and add templates; every edit bumps the version, and
generated results keep the template ID and version they used.

Reads go through a small in-process cache that is cleared on every admin write.
"""
import json
import threading
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.db.models import StyleTemplateModel
from app.db.session import SessionLocal
from app.services.catalog_seed import seed_templates

CATEGORIES = ["Hairstyle", "Hair colour", "Makeup", "Beard & grooming", "Nail art", "Overall beauty look"]
GROUPS = ("women", "men", "all")
STATUSES = ("draft", "published", "archived")
# Columns of style_templates; everything else is stored in data_json.
COLUMNS = ("id", "category", "group", "name", "status", "version", "featured", "sort_order")

_lock = threading.Lock()
_cache: Optional[List[Dict]] = None


def _to_dict(row: StyleTemplateModel) -> Dict:
    data = json.loads(row.data_json or "{}")
    data.update({
        "id": row.id, "category": row.category, "group": row.catalog_group, "name": row.name,
        "status": row.status, "version": row.version, "featured": bool(row.featured), "sort_order": row.sort_order,
    })
    data.setdefault("images", {})
    data["image"] = data["images"].get("front")
    data["audience"] = row.catalog_group  # older clients
    data["tags"] = derived_tags(data)
    return data


def derived_tags(t: Dict) -> List[str]:
    """Searchable tags: the admin's own tags plus the template's filter values."""
    tags = list(t.get("extra_tags") or []) + list(t.get("features") or [])
    for key in ("finish", "subcategory", "technique"):
        if t.get(key):
            tags.append(t[key])
    for key in ("families", "lengths", "occasions", "attributes"):
        tags += t.get(key) or []
    if t.get("maintenance"):
        tags.append(f"{t['maintenance']} maintenance")
    seen, out = set(), []
    for tag in tags:
        tag = str(tag).strip().lower()
        if tag and tag not in seen:
            seen.add(tag)
            out.append(tag)
    return out


def row_from_dict(t: Dict, row: Optional[StyleTemplateModel] = None) -> StyleTemplateModel:
    row = row or StyleTemplateModel(id=t["id"])
    row.category = t["category"]
    row.catalog_group = t["group"]
    row.name = t["name"]
    row.status = t.get("status", "draft")
    row.version = int(t.get("version", 1))
    row.featured = 1 if t.get("featured") else 0
    row.sort_order = int(t.get("sort_order", 1000))
    data = {k: v for k, v in t.items() if k not in COLUMNS and k not in ("image", "audience", "tags")}
    row.data_json = json.dumps(data)
    return row


def sync_seed(db: Session) -> int:
    """Insert seed templates whose ID is not in the database yet. Never overwrites existing rows."""
    existing = {i for (i,) in db.query(StyleTemplateModel.id).all()}
    added = 0
    for t in seed_templates():
        if t["id"] not in existing:
            db.add(row_from_dict(t))
            added += 1
    if added:
        db.commit()
    invalidate()
    return added


def invalidate():
    global _cache
    with _lock:
        _cache = None


def all_templates(include_unpublished: bool = False) -> List[Dict]:
    global _cache
    with _lock:
        if _cache is None:
            db = SessionLocal()
            try:
                rows = db.query(StyleTemplateModel).order_by(StyleTemplateModel.sort_order, StyleTemplateModel.name).all()
                _cache = [_to_dict(r) for r in rows]
            finally:
                db.close()
        items = list(_cache)
    return items if include_unpublished else [t for t in items if t["status"] == "published"]


def published(category: Optional[str] = None, group: Optional[str] = None) -> List[Dict]:
    items = all_templates()
    if category:
        items = [t for t in items if t["category"] == category]
    if group in ("women", "men"):
        items = [t for t in items if t["group"] in (group, "all")]
    return items


def get(template_id: str, include_unpublished: bool = False) -> Optional[Dict]:
    for t in all_templates(include_unpublished):
        if t["id"] == template_id:
            return t
    return None


def find_by_name(name: str, categories: Optional[List[str]] = None) -> Optional[Dict]:
    """Older clients send a style name instead of an ID. Names are unique within a category and group."""
    name = (name or "").strip().lower()
    for t in published():
        if t["name"].lower() == name and t["category"] != "Overall beauty look" and (
                not categories or t["category"] in categories):
            return t
    return None


CATALOG_IMAGE_PREFIX = "/api/v1/catalog-images/"


def image_path(url: Optional[str]) -> Optional[str]:
    """Local file for a template's reference image URL, or None."""
    import os
    if not url:
        return None
    if url.startswith(CATALOG_IMAGE_PREFIX):
        path = os.path.join("storage", "catalog", os.path.basename(url))
    elif "/" not in url and url.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        path = url  # seed images served from the app root
    else:
        return None
    return path if os.path.isfile(path) else None


def attach_image(db: Session, template_id: str, view: str, raw: bytes) -> Dict:
    """Validate and store a reference photo for a template view (front, side or back); bumps the version."""
    import os
    import secrets
    from app.services.catalog_seed import _slug
    from app.services.image_processor import process_image
    row = db.query(StyleTemplateModel).filter(StyleTemplateModel.id == template_id).first()
    if not row:
        raise KeyError(template_id)
    data, _mime, ext, _size = process_image(raw, "The reference photo")
    name = f"{_slug(template_id)}-{view}-{secrets.token_hex(4)}.{ext}"
    os.makedirs(os.path.join("storage", "catalog"), exist_ok=True)
    with open(os.path.join("storage", "catalog", name), "wb") as f:
        f.write(data)
    invalidate()
    t = get(template_id, include_unpublished=True)
    t["images"] = dict(t.get("images") or {}, **{view: CATALOG_IMAGE_PREFIX + name})
    t["version"] += 1
    row_from_dict(t, row)
    db.commit()
    invalidate()
    return t


def public_view(t: Dict) -> Dict:
    """What browsers get: no internal fields such as status, except the version kept on results."""
    keys = ("id", "category", "group", "audience", "name", "description", "image", "images", "tags", "face_shapes",
            "lengths", "textures", "finish", "maintenance", "occasions", "features", "hex", "undertones", "technique",
            "families", "subcategory", "intensity", "attributes", "parts", "featured", "version")
    return {k: t[k] for k in keys if k in t}
