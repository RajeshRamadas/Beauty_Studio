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
uvicorn main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000. Upload both images and click **Apply style to my photo**. Default quality is `medium` (set `OPENAI_IMAGE_QUALITY=low` for cheaper tests). Uploads are auto-rotated and downscaled to 1536px, and the output size follows your photo's aspect ratio. Actual API charges depend on image inputs and generated output.

## Notes
- Each image must be JPG, PNG, or WEBP, at least 256×256 pixels, and no larger than 12 MB.
- Both images are sent to the configured provider. Get consent before using another person's photo; review privacy/retention obligations before production use.
- Results are generative and may not preserve identity or reproduce the reference precisely. Use clear, well-lit images and test with representative examples.
- This is a local development prototype. Before deployment, add authentication, quotas/rate limits, timeouts, secure storage/retention, monitoring, and abuse controls.

## Salons and Shop
- **Salon map search** (`salons.js`) uses free OpenStreetMap services from the browser: Leaflet map tiles, Nominatim for place search and the Overpass API for hairdressers, beauty and nail salons. No API key is needed. These public services have fair-use limits, so a production launch should use a paid tile/geocoding provider or self-hosted instances.
- **Shop** (`shop.js`, `shop-data.js`) shows the catalogue in `shop-data.js` (edit it to change products and prices; current prices are samples). The bag is saved in the browser on that device. Online payment is not connected yet, so checkout explains that instead of taking an order.
