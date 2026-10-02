"""Check that the OpenAI setup works, outside the app.

    python -m app.scripts.check_openai               # key + model access (free)
    python -m app.scripts.check_openai --test-edit   # also one real, low-quality image edit (small cost)
    python -m app.scripts.check_openai --test-vision # also one face-analysis call (small cost)

Reads the same settings as the server (environment variables or .env).
"""
import argparse
import io
import os
import sys
import time

from openai import OpenAI

from app.core.config import settings
from app.services.provider_adapter import explain_openai_error, key_configured

OK, BAD = "OK  ", "FAIL"


def line(status, text):
    print(f"[{status}] {text}")


def check_model(client, model):
    try:
        client.models.retrieve(model)
        line(OK, f"Model '{model}' is available to this key")
        return True
    except Exception as exc:  # noqa: BLE001 - report any provider error
        line(BAD, f"Model '{model}': {explain_openai_error(exc)}")
        return False


def test_edit(client):
    from app.services.image_processor import process_image, pick_size
    from app.services.prompt_builder import build_prompt

    person = process_image(open("sample_short_bob.jpg", "rb").read(), "Your photo")
    style = process_image(open("sample_glamour_waves.jpg", "rb").read(), "The style reference photo")
    prompt = build_prompt(["Hairstyle"], True, None)
    kwargs = dict(
        model=settings.OPENAI_IMAGE_MODEL,
        image=[("person." + person[2], person[0], person[1]), ("style." + style[2], style[0], style[1])],
        prompt=prompt, size=pick_size(*person[3]), quality="low", output_format="png",
    )
    if settings.OPENAI_INPUT_FIDELITY:
        kwargs["input_fidelity"] = settings.OPENAI_INPUT_FIDELITY
    started = time.time()
    try:
        result = client.images.edit(**kwargs)
    except Exception as exc:  # noqa: BLE001
        line(BAD, f"Test edit: {explain_openai_error(exc)}")
        return False
    import base64
    os.makedirs("storage/diagnostics", exist_ok=True)
    out = "storage/diagnostics/test-edit.png"
    with open(out, "wb") as f:
        f.write(base64.b64decode(result.data[0].b64_json))
    usage = getattr(result, "usage", None)
    line(OK, f"Test edit took {time.time() - started:.1f}s; saved {out} (Short Bob photo given Glamour Waves hair)."
             + (f" Tokens: {usage.total_tokens}" if usage else ""))
    print("       Open that file: if it looks right, the API works and the app is calling it correctly.")
    return True


def test_vision():
    from app.services.face_analyzer import FaceAnalysisFailed, analyze_face
    from app.services.image_processor import process_image

    img, mime, _ext, _size = process_image(open("sample_glamour_waves.jpg", "rb").read(), "Your photo")
    try:
        r = analyze_face(img, mime, "auto")
    except FaceAnalysisFailed as exc:
        line(BAD, f"Face analysis ({settings.OPENAI_VISION_MODEL}): {exc} (see the server log line above for the reason)")
        return False
    recs = [h["name"] for h in r["recommendations"]["hairstyles"]]
    line(OK, f"Face analysis: face shape {r['face_shape']}, skin tone {r['skin_tone']}, hair {r['hair']['texture']}; "
             f"suggests {', '.join(recs) or 'nothing'}")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--test-edit", action="store_true", help="run one real low-quality image edit")
    parser.add_argument("--test-vision", action="store_true", help="run one real face-analysis call")
    args = parser.parse_args()

    print("Glow AI: OpenAI check\n")
    if settings.DEMO_MODE:
        line(BAD, "DEMO_MODE is on: the app blends photos locally and never calls OpenAI. Unset DEMO_MODE.")
    if not key_configured():
        line(BAD, "OPENAI_API_KEY is not set (or is a placeholder). Set it in the environment or .env.")
        return 1
    key = settings.OPENAI_API_KEY
    line(OK, f"OPENAI_API_KEY is set (…{key[-4:]})")

    client = OpenAI(api_key=key, timeout=180, max_retries=0)
    ok = check_model(client, settings.OPENAI_IMAGE_MODEL)
    ok = check_model(client, settings.OPENAI_VISION_MODEL) and ok
    print(f"       Image quality: {settings.OPENAI_IMAGE_QUALITY}; input fidelity: {settings.OPENAI_INPUT_FIDELITY or '(model default)'}")
    if args.test_edit:
        ok = test_edit(client) and ok
    if args.test_vision:
        ok = test_vision() and ok
    print("\nAll good." if ok else "\nFix the FAIL lines above, then restart the server.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
