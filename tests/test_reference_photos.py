import io
import os

from PIL import Image

from app.db.session import SessionLocal
from app.services import catalog
from app.scripts import reference_photos as rp


def test_every_style_gets_a_prompt_with_the_right_size():
    rows = rp.all_rows()
    fronts = {r["id"]: r for r in rows if r["view"] == "front"}
    assert set(fronts) == {t["id"] for t in catalog.all_templates(include_unpublished=True) if t["status"] != "archived"}
    assert fronts["nails_marble"]["size"] == "1024x1024"
    assert fronts["hair_women_butterfly_cut"]["size"] == "1024x1536"
    assert {r["view"] for r in rows if r["id"] == "hair_men_man_bun"} == {"front", "side", "back"}
    assert all(r["file"] == f"{r['id']}-{r['view']}.jpg" for r in rows)


def test_prompts_use_catalogue_text_and_matching_models():
    by_id = {r["id"]: r["prompt"] for r in rp.all_rows(["front"])}
    curls = by_id["hair_men_curly_top_fade"]
    assert catalog.get("hair_men_curly_top_fade")["prompt"] in curls and "naturally c" in curls
    assert "coloured a cool, smoky ash brown" in by_id["colour_women_ash_brown"]
    assert "classic, matte statement red lip" in by_id["look_women_red_carpet"]
    assert "No text, no watermark" in by_id["makeup_soft_glam"]


def test_import_attaches_named_files(tmp_path):
    buf = io.BytesIO()
    Image.new("RGB", (400, 600), (120, 100, 90)).save(buf, format="JPEG")
    (tmp_path / "nails_classic_nude-front.jpg").write_bytes(buf.getvalue())
    (tmp_path / "unknown_style-front.jpg").write_bytes(buf.getvalue())
    before = catalog.get("nails_classic_nude")
    try:
        rp.import_folder(str(tmp_path))
        after = catalog.get("nails_classic_nude")
        assert after["image"].startswith(catalog.CATALOG_IMAGE_PREFIX) and after["version"] == before["version"] + 1
        assert catalog.image_path(after["image"])
    finally:
        db = SessionLocal()
        row = db.get(catalog.StyleTemplateModel, "nails_classic_nude")
        path = catalog.image_path(catalog.get("nails_classic_nude")["image"])
        catalog.row_from_dict(before, row)
        db.commit()
        db.close()
        catalog.invalidate()
        if path:
            os.remove(path)
