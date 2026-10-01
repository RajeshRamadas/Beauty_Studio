from PIL import Image

def analyze_face_features(pil_img: Image.Image):
    """
    Analyzes face image geometry, brightness, and color warmth to determine
    face shape, skin tone complexion, undertone, and personalized hairstyle/color recommendations.
    Uses pure Pillow and standard math (no numpy required).
    """
    img = pil_img.convert("RGB")
    width, height = img.size
    aspect_ratio = height / float(width)

    # Resize to 50x50 to compute mean RGB
    small = img.resize((50, 50))
    pixels = list(small.getdata())
    n = len(pixels)
    sum_r = sum(p[0] for p in pixels)
    sum_g = sum(p[1] for p in pixels)
    sum_b = sum(p[2] for p in pixels)

    avg_r = sum_r / float(n)
    avg_g = sum_g / float(n)
    avg_b = sum_b / float(n)
    brightness = (avg_r + avg_g + avg_b) / 3.0

    # Warmth ratio
    warmth = (avg_r - avg_b) / (avg_r + avg_g + avg_b + 1e-5)

    # Face Shape Classification
    if aspect_ratio >= 1.35:
        face_shape = "Oblong / Oval"
        shape_desc = "Balanced vertical proportions with soft jawline contours."
    elif aspect_ratio >= 1.15:
        if warmth > 0.08:
            face_shape = "Oval"
            shape_desc = "Symmetrical, ideal proportions suitable for almost all hairstyles."
        else:
            face_shape = "Heart"
            shape_desc = "Wider forehead tapering into a delicate chin."
    elif aspect_ratio >= 0.95:
        if avg_r > avg_g + 10:
            face_shape = "Square"
            shape_desc = "Defined angular jawline with strong cheekbone width."
        else:
            face_shape = "Round"
            shape_desc = "Soft rounded contours with equal width and length proportions."
    else:
        face_shape = "Diamond"
        shape_desc = "Prominent cheekbones with narrow forehead and chin."

    # Skin Tone & Complexion Classification
    if brightness > 180:
        skin_tone = "Fair Porcelain"
        undertone = "Cool Rosy" if avg_r > avg_g else "Neutral"
    elif brightness > 140:
        skin_tone = "Warm Golden Sand"
        undertone = "Warm Golden" if warmth > 0.05 else "Neutral Beige"
    elif brightness > 90:
        skin_tone = "Warm Olive"
        undertone = "Warm Golden"
    else:
        skin_tone = "Deep Espresso"
        undertone = "Rich Warm"

    # Hairstyle Recommendations based on shape
    if "Oval" in face_shape:
        recommendations = [
            {
                "name": "Glamour Waves",
                "category": "Hairstyle",
                "match_score": 98,
                "reason": "Accentuates natural oval face symmetry with sweeping volumetric waves.",
                "image_url": "sample_glamour_waves.jpg"
            },
            {
                "name": "Beach Waves",
                "category": "Hairstyle",
                "match_score": 95,
                "reason": "Provides effortless lateral movement around cheekbones.",
                "image_url": "sample_beach_waves.jpg"
            },
            {
                "name": "Short Bob",
                "category": "Hairstyle",
                "match_score": 92,
                "reason": "Frames jawline elegantly for a chic French fashion look.",
                "image_url": "sample_short_bob.jpg"
            }
        ]
    elif "Heart" in face_shape:
        recommendations = [
            {
                "name": "Beach Waves",
                "category": "Hairstyle",
                "match_score": 98,
                "reason": "Soft waves balance a wider forehead and draw focus to eyes.",
                "image_url": "sample_beach_waves.jpg"
            },
            {
                "name": "Curtain Bangs",
                "category": "Hairstyle",
                "match_score": 96,
                "reason": "Face-framing curtain bangs soften forehead width.",
                "image_url": "sample_short_bob.jpg"
            },
            {
                "name": "Glamour Waves",
                "category": "Hairstyle",
                "match_score": 91,
                "reason": "Adds fullness around the collarbone and chin.",
                "image_url": "sample_glamour_waves.jpg"
            }
        ]
    elif "Square" in face_shape:
        recommendations = [
            {
                "name": "Glamour Waves",
                "category": "Hairstyle",
                "match_score": 97,
                "reason": "Soft cascading waves round out angular jawline angles.",
                "image_url": "sample_glamour_waves.jpg"
            },
            {
                "name": "Braided Updo",
                "category": "Hairstyle",
                "match_score": 94,
                "reason": "Elongates vertical facial silhouette with crown height.",
                "image_url": "sample_braided_updo.jpg"
            },
            {
                "name": "Beach Waves",
                "category": "Hairstyle",
                "match_score": 90,
                "reason": "Textured layers soften cheekbone prominence.",
                "image_url": "sample_beach_waves.jpg"
            }
        ]
    else:  # Round or Diamond
        recommendations = [
            {
                "name": "Short Bob",
                "category": "Hairstyle",
                "match_score": 97,
                "reason": "Angular bob structure creates vertical length and cheekbone shadow.",
                "image_url": "sample_short_bob.jpg"
            },
            {
                "name": "Braided Updo",
                "category": "Hairstyle",
                "match_score": 95,
                "reason": "Lifts focus upward, creating an elongated aesthetic.",
                "image_url": "sample_braided_updo.jpg"
            },
            {
                "name": "Glamour Waves",
                "category": "Hairstyle",
                "match_score": 93,
                "reason": "Adds volume at crown while maintaining slim side contours.",
                "image_url": "sample_glamour_waves.jpg"
            }
        ]

    # Hair Color Recommendations based on Skin Tone & Undertone
    if "Warm" in undertone or "Golden" in skin_tone:
        color_recommendations = [
            {"name": "Caramel Bronze", "hex": "#c68642", "desc": "Warm golden brown with sun-lit highlights"},
            {"name": "Honey Blonde", "hex": "#e3a857", "desc": "Soft luminous golden blonde"},
            {"name": "Espresso Dark", "hex": "#2b1704", "desc": "Deep glossy black with warm cocoa undertones"},
            {"name": "Rose Gold", "hex": "#b76e79", "desc": "Trendy metallic blush rose color"}
        ]
    else:
        color_recommendations = [
            {"name": "Platinum Ice", "hex": "#e5e4e2", "desc": "Cool high-fashion icy blonde"},
            {"name": "Burgundy Velvet", "hex": "#800020", "desc": "Deep wine red with cool plum reflections"},
            {"name": "Jet Black", "hex": "#0a0a0a", "desc": "High-shine cool monochrome raven black"},
            {"name": "Ash Brown", "hex": "#604e43", "desc": "Sophisticated cool matte brown"}
        ]

    return {
        "face_shape": face_shape,
        "shape_description": shape_desc,
        "skin_tone": skin_tone,
        "undertone": undertone,
        "recommended_hairstyles": recommendations,
        "recommended_hair_colors": color_recommendations
    }
