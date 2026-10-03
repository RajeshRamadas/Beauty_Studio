# Reference photo prompts

Prompts for creating a reference photo for every catalogue style, generated from the catalogue by `python -m app.scripts.reference_photos prompts`. Paste a prompt into your image tool (or run the `generate` command), save the photo with the file name shown, then import it.

139 styles; 269 photos including the optional hairstyle side and back views. The same prompts are in `reference-photos.csv` for batch tools.

## Photo size and format

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

## Side and back views (hairstyles, optional)

Use the style's front prompt and add one of these sentences:

- **Side** (`<id>-side.jpg`): Same person and hairstyle in a side profile view (facing left, 90 degrees), whole head and hair visible.
- **Back** (`<id>-back.jpg`): Same person and hairstyle seen from behind, showing the back and sides of the hairstyle, whole head visible.

Generate the side and back views right after the front one, in the same session or with the front photo as a reference, so it's the same person.

## Hairstyle

### Women's

**Pixie Cut** · `hair_women_pixie_cut-front.jpg` · 1024x1536

> Subject: a woman in her late 20s with light skin, warm undertones and natural brown hair. Hairstyle: a pixie cut: short, close-cropped sides and back with slightly longer, soft layers on top, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Textured Pixie** · `hair_women_textured_pixie-front.jpg` · 1024x1536

> Subject: a woman in her 30s with medium olive skin and dark brown hair. Hairstyle: a textured pixie: short sides, choppy piecey layers on top with movement and a side-swept fringe, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**French Bob** · `hair_women_french_bob-front.jpg` · 1024x1536

> Subject: a woman in her 20s with tan skin and black hair. Hairstyle: a French bob: a jaw-length bob with a soft, slightly tousled edge and a short eyebrow-length fringe, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Classic Bob** · `hair_women_classic_bob-front.jpg` · 1024x1536

> Subject: a woman in her 40s with fair skin, cool undertones and light brown hair. Hairstyle: a sleek chin-length bob with blunt ends and a polished, smooth finish, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Textured Bob** · `hair_women_textured_bob-front.jpg` · 1024x1536

> Subject: a woman in her 30s with light-medium skin, freckles and auburn-brown hair. Hairstyle: a textured bob: chin-length with point-cut ends, lived-in texture and movement, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Wavy Bob** · `hair_women_wavy_bob-front.jpg` · 1024x1536

> Subject: a woman in her 30s with deep brown skin and black hair. Hairstyle: a wavy bob: chin-to-jaw length with soft, loose waves and a side part, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Long Bob (Lob)** · `hair_women_long_bob_lob-front.jpg` · 1024x1536

> Subject: a woman in her late 20s with light skin, warm undertones and natural brown hair. Hairstyle: a long bob (lob): collarbone length with a straight, slightly angled outline, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Layered Lob** · `hair_women_layered_lob-front.jpg` · 1024x1536

> Subject: a woman in her 30s with medium olive skin and dark brown hair. Hairstyle: a layered lob: shoulder length with soft internal layers for movement around the face, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Shoulder-Length Layers** · `hair_women_shoulder_length_layers-front.jpg` · 1024x1536

> Subject: a woman in her 20s with tan skin and black hair. Hairstyle: shoulder-length hair with long, blended layers and a soft, natural finish, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Shag Cut** · `hair_women_shag_cut-front.jpg` · 1024x1536

> Subject: a woman in her 30s with medium brown skin and naturally curly dark hair. Hairstyle: a shag cut: shoulder length with choppy, feathered layers, volume at the crown and a wispy fringe, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Wolf Cut** · `hair_women_wolf_cut-front.jpg` · 1024x1536

> Subject: a woman in her 30s with light-medium skin, freckles and auburn-brown hair. Hairstyle: a wolf cut: heavy, choppy layers around the crown and face, thinner lengths towards the shoulders, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Butterfly Cut** · `hair_women_butterfly_cut-front.jpg` · 1024x1536

> Subject: a woman in her 30s with deep brown skin and black hair. Hairstyle: a butterfly cut: long hair with short face-framing layers from the cheekbones and bouncy volume, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Long Layers** · `hair_women_long_layers-front.jpg` · 1024x1536

> Subject: a woman in her late 20s with light skin, warm undertones and natural brown hair. Hairstyle: long hair below the shoulders with graduated layers for movement and a smooth finish, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Face-Framing Layers** · `hair_women_face_framing_layers-front.jpg` · 1024x1536

> Subject: a woman in her 30s with medium olive skin and dark brown hair. Hairstyle: face-framing layers: shorter layers starting at the chin that frame the face, the rest at its length, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**V-Cut Layers** · `hair_women_v_cut_layers-front.jpg` · 1024x1536

> Subject: a woman in her 20s with tan skin and black hair. Hairstyle: long layered hair cut to a V-shaped point at the back, with soft layers around the face, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**U-Cut Layers** · `hair_women_u_cut_layers-front.jpg` · 1024x1536

> Subject: a woman in her 40s with fair skin, cool undertones and light brown hair. Hairstyle: long layered hair cut to a rounded U-shaped outline at the back, smooth and full, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Sleek Straight** · `hair_women_sleek_straight-front.jpg` · 1024x1536

> Subject: a woman in her 30s with light-medium skin, freckles and auburn-brown hair. Hairstyle: smooth, sleek straight hair with a glossy finish and a centre part, no frizz, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Beach Waves** · `hair_women_beach_waves-front.jpg` · 1024x1536

> Subject: a woman in her 30s with deep brown skin and black hair. Hairstyle: loose, tousled, textured beach waves with a relaxed, undone finish, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Glamour Waves** · `hair_women_glamour_waves-front.jpg` · 1024x1536

> Subject: a woman in her late 20s with light skin, warm undertones and natural brown hair. Hairstyle: long, glossy, voluminous S-shaped waves with soft face-framing layers, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Soft Curls** · `hair_women_soft_curls-front.jpg` · 1024x1536

> Subject: a woman in her 30s with medium olive skin and dark brown hair. Hairstyle: soft, defined curls from mid-length to the ends with a smooth, bouncy finish, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Defined Curls** · `hair_women_defined_curls-front.jpg` · 1024x1536

> Subject: a woman in her 20s with deep brown skin and naturally coily black hair. Hairstyle: pronounced, defined curls all over with full volume and minimal frizz, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Curtain Bangs** · `hair_women_curtain_bangs-front.jpg` · 1024x1536

> Subject: a woman in her 40s with fair skin, cool undertones and light brown hair. Hairstyle: soft curtain bangs parted in the centre, sweeping to frame the cheekbones and blending into layers, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Wispy Bangs** · `hair_women_wispy_bangs-front.jpg` · 1024x1536

> Subject: a woman in her 30s with light-medium skin, freckles and auburn-brown hair. Hairstyle: a light, airy, see-through fringe falling to the eyebrows, the rest of the hair unchanged, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Blunt Bangs** · `hair_women_blunt_bangs-front.jpg` · 1024x1536

> Subject: a woman in her 30s with deep brown skin and black hair. Hairstyle: a straight, blunt, eyebrow-length fringe with a clean edge, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Side-Swept Bangs** · `hair_women_side_swept_bangs-front.jpg` · 1024x1536

> Subject: a woman in her late 20s with light skin, warm undertones and natural brown hair. Hairstyle: a long fringe swept diagonally across the forehead to one side, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**High Ponytail** · `hair_women_high_ponytail-front.jpg` · 1024x1536

> Subject: a woman in her 30s with medium olive skin and dark brown hair. Hairstyle: hair gathered smoothly into a high ponytail at the crown, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Low Ponytail** · `hair_women_low_ponytail-front.jpg` · 1024x1536

> Subject: a woman in her 20s with tan skin and black hair. Hairstyle: hair gathered into a neat low ponytail at the nape with a smooth top, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Messy Bun** · `hair_women_messy_bun-front.jpg` · 1024x1536

> Subject: a woman in her 40s with fair skin, cool undertones and light brown hair. Hairstyle: a casual, loose messy bun at the crown with a few soft face-framing strands, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Sleek Bun** · `hair_women_sleek_bun-front.jpg` · 1024x1536

> Subject: a woman in her 30s with light-medium skin, freckles and auburn-brown hair. Hairstyle: a smooth, polished bun at the back of the head with no flyaways, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**French Braid** · `hair_women_french_braid-front.jpg` · 1024x1536

> Subject: a woman in her 30s with deep brown skin and black hair. Hairstyle: a classic French braid starting at the hairline and running down the back of the head, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Dutch Braid** · `hair_women_dutch_braid-front.jpg` · 1024x1536

> Subject: a woman in her late 20s with light skin, warm undertones and natural brown hair. Hairstyle: a Dutch braid: an inside-out braid that sits raised along the back of the head, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Fishtail Braid** · `hair_women_fishtail_braid-front.jpg` · 1024x1536

> Subject: a woman in her 30s with medium olive skin and dark brown hair. Hairstyle: a fishtail braid with a fine woven pattern, worn over one shoulder, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Crown Braid** · `hair_women_crown_braid-front.jpg` · 1024x1536

> Subject: a woman in her 20s with tan skin and black hair. Hairstyle: a braid wrapped around the head like a crown, with soft loose strands, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Braided Updo** · `hair_women_braided_updo-front.jpg` · 1024x1536

> Subject: a woman in her 40s with fair skin, cool undertones and light brown hair. Hairstyle: an elegant braided updo gathered at the back with soft loose tendrils, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Bridal Updo** · `hair_women_bridal_updo-front.jpg` · 1024x1536

> Subject: a woman in her 30s with light-medium skin, freckles and auburn-brown hair. Hairstyle: a formal bridal updo: hair gathered into a smooth, sculpted low updo with soft face-framing tendrils, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Chignon** · `hair_women_chignon-front.jpg` · 1024x1536

> Subject: a woman in her 30s with deep brown skin and black hair. Hairstyle: a chignon: a low, structured bun at the nape with a smooth, polished top, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

### Men's

**Buzz Cut** · `hair_men_buzz_cut-front.jpg` · 1024x1536

> Subject: a man in his late 20s with light skin and natural brown hair. Hairstyle: an even buzz cut of about 6 mm all over with a clean, natural hairline, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Crew Cut** · `hair_men_crew_cut-front.jpg` · 1024x1536

> Subject: a man in his 30s with medium olive skin and dark brown hair. Hairstyle: a crew cut: 2-3 cm on top, slightly longer at the front, tapered short on the sides and back, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**French Crop** · `hair_men_french_crop-front.jpg` · 1024x1536

> Subject: a man in his 20s with tan skin and black hair. Hairstyle: a French crop: short faded sides, 3-4 cm textured top pushed forward into a short straight fringe, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Textured Crop** · `hair_men_textured_crop-front.jpg` · 1024x1536

> Subject: a man in his 40s with fair skin and light brown hair, a few grey strands. Hairstyle: a textured crop: mid fade on the sides, 4 cm choppy, piecey texture on top with a matte finish, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Caesar Cut** · `hair_men_caesar_cut-front.jpg` · 1024x1536

> Subject: a man in his 30s with light-medium skin and dark blond hair. Hairstyle: a Caesar cut: hair 2-3 cm all over combed forward into a short, straight horizontal fringe, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Ivy League** · `hair_men_ivy_league-front.jpg` · 1024x1536

> Subject: a man in his 30s with deep brown skin and black hair. Hairstyle: an Ivy League cut: short tapered sides, 4-5 cm on top at the front, neatly side-parted and swept, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Classic Taper** · `hair_men_classic_taper-front.jpg` · 1024x1536

> Subject: a man in his late 20s with light skin and natural brown hair. Hairstyle: a classic taper: sides and back gradually shorter down to the neckline, 3-4 cm on top neatly combed, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Low Taper Fade** · `hair_men_low_taper_fade-front.jpg` · 1024x1536

> Subject: a man in his 30s with medium olive skin and dark brown hair. Hairstyle: a low taper fade only around the sideburns and neckline, the rest of the hair kept at its length on top, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Mid Fade** · `hair_men_mid_fade-front.jpg` · 1024x1536

> Subject: a man in his 20s with tan skin and black hair. Hairstyle: a mid fade starting halfway up the sides, blending into 4-5 cm on top, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**High Fade** · `hair_men_high_fade-front.jpg` · 1024x1536

> Subject: a man in his 40s with fair skin and light brown hair, a few grey strands. Hairstyle: a high fade starting near the temples, with 3-5 cm of hair left on top, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Skin Fade** · `hair_men_skin_fade-front.jpg` · 1024x1536

> Subject: a man in his 30s with light-medium skin and dark blond hair. Hairstyle: a skin fade: sides and back blended down to bare skin, 3-4 cm on top, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Burst Fade** · `hair_men_burst_fade-front.jpg` · 1024x1536

> Subject: a man in his 30s with medium brown skin and naturally curly dark hair. Hairstyle: a burst fade curving in a semicircle around each ear, longer hair kept at the back and on top, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Temple Fade** · `hair_men_temple_fade-front.jpg` · 1024x1536

> Subject: a man in his late 20s with light skin and natural brown hair. Hairstyle: a temple fade: a tight taper only at the temples with a crisp hairline, the rest of the cut unchanged, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Classic Side Part** · `hair_men_classic_side_part-front.jpg` · 1024x1536

> Subject: a man in his 30s with medium olive skin and dark brown hair. Hairstyle: a classic side part: tapered sides, 5-6 cm on top combed to one side from a clean, defined part, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Comb Over** · `hair_men_comb_over-front.jpg` · 1024x1536

> Subject: a man in his 20s with tan skin and black hair. Hairstyle: a comb over: short sides, longer top combed across from a low side part with a smooth finish, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Textured Quiff** · `hair_men_textured_quiff-front.jpg` · 1024x1536

> Subject: a man in his 40s with fair skin and light brown hair, a few grey strands. Hairstyle: a textured quiff: short sides, 6-8 cm on top with the front lifted up and back with loose, matte texture, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Classic Quiff** · `hair_men_classic_quiff-front.jpg` · 1024x1536

> Subject: a man in his 30s with light-medium skin and dark blond hair. Hairstyle: a classic quiff: tapered sides, the front 7-9 cm brushed up and back into smooth, structured height, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Pompadour** · `hair_men_pompadour-front.jpg` · 1024x1536

> Subject: a man in his 30s with deep brown skin and black hair. Hairstyle: a pompadour: short sides, long top swept upward and backward into a high, glossy roll at the front, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Slicked Back** · `hair_men_slicked_back-front.jpg` · 1024x1536

> Subject: a man in his late 20s with light skin and natural brown hair. Hairstyle: slicked-back hair: 8-10 cm on top combed straight back with a smooth, light-shine finish, tidy sides, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Curtains** · `hair_men_curtains-front.jpg` · 1024x1536

> Subject: a man in his 30s with medium olive skin and dark brown hair. Hairstyle: curtains: medium-length hair parted in the centre, falling to either side of the forehead to the cheekbones, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Medium Layered Cut** · `hair_men_medium_layered_cut-front.jpg` · 1024x1536

> Subject: a man in his 20s with tan skin and black hair. Hairstyle: a medium layered cut: hair to the ears and collar with soft layers for movement and a natural finish, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Wavy Fringe** · `hair_men_wavy_fringe-front.jpg` · 1024x1536

> Subject: a man in his 30s with medium brown skin and naturally curly dark hair. Hairstyle: a wavy fringe: tapered sides, longer wavy top pushed forward into a loose fringe, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Natural Curls** · `hair_men_natural_curls-front.jpg` · 1024x1536

> Subject: a man in his 20s with deep brown skin and naturally coily black hair. Hairstyle: natural curls: curly hair shaped evenly with defined curls and natural volume, tidy around the ears, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Curly Top Fade** · `hair_men_curly_top_fade-front.jpg` · 1024x1536

> Subject: a man in his 30s with medium brown skin and naturally curly dark hair. Hairstyle: a curly top fade: tight fade on the sides with 5-6 cm of defined curls on top, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Undercut** · `hair_men_undercut-front.jpg` · 1024x1536

> Subject: a man in his late 20s with light skin and natural brown hair. Hairstyle: an undercut: sides and back clipped short with no blending, 8-10 cm on top styled back, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Faux Hawk** · `hair_men_faux_hawk-front.jpg` · 1024x1536

> Subject: a man in his 30s with medium olive skin and dark brown hair. Hairstyle: a faux hawk: short sides, a strip of longer hair along the centre styled upward to a soft peak, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Modern Mullet** · `hair_men_modern_mullet-front.jpg` · 1024x1536

> Subject: a man in his 20s with tan skin and black hair. Hairstyle: a modern mullet: short textured front and sides, longer hair at the back reaching the collar, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Man Bun** · `hair_men_man_bun-front.jpg` · 1024x1536

> Subject: a man in his 40s with fair skin and light brown hair, a few grey strands. Hairstyle: long hair gathered back and tied into a neat bun at the crown, sides smooth, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Shoulder-Length Layers** · `hair_men_shoulder_length_layers-front.jpg` · 1024x1536

> Subject: a man in his 30s with light-medium skin and dark blond hair. Hairstyle: shoulder-length layered hair with a natural texture, tucked behind the ears, in the person's natural hair colour. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

## Hair colour

### Women's

**Natural Black** · `colour_women_natural_black-front.jpg` · 1024x1536

> Subject: a woman in her 40s with fair skin, cool undertones and light brown hair. Hair: long, soft layered hair falling past the shoulders, coloured a deep, natural-looking black with a soft shine. The colour must be clearly visible in soft daylight. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Soft Black** · `colour_women_soft_black-front.jpg` · 1024x1536

> Subject: a woman in her 40s with fair skin, cool undertones and light brown hair. Hair: long, soft layered hair falling past the shoulders, coloured a soft black with a hint of brown, less harsh than jet black. The colour must be clearly visible in soft daylight. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Espresso Brown** · `colour_women_espresso_brown-front.jpg` · 1024x1536

> Subject: a woman in her 40s with fair skin, cool undertones and light brown hair. Hair: long, soft layered hair falling past the shoulders, coloured a very deep espresso brown. The colour must be clearly visible in soft daylight. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Dark Chocolate** · `colour_women_dark_chocolate-front.jpg` · 1024x1536

> Subject: a woman in her 40s with fair skin, cool undertones and light brown hair. Hair: long, soft layered hair falling past the shoulders, coloured a rich dark chocolate brown with warm depth. The colour must be clearly visible in soft daylight. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Mocha Brown** · `colour_women_mocha_brown-front.jpg` · 1024x1536

> Subject: a woman in her 40s with fair skin, cool undertones and light brown hair. Hair: long, soft layered hair falling past the shoulders, coloured a balanced mid mocha brown. The colour must be clearly visible in soft daylight. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Chestnut Brown** · `colour_women_chestnut_brown-front.jpg` · 1024x1536

> Subject: a woman in her 40s with fair skin, cool undertones and light brown hair. Hair: long, soft layered hair falling past the shoulders, coloured a warm chestnut brown with reddish-gold reflections. The colour must be clearly visible in soft daylight. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Caramel Balayage** · `colour_women_caramel_balayage-front.jpg` · 1024x1536

> Subject: a woman in her 40s with fair skin, cool undertones and light brown hair. Hair: long, soft layered hair falling past the shoulders, coloured a caramel balayage: hand-painted caramel lightening from mid-lengths to ends, blended into the base. The colour must be clearly visible in soft daylight. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Honey Blonde** · `colour_women_honey_blonde-front.jpg` · 1024x1536

> Subject: a woman in her 40s with fair skin, cool undertones and light brown hair. Hair: long, soft layered hair falling past the shoulders, coloured a golden honey blonde. The colour must be clearly visible in soft daylight. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Beige Blonde** · `colour_women_beige_blonde-front.jpg` · 1024x1536

> Subject: a woman in her 40s with fair skin, cool undertones and light brown hair. Hair: long, soft layered hair falling past the shoulders, coloured a soft beige blonde with neutral tones. The colour must be clearly visible in soft daylight. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Ash Brown** · `colour_women_ash_brown-front.jpg` · 1024x1536

> Subject: a woman in her 40s with fair skin, cool undertones and light brown hair. Hair: long, soft layered hair falling past the shoulders, coloured a cool, smoky ash brown with no warmth. The colour must be clearly visible in soft daylight. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Copper** · `colour_women_copper-front.jpg` · 1024x1536

> Subject: a woman in her 40s with fair skin, cool undertones and light brown hair. Hair: long, soft layered hair falling past the shoulders, coloured a vivid copper with orange-red tones. The colour must be clearly visible in soft daylight. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Auburn** · `colour_women_auburn-front.jpg` · 1024x1536

> Subject: a woman in her 40s with fair skin, cool undertones and light brown hair. Hair: long, soft layered hair falling past the shoulders, coloured a rich auburn red-brown. The colour must be clearly visible in soft daylight. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Burgundy** · `colour_women_burgundy-front.jpg` · 1024x1536

> Subject: a woman in her 40s with fair skin, cool undertones and light brown hair. Hair: long, soft layered hair falling past the shoulders, coloured a deep burgundy red-purple. The colour must be clearly visible in soft daylight. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Rose Brown** · `colour_women_rose_brown-front.jpg` · 1024x1536

> Subject: a woman in her 40s with fair skin, cool undertones and light brown hair. Hair: long, soft layered hair falling past the shoulders, coloured a brown with muted rose-pink tones. The colour must be clearly visible in soft daylight. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Platinum Blonde** · `colour_women_platinum_blonde-front.jpg` · 1024x1536

> Subject: a woman in her 40s with fair skin, cool undertones and light brown hair. Hair: long, soft layered hair falling past the shoulders, coloured a very light, icy platinum blonde. The colour must be clearly visible in soft daylight. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Balayage** · `colour_women_balayage-front.jpg` · 1024x1536

> Subject: a woman in her 40s with fair skin, cool undertones and light brown hair. Hair: long, soft layered hair falling past the shoulders, coloured a natural balayage: soft, gradual lighter pieces from mid-lengths to ends, a few shades lighter than the base. The colour must be clearly visible in soft daylight. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Face-Framing Highlights** · `colour_women_face_framing_highlights-front.jpg` · 1024x1536

> Subject: a woman in her 40s with fair skin, cool undertones and light brown hair. Hair: long, soft layered hair falling past the shoulders, coloured face-framing highlights: two lighter sections at the front framing the face, the rest of the colour unchanged. The colour must be clearly visible in soft daylight. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

### Men's

**Natural Black** · `colour_men_natural_black-front.jpg` · 1024x1536

> Subject: a man in his late 20s with light skin and natural brown hair. Hair: a short textured crop with 4-5 cm on top and tapered sides, coloured a natural-looking black with a matte finish. The colour must be clearly visible in soft daylight. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Soft Black** · `colour_men_soft_black-front.jpg` · 1024x1536

> Subject: a man in his late 20s with light skin and natural brown hair. Hair: a short textured crop with 4-5 cm on top and tapered sides, coloured a soft black with a hint of brown. The colour must be clearly visible in soft daylight. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Dark Brown** · `colour_men_dark_brown-front.jpg` · 1024x1536

> Subject: a man in his late 20s with light skin and natural brown hair. Hair: a short textured crop with 4-5 cm on top and tapered sides, coloured a deep natural dark brown. The colour must be clearly visible in soft daylight. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Chocolate Brown** · `colour_men_chocolate_brown-front.jpg` · 1024x1536

> Subject: a man in his late 20s with light skin and natural brown hair. Hair: a short textured crop with 4-5 cm on top and tapered sides, coloured a rich chocolate brown. The colour must be clearly visible in soft daylight. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Ash Brown** · `colour_men_ash_brown-front.jpg` · 1024x1536

> Subject: a man in his late 20s with light skin and natural brown hair. Hair: a short textured crop with 4-5 cm on top and tapered sides, coloured a cool ash brown with no warmth. The colour must be clearly visible in soft daylight. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Chestnut Brown** · `colour_men_chestnut_brown-front.jpg` · 1024x1536

> Subject: a man in his late 20s with light skin and natural brown hair. Hair: a short textured crop with 4-5 cm on top and tapered sides, coloured a warm chestnut brown. The colour must be clearly visible in soft daylight. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Caramel Highlights** · `colour_men_caramel_highlights-front.jpg` · 1024x1536

> Subject: a man in his late 20s with light skin and natural brown hair. Hair: a short textured crop with 4-5 cm on top and tapered sides, coloured subtle caramel highlights on the top section only, blended into the base colour. The colour must be clearly visible in soft daylight. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Salt and Pepper** · `colour_men_salt_and_pepper-front.jpg` · 1024x1536

> Subject: a man in his late 20s with light skin and natural brown hair. Hair: a short textured crop with 4-5 cm on top and tapered sides, coloured a salt-and-pepper mix of dark hair and grey strands. The colour must be clearly visible in soft daylight. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Silver Gray** · `colour_men_silver_gray-front.jpg` · 1024x1536

> Subject: a man in his late 20s with light skin and natural brown hair. Hair: a short textured crop with 4-5 cm on top and tapered sides, coloured a cool, even silver grey. The colour must be clearly visible in soft daylight. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Platinum Blonde** · `colour_men_platinum_blonde-front.jpg` · 1024x1536

> Subject: a man in his late 20s with light skin and natural brown hair. Hair: a short textured crop with 4-5 cm on top and tapered sides, coloured a very light, icy platinum blonde. The colour must be clearly visible in soft daylight. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Copper Brown** · `colour_men_copper_brown-front.jpg` · 1024x1536

> Subject: a man in his late 20s with light skin and natural brown hair. Hair: a short textured crop with 4-5 cm on top and tapered sides, coloured a warm copper brown. The colour must be clearly visible in soft daylight. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Burgundy Tint** · `colour_men_burgundy_tint-front.jpg` · 1024x1536

> Subject: a man in his late 20s with light skin and natural brown hair. Hair: a short textured crop with 4-5 cm on top and tapered sides, coloured a subtle burgundy red-purple tint over the natural base. The colour must be clearly visible in soft daylight. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Frosted Tips** · `colour_men_frosted_tips-front.jpg` · 1024x1536

> Subject: a man in his late 20s with light skin and natural brown hair. Hair: a short textured crop with 4-5 cm on top and tapered sides, coloured frosted tips: only the tips of the top section lightened to pale blonde. The colour must be clearly visible in soft daylight. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Gray Blending** · `colour_men_gray_blending-front.jpg` · 1024x1536

> Subject: a man in his late 20s with light skin and natural brown hair. Hair: a short textured crop with 4-5 cm on top and tapered sides, coloured grey blending: visible grey strands softened so they blend with the natural colour, still natural-looking. The colour must be clearly visible in soft daylight. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

## Makeup

### For everyone

**No-Makeup Makeup** · `makeup_no_makeup_makeup-front.jpg` · 1024x1536

> Subject: a woman in her late 20s with light skin, warm undertones and natural brown hair. Makeup: minimal makeup that looks like none: evened-out skin with sheer coverage, groomed brows, clear mascara, tinted lip balm. Hair pulled back off the face. Close head-and-shoulders framing so the makeup detail is clear. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Natural Glow** · `makeup_natural_glow-front.jpg` · 1024x1536

> Subject: a woman in her 30s with medium olive skin and dark brown hair. Makeup: fresh, dewy skin with light coverage, soft brows, rosy cheeks and a tinted lip. Hair pulled back off the face. Close head-and-shoulders framing so the makeup detail is clear. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Soft Nude** · `makeup_soft_nude-front.jpg` · 1024x1536

> Subject: a woman in her 20s with tan skin and black hair. Makeup: neutral nude makeup: soft taupe eyeshadow, thin brown liner, light mascara and a nude lip. Hair pulled back off the face. Close head-and-shoulders framing so the makeup detail is clear. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Office Makeup** · `makeup_office_makeup-front.jpg` · 1024x1536

> Subject: a woman in her 40s with fair skin, cool undertones and light brown hair. Makeup: polished office makeup: even satin skin, defined brows, matte neutral eyeshadow, mascara and a muted rose lip. Hair pulled back off the face. Close head-and-shoulders framing so the makeup detail is clear. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Fresh Everyday** · `makeup_fresh_everyday-front.jpg` · 1024x1536

> Subject: a woman in her 30s with light-medium skin, freckles and auburn-brown hair. Makeup: fresh everyday makeup: light skin tint, a touch of peach blush, mascara and a glossy lip. Hair pulled back off the face. Close head-and-shoulders framing so the makeup detail is clear. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Minimal Makeup** · `makeup_minimal_makeup-front.jpg` · 1024x1536

> Subject: a man in his 30s with deep brown skin and black hair. Makeup: minimal makeup: concealer only where needed, brushed-up brows and a sheer lip colour. Hair pulled back off the face. Close head-and-shoulders framing so the makeup detail is clear. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Soft Glam** · `makeup_soft_glam-front.jpg` · 1024x1536

> Subject: a woman in her late 20s with light skin, warm undertones and natural brown hair. Makeup: soft glam: warm neutral blended eyeshadow, soft winged liner, defined lashes, sculpted cheeks and a nude-pink lip. Hair pulled back off the face. Close head-and-shoulders framing so the makeup detail is clear. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Full Glam** · `makeup_full_glam-front.jpg` · 1024x1536

> Subject: a woman in her 30s with medium olive skin and dark brown hair. Makeup: full glam: full-coverage skin, contour and highlight, dramatic eyeshadow, lashes and a defined lip. Hair pulled back off the face. Close head-and-shoulders framing so the makeup detail is clear. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Smokey Eye** · `makeup_smokey_eye-front.jpg` · 1024x1536

> Subject: a woman in her 20s with tan skin and black hair. Makeup: a smokey eye: blended charcoal eyeshadow, smudged liner on the waterline, full lashes and a neutral lip. Hair pulled back off the face. Close head-and-shoulders framing so the makeup detail is clear. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Cut Crease** · `makeup_cut_crease-front.jpg` · 1024x1536

> Subject: a woman in her 40s with fair skin, cool undertones and light brown hair. Makeup: a cut crease: a sharply defined crease line with a light lid colour and winged liner. Hair pulled back off the face. Close head-and-shoulders framing so the makeup detail is clear. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Bridal** · `makeup_bridal-front.jpg` · 1024x1536

> Subject: a woman in her 30s with light-medium skin, freckles and auburn-brown hair. Makeup: long-wear bridal makeup: soft-matte flawless skin, shimmer lids, lashes, soft blush and a rose lip. Hair pulled back off the face. Close head-and-shoulders framing so the makeup detail is clear. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Party** · `makeup_party-front.jpg` · 1024x1536

> Subject: a woman in her 30s with deep brown skin and black hair. Makeup: party makeup: shimmer eyeshadow, winged liner, glowing highlight and a bold glossy lip. Hair pulled back off the face. Close head-and-shoulders framing so the makeup detail is clear. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Evening** · `makeup_evening-front.jpg` · 1024x1536

> Subject: a woman in her late 20s with light skin, warm undertones and natural brown hair. Makeup: evening makeup: defined bronze eyes, sculpted cheeks and a deep berry lip. Hair pulled back off the face. Close head-and-shoulders framing so the makeup detail is clear. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Festive** · `makeup_festive-front.jpg` · 1024x1536

> Subject: a woman in her 30s with medium olive skin and dark brown hair. Makeup: festive makeup: jewel-toned shimmer eyeshadow, gold inner-corner highlight, kohl liner and a rich red lip. Hair pulled back off the face. Close head-and-shoulders framing so the makeup detail is clear. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Winged Liner** · `makeup_winged_liner-front.jpg` · 1024x1536

> Subject: a woman in her 20s with tan skin and black hair. Makeup: a clean black winged eyeliner flick on the upper lid, the rest of the face unchanged. Hair pulled back off the face. Close head-and-shoulders framing so the makeup detail is clear. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Soft Smokey Eye** · `makeup_soft_smokey_eye-front.jpg` · 1024x1536

> Subject: a woman in her 40s with fair skin, cool undertones and light brown hair. Makeup: a soft brown smokey eye, lightly blended, with mascara. Hair pulled back off the face. Close head-and-shoulders framing so the makeup detail is clear. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Graphic Liner** · `makeup_graphic_liner-front.jpg` · 1024x1536

> Subject: a woman in her 30s with light-medium skin, freckles and auburn-brown hair. Makeup: graphic eyeliner: a bold, sharp geometric liner shape on the upper lid. Hair pulled back off the face. Close head-and-shoulders framing so the makeup detail is clear. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Nude Lip** · `makeup_nude_lip-front.jpg` · 1024x1536

> Subject: a woman in her 30s with deep brown skin and black hair. Makeup: a creamy nude lip colour close to the natural lip tone. Hair pulled back off the face. Close head-and-shoulders framing so the makeup detail is clear. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Rose Lip** · `makeup_rose_lip-front.jpg` · 1024x1536

> Subject: a woman in her late 20s with light skin, warm undertones and natural brown hair. Makeup: a muted rose lip colour. Hair pulled back off the face. Close head-and-shoulders framing so the makeup detail is clear. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Classic Red Lip** · `makeup_classic_red_lip-front.jpg` · 1024x1536

> Subject: a woman in her 30s with medium olive skin and dark brown hair. Makeup: a classic, matte statement red lip. Hair pulled back off the face. Close head-and-shoulders framing so the makeup detail is clear. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Glossy Lip** · `makeup_glossy_lip-front.jpg` · 1024x1536

> Subject: a woman in her 20s with tan skin and black hair. Makeup: a sheer, glossy lip finish over the natural lip colour. Hair pulled back off the face. Close head-and-shoulders framing so the makeup detail is clear. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Dewy** · `makeup_dewy-front.jpg` · 1024x1536

> Subject: a woman in her 40s with fair skin, cool undertones and light brown hair. Makeup: a dewy skin finish with natural radiance, no heavy coverage. Hair pulled back off the face. Close head-and-shoulders framing so the makeup detail is clear. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Matte** · `makeup_matte-front.jpg` · 1024x1536

> Subject: a woman in her 30s with light-medium skin, freckles and auburn-brown hair. Makeup: a soft-matte skin finish that reduces shine, skin texture kept. Hair pulled back off the face. Close head-and-shoulders framing so the makeup detail is clear. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Satin** · `makeup_satin-front.jpg` · 1024x1536

> Subject: a man in his 30s with deep brown skin and black hair. Makeup: a satin skin finish between matte and dewy. Hair pulled back off the face. Close head-and-shoulders framing so the makeup detail is clear. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Radiant** · `makeup_radiant-front.jpg` · 1024x1536

> Subject: a woman in her late 20s with light skin, warm undertones and natural brown hair. Makeup: a luminous, radiant skin finish with highlight on the cheekbones. Hair pulled back off the face. Close head-and-shoulders framing so the makeup detail is clear. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

## Beard & grooming

### Men's

**Full Beard** · `beard_full_beard-front.jpg` · 1024x1536

> Subject: a man in his late 20s with light skin and natural brown hair. Facial hair: a full, well-groomed beard about 2-3 cm long with a sharp cheek line and neckline. Hair: a short, neat classic taper. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Short Boxed Beard** · `beard_short_boxed_beard-front.jpg` · 1024x1536

> Subject: a man in his 30s with medium olive skin and dark brown hair. Facial hair: a short boxed beard about 1 cm long with crisp edges and a connected moustache. Hair: a short, neat classic taper. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Designer Stubble** · `beard_designer_stubble-front.jpg` · 1024x1536

> Subject: a man in his 20s with tan skin and black hair. Facial hair: even designer stubble of a few days' growth with a tidy neckline. Hair: a short, neat classic taper. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Goatee** · `beard_goatee-front.jpg` · 1024x1536

> Subject: a man in his 40s with fair skin and light brown hair, a few grey strands. Facial hair: a neat goatee: hair on the chin connected to a trimmed moustache, cheeks clean-shaven. Hair: a short, neat classic taper. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Classic Moustache** · `beard_classic_moustache-front.jpg` · 1024x1536

> Subject: a man in his 30s with light-medium skin and dark blond hair. Facial hair: a trimmed classic moustache along the top lip, the rest of the face clean-shaven. Hair: a short, neat classic taper. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Clean Shave** · `beard_clean_shave-front.jpg` · 1024x1536

> Subject: a man in his 30s with deep brown skin and black hair. Facial hair: a smooth, clean-shaven face with no facial hair. Hair: a short, neat classic taper. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

## Nail art

### For everyone

**French Ombre** · `nails_french_ombre-front.jpg` · 1024x1024

> Close-up of one relaxed hand resting on a plain warm light-grey surface, fingers slightly apart, all nails clearly visible and in sharp focus: a soft pink-to-white French ombre manicure. Medium-length nails, natural skin. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Rose Gold Chrome** · `nails_rose_gold_chrome-front.jpg` · 1024x1024

> Close-up of one relaxed hand resting on a plain warm light-grey surface, fingers slightly apart, all nails clearly visible and in sharp focus: mirror-finish rose gold chrome nails. Medium-length nails, natural skin. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Classic Nude** · `nails_classic_nude-front.jpg` · 1024x1024

> Close-up of one relaxed hand resting on a plain warm light-grey surface, fingers slightly apart, all nails clearly visible and in sharp focus: glossy classic nude almond nails. Medium-length nails, natural skin. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Marble** · `nails_marble-front.jpg` · 1024x1024

> Close-up of one relaxed hand resting on a plain warm light-grey surface, fingers slightly apart, all nails clearly visible and in sharp focus: white marble nail art with fine grey and gold veins. Medium-length nails, natural skin. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

## Overall beauty look

### Women's

**Red Carpet** · `look_women_red_carpet-front.jpg` · 1024x1536

> Subject: a woman in her late 20s with light skin, warm undertones and natural brown hair. Hairstyle: long, glossy, voluminous S-shaped waves with soft face-framing layers. Makeup: a classic, matte statement red lip. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Evening Gala** · `look_women_evening_gala-front.jpg` · 1024x1536

> Subject: a woman in her 30s with medium olive skin and dark brown hair. Hairstyle: an elegant braided updo gathered at the back with soft loose tendrils. Makeup: a smokey eye: blended charcoal eyeshadow, smudged liner on the waterline, full lashes and a neutral lip. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Bridal Luxe** · `look_women_bridal_luxe-front.jpg` · 1024x1536

> Subject: a woman in her 20s with tan skin and black hair. Hairstyle: a formal bridal updo: hair gathered into a smooth, sculpted low updo with soft face-framing tendrils. Makeup: long-wear bridal makeup: soft-matte flawless skin, shimmer lids, lashes, soft blush and a rose lip. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Sunny Weekend** · `look_women_sunny_weekend-front.jpg` · 1024x1536

> Subject: a woman in her 40s with fair skin, cool undertones and light brown hair. Hairstyle: loose, tousled, textured beach waves with a relaxed, undone finish. Hair colour: a golden honey blonde. Makeup: fresh, dewy skin with light coverage, soft brows, rosy cheeks and a tinted lip. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Office Ready** · `look_women_office_ready-front.jpg` · 1024x1536

> Subject: a woman in her 30s with light-medium skin, freckles and auburn-brown hair. Hairstyle: a long bob (lob): collarbone length with a straight, slightly angled outline. Makeup: polished office makeup: even satin skin, defined brows, matte neutral eyeshadow, mascara and a muted rose lip. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

### Men's

**Groom Look** · `look_men_groom_look-front.jpg` · 1024x1536

> Subject: a man in his late 20s with light skin and natural brown hair. Hairstyle: a classic side part: tapered sides, 5-6 cm on top combed to one side from a clean, defined part. Beard & grooming: a short boxed beard about 1 cm long with crisp edges and a connected moustache. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Smart Classic** · `look_men_smart_classic-front.jpg` · 1024x1536

> Subject: a man in his 30s with medium olive skin and dark brown hair. Hairstyle: a classic taper: sides and back gradually shorter down to the neckline, 3-4 cm on top neatly combed. Beard & grooming: a smooth, clean-shaven face with no facial hair. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.

**Weekend Texture** · `look_men_weekend_texture-front.jpg` · 1024x1536

> Subject: a man in his 20s with tan skin and black hair. Hairstyle: a textured crop: mid fade on the sides, 4 cm choppy, piecey texture on top with a matte finish. Beard & grooming: even designer stubble of a few days' growth with a tidy neckline. Head and shoulders, centred, facing the camera and looking into the lens, relaxed natural expression. The whole head and all of the hair are visible, with clear space above the top of the head. Simple black crew-neck top, no jewellery, no hat, no glasses, no hands near the face. Professional beauty catalogue reference photo, photorealistic, shot on a full-frame camera with an 85 mm lens. Plain warm light-grey studio background, soft even front lighting, natural skin texture, true-to-life colours. No text, no watermark, no logo.
