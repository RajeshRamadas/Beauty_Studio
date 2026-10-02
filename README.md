# AI Beauty Studio — Two-Image Style Reference Test

Upload **your own photo** and a **style reference image**. The backend sends both to the image-edit API, instructing it to apply the reference's requested beauty style to your photo while preserving your identity and the target photo's scene as closely as possible.

## Run on Ubuntu/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="YOUR_API_KEY"
export OPENAI_IMAGE_MODEL="gpt-image-2.5-flare"  # optional; this is the default
export OPENAI_IMAGE_QUALITY="medium"             # optional: low | medium | high | auto
# export OPENAI_INPUT_FIDELITY="high"            # optional; only if your model supports it
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000. Upload both images and click **Apply style to my photo**. Default quality is `medium` (set `OPENAI_IMAGE_QUALITY=low` for cheaper tests). Uploads are auto-rotated and downscaled to 1536px, and the output size follows your photo's aspect ratio. Actual API charges depend on image inputs and generated output.

## Notes
- Each image must be JPG, PNG, or WEBP, at least 256×256 pixels, and no larger than 12 MB.
- Both images are sent to the configured provider. Get consent before using another person's photo; review privacy/retention obligations before production use.
- Results are generative and may not preserve identity or reproduce the reference precisely. Use clear, well-lit images and test with representative examples.
- This is a local development prototype. Before deployment, add authentication, quotas/rate limits, timeouts, secure storage/retention, monitoring, and abuse controls.

## Face analysis
**Analyse my face** (Home screen, or the link under "1. Your Photo" in the generator) sends the photo to an OpenAI vision model (`OPENAI_VISION_MODEL`, default `gpt-5-mini`) and returns face shape, skin tone, undertone, hair texture/length/thickness/colour, recommended hairstyles, makeup and full looks from the app's catalogue, flattering hair colours and tips. "Try on" opens the style with the same photo already selected. It uses the same `OPENAI_API_KEY` as image generation, is limited to `ANALYSIS_LIMIT_PER_DAY` (default 30) per user or IP, and the photo is not stored. The model is told not to infer age, gender, ethnicity or health.

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
