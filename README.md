# Beautiva — AI Beauty Studio

Upload **your own photo** and a **style reference image**. The backend sends both to the image-edit API, instructing it to apply the reference's requested beauty style to your photo while preserving your identity and the target photo's scene as closely as possible.

## Run on Ubuntu/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="YOUR_API_KEY"
export OPENAI_IMAGE_MODEL="gpt-image-2.5-flare"  # optional; this is the default
export OPENAI_IMAGE_QUALITY="medium"             # optional: low | medium | high | auto
# export OPENAI_INPUT_FIDELITY="high"            # default; keeps faces closer to the photo (set empty to disable)
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

`--reload` restarts the server when code changes. Without it, restart the server after every `git pull`, or new features (for example the photo check) return "Not Found".

Open http://127.0.0.1:8000. Upload both images and click **Apply style to my photo**. Default quality is `medium` (set `OPENAI_IMAGE_QUALITY=low` for cheaper tests). Uploads are auto-rotated and downscaled to 1536px, and the output size follows your photo's aspect ratio. Actual API charges depend on image inputs and generated output.

## Accuracy gate
Every generated look is checked by the vision model before it is shown. It compares your photo, the style and the result and scores four things 0-100: **face kept**, **style match**, **everything else unchanged** and **natural result**. Accuracy is the lowest of the four.

- At or above `QUALITY_MIN_SCORE` (default **90**) the result is shown with its accuracy and breakdown.
- Below it, the image is regenerated with the problems fed back to the model, up to `QUALITY_MAX_ATTEMPTS` (default **2**) attempts in total; the best passing attempt is shown.
- If no attempt passes, or the check itself can't run, the generation fails with the reason and **no image is saved or shown**.

Each extra attempt and check costs another API call. `QUALITY_CHECK=off` disables the gate (not recommended). The score is the model's estimate, not a guarantee; higher `OPENAI_IMAGE_QUALITY` (e.g. `high`) generally raises it.

## Checking the OpenAI connection
If results look wrong, first check the AI is really being used:

```bash
python -m app.scripts.check_openai               # key and model access (free)
python -m app.scripts.check_openai --test-edit   # one real low-quality edit, saved to storage/diagnostics/test-edit.png
python -m app.scripts.check_openai --test-vision # one real face-analysis call
```

The server log also says at start-up whether image generation uses OpenAI (and which model) or is not configured. If an OpenAI call fails (bad key, no credit, model not available, safety block, timeout) the generation fails and the app shows the reason. It never substitutes a fake result. `DEMO_MODE=1` blends the two photos locally without AI for UI testing only; those results are labelled "Demo result: no AI was used".

## Notes
- Each image must be JPG, PNG, or WEBP, at least 256×256 pixels, and no larger than 12 MB.
- Photos are sent to the configured provider only after the user agrees in the app (see Privacy). Get consent before using another person's photo.
- Results are generative and may not preserve identity or reproduce the reference precisely. Use clear, well-lit images and test with representative examples.
- This is a local development prototype. Before deployment, add authentication, quotas/rate limits, timeouts, secure storage/retention, monitoring, and abuse controls.

## Photo check and guided camera
Before a photo is used for try-on or face analysis it is checked by `POST /api/v1/check-photo`:
- **Always (free, local):** too small (< 400 px), too dark, too bright, blurry.
- **With `OPENAI_API_KEY` (vision model, low detail):** no face, more than one face, face or hair cut off, face covered, too far away, not facing the camera, heavy filters.

If anything fails, the app lists what's wrong and offers **Retake photo** or **Upload another**; Generate and Analyse stay locked until the photo passes. **Camera** opens an in-app camera with a face-and-hair outline to frame the whole head (needs HTTPS or localhost; otherwise it falls back to the phone's camera app). Limit: `PHOTO_CHECK_LIMIT_PER_DAY` (default 100).

## Style catalogue
The catalogue follows the requirements doc v1.0 ("Men's and Women's Style Catalog"). Templates are stored in the
`style_templates` table; seed templates in `app/services/catalog_seed.py` are added on start-up when their ID is missing
(admin edits are never overwritten):
- **Hairstyles:** 29 men's and 36 women's, each with face-shape tags, lengths, textures, finish, maintenance, occasions and cut/styling features.
- **Hair colours:** 17 women's and 14 men's, with undertone tags, colour family, technique and a swatch colour.
- **Makeup:** 25 templates (natural, everyday, glam, occasion, eye, lip, finish), **for everyone**, never filtered by gender.
- **Beard & grooming** (6), **nail art** (4) and **complete looks** (8). A look is a preset of template IDs (for example Beach Waves + Honey Blonde + Natural Glow), not a template of its own.

Browse with **Women / Men / All styles** on Home, search by name or tag, and use filters that can each be removed. Each card has a favourite heart (saved on the device) and **Try this style**; the detail page shows front/side/back photos when available, tags, maintenance, related styles and **Add to my look**. Photos are labelled **Reference**; generated results are labelled **AI-generated preview**. Templates without a photo are tried on from their server-side instruction.

`GET /api/v1/styles?group=men&category=Hairstyle` lists published templates (the try-on instructions stay on the server); `GET /api/v1/styles/{id}` returns one.

## Composing a look
The generator ("Create a look") combines one choice per area: hairstyle + hair colour + makeup (+ beard, nails), each from the catalogue or a personalised idea from face analysis, plus an optional reference photo for other areas, **intensity** (subtle / medium / bold) and **Keep my natural roots** for colour. `POST /api/v1/generations` takes:
- `templates`: comma-separated template IDs, one per area;
- `custom_styles`: JSON list of personalised styles `[{"area", "name", "description"}]`;
- `reference_image` + `category`: the areas the reference photo changes;
- `intensity`, `keep_roots`, `notes`, `consent_version`.

Each area is passed to the image model separately, with rules for that area (hair colour only on visible hair, makeup without changing skin tone, and so on). When a chosen template has a reference photo, it is sent as IMAGE 2 for that area only. The result keeps the template IDs and versions it used (`selections` in `GET /api/v1/generations/{id}`, `generation_selections` table). The result screen has before/after, Original / Compare / AI result, Regenerate at another intensity, Download, Share, Delete and Shop this look.

## Photo quality
Better input photos give more accurate results, so the app helps at each step:
- **Smart camera:** live tips while you frame the photo: too dark or too bright, hold still and, on browsers with face detection (Chrome on Android), move closer, move back or centre your face. The outline turns green when the shot is good. **Auto-capture** (on by default, toggle in the camera) takes the photo after about a second of a good, steady frame. Each capture takes a short burst of 4 frames and keeps the sharpest one.
- **Automatic touch-ups** (`app/services/image_enhance.py`), applied before the AI sees your photo, only when needed: brighten a dark face, tone down harsh light, lift flat contrast, reduce a strong colour cast at half strength (so undertone isn't thrown off by yellow indoor light), and sharpen a soft photo slightly. Well-lit photos are left untouched. Nothing is invented: there is no AI upscaling or "face restoration", which changes faces. The photo check says what will be adjusted. Turn it off with `PHOTO_ENHANCE=0`.
- **Side photo for face analysis (optional):** a profile photo next to the front one improves face shape, jawline and hair estimates.
- **Face kept closer to your photo:** `OPENAI_INPUT_FIDELITY` defaults to `high`. If the model doesn't accept it, the app retries without it automatically.
- `OPENAI_IMAGE_QUALITY=high` gives sharper results at a higher cost per try-on (default `medium`).

## Face analysis
**Analyse my face** sends the photo to an OpenAI vision model (`OPENAI_VISION_MODEL`, default `gpt-5-mini`). It returns **estimates with a confidence** (high / medium / low): face shape and undertone (both may be **Uncertain**), skin tone, visible hair length, texture and colour, and image quality. The user chooses **Women's / Men's / All styles**; the app never infers gender, age or ethnicity.

Suggestions come in two kinds:
- **From our catalogue:** templates ranked by `app/services/recommender.py`. The method is documented in that file: filter by the user's preferences, then score face-shape tags (weighted by confidence), texture, current length and undertone. Results are labelled *Suggested*, *Another option* or *Matches your selected preference*, with short reasons. Uncertain estimates are ignored, and if the undertone is uncertain no colour is singled out. Changing the preferences re-ranks with `POST /api/v1/recommendations`, with no new AI call.
- **New ideas for you:** styles the model designs for this person, each linked to the closest catalogue template.

Nothing is hidden or called unsuitable: every template stays available. Limit: `ANALYSIS_LIMIT_PER_DAY` (default 30); the photo is not stored.

## Privacy
- **Consent:** before any photo is checked, analysed or tried on, the app explains how it's used and asks for agreement. The server refuses photos without the current `PHOTO_CONSENT_VERSION` (HTTP 428). Profile → Photo privacy shows the text again.
- **Signed links:** stored images are only reachable through short-lived signed URLs.
- **Deletion:** deleting a result removes its source, reference and result images. Anonymous results are deleted after `RETENTION_DAYS` (default 30).
- Photos are never used for training. Keys stay on the server.

## Reference photos for the catalogue
`docs/reference-photos.md` (and `.csv`) has a ready-to-use image prompt for every style: hairstyles (front, plus optional side and back), hair colours, makeup, beards, nails and looks, with the size and framing to use. Regenerate it after catalogue changes with `python -m app.scripts.reference_photos prompts`.

- **Make the photos** in any image tool, or with `python -m app.scripts.reference_photos generate photos/ --limit 5`. This uses your OpenAI key and costs money; it asks before starting and skips photos that already exist.
- **Attach them** with `python -m app.scripts.reference_photos import photos/`. Files must be named `<template id>-front.jpg`, `-side.jpg` or `-back.jpg`. You can also upload them one at a time in /admin.

Once a style has a photo, its try-on sends that photo as a visual reference for the area it changes.

## Catalogue admin
Set `ADMIN_EMAILS=you@example.com` and sign in at **/admin** (Profile shows **Manage catalogue** for admins). Admins can:
- create templates (saved as drafts);
- edit any field, including the try-on instruction (each save raises the version);
- upload front/side/back reference photos (only ones you have the rights to use);
- publish, archive or feature templates;
- see try-ons and success rate per template.

API: `/api/v1/admin/catalog*`.

## Salons and Shop
- **Salon map search** (`salons.js`) uses **Google Maps + Places** when `GOOGLE_MAPS_API_KEY` is set, showing Google ratings, review counts, today's opening hours, phone and website. Without a key it falls back to free OpenStreetMap services (Leaflet tiles, Nominatim place search, Overpass API), which have fair-use limits. If Google rejects the key, the app switches to OpenStreetMap automatically.

### Setting up Google Maps
1. In [Google Cloud Console](https://console.cloud.google.com/), create a project and enable billing.
2. Enable **Maps JavaScript API** and **Places API (New)**.
3. Create an API key. Under *Application restrictions* choose **Websites** and add your site (for local testing `http://127.0.0.1:8000/*` and `http://localhost:8000/*`). Under *API restrictions* allow only the two APIs above. The key is sent to the browser, so these restrictions are what protect it.
4. Optional: create a Map ID (Google Maps Platform → Map management, JavaScript, vector) and set `GOOGLE_MAPS_MAP_ID`. Without it the built-in `DEMO_MAP_ID` is used, which is fine for development.
5. Start the server with the key:
   ```bash
   export GOOGLE_MAPS_API_KEY="AIza..."
   uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```

Each search makes one Places Nearby Search request (plus one Text Search when the user types a place). Ratings, phone, website and opening hours are billed at Google's higher "Enterprise" field tier, so check current Places API pricing and set a budget alert in Google Cloud.
- **Shop** (`shop.js`, `shop-data.js`) shows the catalogue in `shop-data.js` (edit it to change products and prices; current prices are samples). The bag is saved in the browser on that device. Online payment is not connected yet, so checkout explains that instead of taking an order.
