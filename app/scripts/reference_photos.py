"""Reference photos for the style catalogue: prompts, generation and import.

    python -m app.scripts.reference_photos prompts                 # write docs/reference-photos.md and .csv
    python -m app.scripts.reference_photos generate DIR [--views front] [--ids a,b] [--limit N] [--yes]
                                                                   # create photos with OpenAI (costs money)
    python -m app.scripts.reference_photos import DIR              # attach DIR/<template_id>-<view>.jpg files

Prompts are built from the catalogue in the database, so admin edits are included.
Photos you make elsewhere (another image tool, a photographer) work too: name them
<template_id>-front.jpg, -side.jpg or -back.jpg and run `import`.
Only use photos you have the rights to use; they're shown with a "Reference" label.
"""
import argparse
import base64
import csv
import os
import sys
import time
from typing import Dict, List

from app.core.config import settings
from app.db.session import SessionLocal
from app.services import catalog

PORTRAIT = "1024x1536"
SQUARE = "1024x1024"

COMMON = ("Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. "
          "Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. "
          "No text, no watermark, no logo.")
FRAMING = ("Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. "
           "The whole head and all of the hair are visible, with clear space above the top of the head. "
           "Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face.")
VIEW_TEXT = {
    "front": "",
    "side": "Same person and hairstyle in a side profile view (facing left, 90 degrees), whole head and hair visible.",
    "back": "Same person and hairstyle seen from behind, showing the back and sides of the hairstyle, whole head visible.",
}

# Models are rotated so the catalogue shows a range of skin tones and hair textures.
WOMEN = {
    "straight": ["a woman in her late 20s with light skin, warm undertones and natural brown hair",
                 "a woman in her 30s with medium olive skin and dark brown hair",
                 "a woman in her 20s with tan skin and black hair",
                 "a woman in her 40s with fair skin, cool undertones and light brown hair",
                 "a woman in her 30s with light-medium skin, freckles and auburn-brown hair",
                 "a woman in her 30s with deep brown skin and black hair"],
    "curly": ["a woman in her 20s with deep brown skin and naturally coily black hair",
              "a woman in her 30s with medium brown skin and naturally curly dark hair"],
}
MEN = {
    "straight": ["a man in his late 20s with light skin and natural brown hair",
                 "a man in his 30s with medium olive skin and dark brown hair",
                 "a man in his 20s with tan skin and black hair",
                 "a man in his 40s with fair skin and light brown hair, a few grey strands",
                 "a man in his 30s with light-medium skin and dark blond hair",
                 "a man in his 30s with deep brown skin and black hair"],
    "curly": ["a man in his 20s with deep brown skin and naturally coily black hair",
              "a man in his 30s with medium brown skin and naturally curly dark hair"],
}
COLOUR_MODEL = {"women": WOMEN["straight"][3], "men": MEN["straight"][0]}  # light base hair shows colours clearly
COLOUR_BASE = {"women": "long, soft layered hair falling past the shoulders",
               "men": "a short textured crop with 4-5 cm on top and tapered sides"}
EVERYONE_MAKEUP = {"makeup_no_makeup_makeup", "makeup_minimal_makeup", "makeup_matte", "makeup_satin"}


def _model(pool: Dict[str, List[str]], t: Dict, i: int) -> str:
    textures = set(t.get("textures") or [])
    if textures and "straight" not in textures:
        return pool["curly"][i % 2]
    # Curl-specific styles use models with natural curls; otherwise the style prompt sets the texture.
    return pool["straight"][i % len(pool["straight"])]


def build(t: Dict, i: int, view: str = "front") -> Dict:
    """Prompt, size and file name for one template view."""
    cat, group = t["category"], t["group"]
    size = PORTRAIT
    if cat == "Hairstyle":
        subject = _model(WOMEN if group == "women" else MEN, t, i)
        body = f"Subject: {subject}. Hairstyle: {t['prompt']}, in the person's natural hair colour. {FRAMING}"
    elif cat == "Hair colour":
        g = "men" if group == "men" else "women"
        body = (f"Subject: {COLOUR_MODEL[g]}. Hair: {COLOUR_BASE[g]}, coloured {t['prompt']}. "
                f"The colour must be clearly visible in soft daylight. {FRAMING}")
    elif cat == "Makeup":
        pool = MEN if t["id"] in EVERYONE_MAKEUP and i % 2 else WOMEN
        subject = _model(pool, {"textures": ["straight"]}, i)
        body = (f"Subject: {subject}. Makeup: {t['prompt']}. Hair pulled back off the face. "
                f"Close head-and-shoulders framing so the makeup detail is clear. {FRAMING}")
    elif cat == "Beard & grooming":
        subject = _model(MEN, {"textures": ["straight"]}, i)
        body = (f"Subject: {subject}. Facial hair: {t['prompt']}. Hair: a short, neat classic taper. {FRAMING}")
    elif cat == "Nail art":
        size = SQUARE
        body = ("Close-up of one relaxed hand resting on a plain warm light-grey surface, fingers slightly apart, "
                f"all nails clearly visible and in sharp focus: {t['prompt']}. Medium-length nails, natural skin.")
    else:  # complete look: combine its parts
        parts = [catalog.get(p, include_unpublished=True) for p in t.get("parts") or []]
        subject = _model(WOMEN if group == "women" else MEN, {"textures": ["straight"]}, i)
        details = " ".join(f"{p['category']}: {p['prompt']}." for p in parts if p)
        body = f"Subject: {subject}. {details} {FRAMING}"
    prompt = " ".join(x for x in (body, VIEW_TEXT[view], COMMON) if x)
    return {"id": t["id"], "name": t["name"], "category": cat, "group": group, "view": view, "size": size,
            "file": f"{t['id']}-{view}.jpg", "prompt": prompt}


def views_for(t: Dict) -> List[str]:
    return ["front", "side", "back"] if t["category"] == "Hairstyle" else ["front"]


def all_rows(views=None) -> List[Dict]:
    rows = []
    items = [t for t in catalog.all_templates(include_unpublished=True) if t["status"] != "archived"]
    counters: Dict[str, int] = {}
    for t in items:
        key = t["category"] + t["group"]
        i = counters.get(key, 0)
        counters[key] = i + 1
        for view in views_for(t):
            if views and view not in views:
                continue
            rows.append(build(t, i, view))
    return rows


SIZE_GUIDE = """## Photo size and format

| What | Generate at | Aspect | Notes |
|---|---|---|---|
| Hairstyles, hair colours, makeup, beards, looks | **1024 × 1536 px** | 2:3 portrait | Matches the image model's portrait size and the try-on output. |
| Nail art | **1024 × 1024 px** | 1:1 square | Hand close-up. |

- **Format:** JPG, quality 85–90, ideally under 1 MB each. The app accepts JPG, PNG or WEBP up to 12 MB and at least 256 px; it stores at most 1536 px on the long side.
- **Framing:** keep the face in the middle third of the frame, with the whole head and hair visible and some space above it. Cards in the app crop the photo to fill wide (about 4:3) and tall (about 4:5) frames, so anything near the edges may be hidden.
- **Consistency:** same background (plain warm light grey), soft front light, black top and no jewellery in every photo, so styles compare fairly and nothing but the style draws attention.
- **Views:** every style needs a **front** photo. For hairstyles, **side** and **back** photos are optional but help a lot for updos, braids, ponytails, buns, mullets and V/U-cut layers.
- **File names:** `<template id>-front.jpg`, `-side.jpg` or `-back.jpg`, then run `python -m app.scripts.reference_photos import <folder>`, or upload one at a time in **/admin**.
- **Rights:** use only photos you created or have permission to use. The app labels them “Reference” so customers don't mistake them for their own results.
"""


def write_prompts(md_path="docs/reference-photos.md", csv_path="docs/reference-photos.csv"):
    rows = all_rows()
    os.makedirs(os.path.dirname(md_path), exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "name", "category", "group", "view", "size", "file", "prompt"])
        w.writeheader()
        w.writerows(rows)
    fronts = [r for r in rows if r["view"] == "front"]
    lines = ["# Reference photo prompts", "",
             "Prompts for creating a reference photo for every catalogue style, generated from the catalogue by "
             "`python -m app.scripts.reference_photos prompts`. Paste a prompt into your image tool (or run the "
             "`generate` command), save the photo with the file name shown, then import it.",
             f"\n{len(fronts)} styles; {len(rows)} photos including the optional hairstyle side and back views. "
             "The same prompts are in `reference-photos.csv` for batch tools.", "", SIZE_GUIDE]
    side = VIEW_TEXT["side"]
    back = VIEW_TEXT["back"]
    lines += ["## Side and back views (hairstyles, optional)", "",
              "Use the style's front prompt and add one of these sentences:", "",
              f"- **Side** (`<id>-side.jpg`): {side}", f"- **Back** (`<id>-back.jpg`): {back}", "",
              "Generate the side and back views right after the front one, in the same session or with the front "
              "photo as a reference, so it's the same person.", ""]
    for cat in catalog.CATEGORIES:
        group_rows = [r for r in fronts if r["category"] == cat]
        if not group_rows:
            continue
        lines.append(f"## {cat}\n")
        for g in ("women", "men", "all"):
            sub = [r for r in group_rows if r["group"] == g]
            if not sub:
                continue
            label = {"women": "Women's", "men": "Men's", "all": "For everyone"}[g]
            lines.append(f"### {label}\n")
            for r in sub:
                lines.append(f"**{r['name']}** · `{r['file']}` · {r['size']}\n")
                lines.append(f"> {r['prompt']}\n")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Wrote {md_path} and {csv_path}: {len(fronts)} styles, {len(rows)} prompts.")


def generate(folder: str, views, ids, limit: int, yes: bool):
    from openai import OpenAI
    rows = [r for r in all_rows(views) if not ids or r["id"] in ids]
    os.makedirs(folder, exist_ok=True)
    rows = [r for r in rows if not os.path.exists(os.path.join(folder, r["file"]))][: limit or None]
    if not rows:
        print("Nothing to generate: every photo already exists in", folder)
        return
    print(f"About to generate {len(rows)} photos with {settings.OPENAI_IMAGE_MODEL} (quality high). "
          "Each image is billed by OpenAI.")
    if not yes and input("Continue? [y/N] ").strip().lower() != "y":
        return
    client = OpenAI(api_key=settings.OPENAI_API_KEY, timeout=180, max_retries=1)
    for n, r in enumerate(rows, 1):
        started = time.time()
        try:
            res = client.images.generate(model=settings.OPENAI_IMAGE_MODEL, prompt=r["prompt"], size=r["size"],
                                         quality="high", output_format="jpeg", n=1)
            with open(os.path.join(folder, r["file"]), "wb") as f:
                f.write(base64.b64decode(res.data[0].b64_json))
            print(f"[{n}/{len(rows)}] {r['file']} ({time.time() - started:.0f}s)")
        except Exception as exc:  # keep going; rerun to retry the missing ones
            print(f"[{n}/{len(rows)}] FAILED {r['file']}: {str(exc)[:200]}")
    print("Check the photos, delete any that don't match the style, then run: "
          f"python -m app.scripts.reference_photos import {folder}")


def import_folder(folder: str):
    db = SessionLocal()
    done = skipped = 0
    try:
        for name in sorted(os.listdir(folder)):
            stem, ext = os.path.splitext(name)
            if ext.lower() not in (".jpg", ".jpeg", ".png", ".webp") or "-" not in stem:
                continue
            template_id, view = stem.rsplit("-", 1)
            if view not in ("front", "side", "back") or not catalog.get(template_id, include_unpublished=True):
                print("Skipped (unknown template or view):", name)
                skipped += 1
                continue
            with open(os.path.join(folder, name), "rb") as f:
                raw = f.read()
            try:
                catalog.attach_image(db, template_id, view, raw)
                done += 1
                print("Attached", name)
            except Exception as exc:
                print("Skipped", name + ":", getattr(exc, "detail", exc))
                skipped += 1
    finally:
        db.close()
    print(f"Done: {done} attached, {skipped} skipped. Restart is not needed; the app shows them right away.")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("prompts", help="write docs/reference-photos.md and .csv")
    g = sub.add_parser("generate", help="create photos with OpenAI")
    g.add_argument("folder")
    g.add_argument("--views", default="front", help="comma-separated: front,side,back (default front)")
    g.add_argument("--ids", default="", help="comma-separated template IDs (default all)")
    g.add_argument("--limit", type=int, default=0, help="at most this many photos")
    g.add_argument("--yes", action="store_true", help="don't ask for confirmation")
    i = sub.add_parser("import", help="attach <template_id>-<view>.jpg files to the catalogue")
    i.add_argument("folder")
    args = p.parse_args()
    if args.cmd == "prompts":
        write_prompts()
    elif args.cmd == "generate":
        generate(args.folder, [v for v in args.views.split(",") if v], {x for x in args.ids.split(",") if x},
                 args.limit, args.yes)
    else:
        import_folder(args.folder)
    return 0


if __name__ == "__main__":
    sys.exit(main())
