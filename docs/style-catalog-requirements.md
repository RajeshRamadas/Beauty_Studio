# AI Beauty Studio — Men’s and Women’s Style Catalog Requirements

**Version:** 1.0  
**Status:** Draft for MVP planning  
**Platforms:** iOS, Android, tablet, and web

## 1. Purpose

This document defines the initial men’s and women’s hairstyle catalog, makeup templates, hair-color options, and metadata required for AI recommendations and virtual try-on.

The intended flow is: upload a customer photo → analyze visible characteristics → recommend styles from the existing catalog → browse or select any template → adapt the selected style to the customer photo → compare, save, or download the result.

Recommendations are optional suggestions, not restrictions. Face shape, hair texture, and undertone estimates must be treated as uncertain visual estimates rather than definitive judgments.

## 2. Catalog Structure

- Hairstyles: Men, Women, All styles
- Hair colors: color families and application techniques
- Makeup: natural, everyday, glam, occasion, eye, lip, and finish templates
- Future: beard/moustache, nail art, complete looks

Every template has a unique ID, name, category, description, tags, reference images, status, and version.

## 3. Face Shape Categories

| Value | Approximate visual description |
|---|---|
| Oval | Face appears longer than wide, with softly rounded contours |
| Round | Width and length appear relatively similar, with softer contours |
| Square | Forehead and jaw appear comparatively broad and angular |
| Heart | Forehead appears broader than lower face, with a narrower chin |
| Diamond | Cheekbone area appears comparatively broad |
| Oblong / Rectangle | Face appears longer, with relatively straighter side proportions |
| Mixed / Uncertain | Image is ambiguous or does not support a confident estimate |

The system must support “Uncertain.” It must not force a classification from a poor or occluded photograph.

## 4. Men’s Hairstyle Catalog

| Template | Description | Face-shape tags for recommendations |
|---|---|---|
| Buzz Cut | Very short, uniform cut | Oval, square, diamond |
| Crew Cut | Short top with tapered sides | Oval, square, heart |
| French Crop | Short top with forward fringe | Oval, round, square |
| Textured Crop | Short, piecey texture on top | Oval, round, square |
| Caesar Cut | Short cut with small forward fringe | Oval, square, oblong |
| Ivy League | Neat short cut with side-part length | Oval, square, heart |
| Classic Taper | Gradually shorter sides and back | Oval, square, oblong |
| Low Taper Fade | Subtle taper around sideburns and neckline | Oval, round, square, heart |
| Mid Fade | Fade begins around middle of sides | Oval, round, square |
| High Fade | Fade begins higher on sides | Oval, square, oblong |
| Skin Fade | Very short sides fading to skin | Oval, square, diamond |
| Burst Fade | Curved fade around the ear | Oval, square, round |
| Temple Fade | Taper focused around temples | Oval, round, square |
| Classic Side Part | Defined part with controlled volume | Oval, square, oblong |
| Comb Over | Hair directed across from a part | Oval, square, round |
| Textured Quiff | Front section lifted with texture | Oval, round, square |
| Classic Quiff | Structured front height | Oval, square, heart |
| Pompadour | Hair swept upward and backward | Oval, round, square |
| Slicked Back | Hair directed backward | Oval, square, oblong |
| Curtains | Center-parted medium hair | Oval, square, heart |
| Medium Layered Cut | Medium layers for movement | Oval, oblong, square |
| Wavy Fringe | Forward fringe with natural wave | Oval, square, oblong |
| Natural Curls | Curly hair shaped with natural volume | Oval, square, heart |
| Curly Top Fade | Curly volume on top, shorter sides | Oval, round, square |
| Undercut | Longer top contrasted with shorter sides | Oval, square, heart |
| Faux Hawk | Hair styled upward along center | Oval, round, square |
| Modern Mullet | Shorter front/sides with longer back | Oval, square, diamond |
| Man Bun | Longer hair tied into a bun | Oval, square, oblong |
| Shoulder-Length Layers | Longer layered hair | Oval, square, oblong |

Face-shape tags are recommendation metadata only. They must not hide or disable styles.

### Men’s filters

Length (very short/short/medium/long), texture (straight/wavy/curly/coily/unknown), finish (natural/textured/sleek/structured), maintenance (low/medium/high), occasion (everyday/professional/formal/creative), and cut feature (fade/taper/fringe/part/layers/tied-back).

## 5. Women’s Hairstyle Catalog

| Template | Description | Face-shape tags for recommendations |
|---|---|---|
| Pixie Cut | Short, compact silhouette | Oval, heart, square |
| Textured Pixie | Short cut with texture and movement | Oval, round, heart |
| French Bob | Short bob, often with fringe | Oval, heart, oblong |
| Classic Bob | Structured bob around jaw or chin | Oval, heart, oblong |
| Textured Bob | Bob with movement and texture | Oval, square, heart |
| Wavy Bob | Bob-length hair with soft waves | Oval, square, round |
| Long Bob (Lob) | Bob extending toward shoulders | Oval, round, heart, square |
| Layered Lob | Shoulder-length cut with layers | Oval, square, heart |
| Shoulder-Length Layers | Layers around shoulder length | Oval, round, square, heart |
| Shag Cut | Layered, textured cut | Oval, square, oblong |
| Wolf Cut | Shag-inspired cut with pronounced layers | Oval, round, square, heart |
| Butterfly Cut | Long overall length with shorter face-framing layers | Oval, round, square, heart |
| Long Layers | Long hair with graduated layers | Oval, round, square, oblong |
| Face-Framing Layers | Shorter layers around the face | Oval, square, heart, round |
| V-Cut Layers | Long hair with V-shaped back outline | Oval, square, oblong |
| U-Cut Layers | Long hair with rounded U-shaped outline | All shapes |
| Sleek Straight | Smooth straight finish | All shapes |
| Beach Waves | Loose, relaxed waves | Oval, square, heart, round |
| Soft Curls | Soft defined curls | Oval, square, heart, round |
| Defined Curls | More pronounced curl definition | All shapes |
| Curtain Bangs | Center-parted fringe blending into layers | Oval, square, heart, oblong |
| Wispy Bangs | Light, airy fringe | Oval, square, heart |
| Blunt Bangs | Straight, defined fringe | Oval, oblong |
| Side-Swept Bangs | Fringe directed diagonally | Round, square, heart, oblong |
| High Ponytail | Hair gathered high at back | Oval, round, heart |
| Low Ponytail | Hair gathered near nape | All shapes |
| Messy Bun | Casual gathered bun | All shapes |
| Sleek Bun | Smooth, polished bun | All shapes |
| French Braid | Classic woven braid | All shapes |
| Dutch Braid | Raised braid structure | All shapes |
| Fishtail Braid | Fine woven braid pattern | All shapes |
| Crown Braid | Braid arranged around head | All shapes |
| Bridal Updo | Formal gathered hairstyle | All shapes |
| Chignon | Low structured bun | All shapes |

### Women’s filters

Length, texture, cut type, styling method (loose/tied/braided/updo/sleek), maintenance, occasion, and catalog group. Filters must remain optional and removable.

## 6. Hair Color Catalog

Hair color is a separate dimension from haircut so customers can combine one cut with multiple colors.

### Women’s color templates

| Template | Description / tags |
|---|---|
| Natural Black | Deep natural-looking black; neutral/dark |
| Soft Black | Softer black appearance; neutral/dark |
| Espresso Brown | Very deep brown; neutral/dark |
| Dark Chocolate | Rich dark brown; warm |
| Mocha Brown | Balanced brown; neutral |
| Chestnut Brown | Warm brown |
| Caramel Balayage | Blended caramel highlights; warm/highlights |
| Honey Blonde | Golden blonde; warm |
| Beige Blonde | Beige-toned blonde; neutral |
| Ash Brown | Cool-toned brown |
| Copper | Orange-red tone; warm |
| Auburn | Red-brown tone; warm |
| Burgundy | Deep red-purple tone |
| Rose Brown | Brown with muted pink tones |
| Platinum Blonde | Very light blonde |
| Balayage | Gradual blended color placement |
| Face-Framing Highlights | Lighter sections near the face |

### Men’s color templates

| Template | Description / tags |
|---|---|
| Natural Black | Natural-looking black |
| Soft Black | Softer black finish |
| Dark Brown | Deep brown |
| Chocolate Brown | Rich brown |
| Ash Brown | Cool-toned brown |
| Chestnut Brown | Warm brown |
| Caramel Highlights | Subtle lighter sections |
| Salt and Pepper | Mixed dark and gray |
| Silver Gray | Cool silver-gray |
| Platinum Blonde | Very light blonde |
| Copper Brown | Warm copper-brown |
| Burgundy Tint | Subtle red-purple tone |
| Frosted Tips | Lighter tips on selected sections |
| Gray Blending | Blends visible gray with natural color |

### Undertone tags for optional color suggestions

| Estimated undertone | Color families to offer |
|---|---|
| Warm | Golden brown, caramel, honey, copper, warm chestnut |
| Cool | Ash brown, cool chocolate, burgundy, cool black, beige blonde |
| Neutral | Neutral brown, mocha, soft chocolate, beige, balanced highlights |
| Olive / muted | Espresso, mocha, chestnut, muted caramel, selected burgundy |
| Uncertain | Show the full catalog and ask preference |

Undertone estimation is sensitive to lighting, camera processing, makeup and white balance. If confidence is low, do not make a strong claim; show all colors or ask the user.

### Color controls

Preserve natural color, preview selected color, subtle/medium/bold intensity, preserve roots, adjust highlight placement, select maintenance preference, and reset.

## 7. Makeup Template Catalog

Makeup templates should be available to all users and should not be restricted solely by inferred gender.

| Category | Template | Description |
|---|---|---|
| Natural | No-Makeup Makeup | Minimal, natural-looking enhancement |
| Natural | Natural Glow | Soft radiant finish |
| Natural | Soft Nude | Neutral understated palette |
| Everyday | Office Makeup | Subtle professional styling |
| Everyday | Fresh Everyday | Light, fresh appearance |
| Everyday | Minimal Makeup | Reduced intensity |
| Glam | Soft Glam | Blended tones and moderate definition |
| Glam | Full Glam | More pronounced makeup |
| Glam | Smokey Eye | Darker blended eye makeup |
| Glam | Cut Crease | Defined eyeshadow structure |
| Occasion | Bridal | Occasion-specific makeup |
| Occasion | Party | Event-oriented styling |
| Occasion | Evening | Defined evening look |
| Occasion | Festive | Color and finish configurable |
| Eye | Winged Liner | Defined winged eyeliner |
| Eye | Soft Smokey Eye | Blended smoky eye |
| Eye | Graphic Liner | Expressive liner |
| Lip | Nude Lip | Neutral lip color |
| Lip | Rose Lip | Muted rosy tone |
| Lip | Classic Red Lip | Red statement lip |
| Lip | Glossy Lip | Gloss finish |
| Finish | Dewy | Radiant finish |
| Finish | Matte | Reduced-shine finish |
| Finish | Satin | Balanced finish |
| Finish | Radiant | Luminous finish |

Makeup attributes can include foundation finish, blush color/placement, eyeshadow palette, eyeliner shape, brow styling, lip color/finish, highlight intensity, overall intensity and occasion tags.

Controls: natural-to-bold intensity, preserve skin tone, preserve identity/expression, adjust eye makeup, adjust lip color, reset, and try another template.

## 8. AI Analysis and Recommendation Requirements

### Analysis inputs

- Customer photograph
- Image quality and face visibility
- Estimated face shape and confidence
- Visible hair length and texture, when discernible
- Hair color estimate, when lighting permits
- Optional undertone estimate and confidence
- User-selected style category
- Preferences for length, maintenance, occasion and color

### Recommendation flow

1. Retrieve published templates from the selected category.
2. Apply explicit user-selected filters.
3. Compare catalog tags with available analysis attributes.
4. Rank possible templates using a documented method.
5. Return short, nonjudgmental explanations.
6. Keep the complete catalog accessible.

Do not label a hairstyle as objectively bad or unsuitable for a face shape. Suggested labels include “Suggested,” “Another option,” and “Matches your selected preference.” If confidence is weak, avoid presenting false precision.

### Example analysis object

```json
{
  "face_shape": {"value": "round", "confidence": "medium"},
  "hair": {
    "visible_length": "medium",
    "texture": "wavy",
    "natural_color_estimate": "dark_brown"
  },
  "undertone": {"value": "uncertain", "confidence": "low"},
  "image_quality": {
    "face_visible": true,
    "lighting": "good",
    "suitable_for_tryon": true
  }
}
```

## 9. Virtual Try-On Requirements

### Hairstyle

- Adapt selected style to head orientation, perspective and visible hairline.
- Preserve identity, expression, skin tone and unaffected features as much as possible.
- Keep clothing and background unchanged unless requested.
- Do not change hair color unless selected.
- Handle occluded regions conservatively.

### Hair color

- Apply color to visible hair regions only.
- Preserve hairstyle and texture.
- Respect root and highlight settings.
- Avoid recoloring skin, eyebrows or background unintentionally.
- Warn when insufficient hair is visible.

### Makeup

- Apply selected makeup to visible facial regions.
- Preserve identity, expression and face structure.
- Preserve skin texture where possible.
- Avoid unintended skin-tone changes.
- Apply only selected makeup attributes.

### Result controls

Before/after comparison, original/generated toggle, try another template, adjust intensity, regenerate, save to session, download, share with consent, and delete.

## 10. Template Metadata

Example hairstyle record:

```json
{
  "template_id": "hair_women_butterfly_001",
  "name": "Butterfly Cut",
  "category": "hairstyle",
  "catalog_group": "women",
  "description": "Long hairstyle with shorter face-framing layers.",
  "tags": ["long", "layered", "face-framing", "volume"],
  "face_shape_tags": ["oval", "round", "square", "heart"],
  "hair_length_tags": ["medium", "long"],
  "hair_texture_tags": ["straight", "wavy"],
  "maintenance_level": "medium",
  "occasion_tags": ["everyday", "professional", "occasion"],
  "reference_images": {
    "front": "asset-id-front",
    "side": "asset-id-side",
    "back": "asset-id-back"
  },
  "status": "published",
  "version": 1
}
```

Recommended entities: users, customers, customer_sessions, uploaded_images, face_analyses, style_categories, style_templates, style_template_images, style_recommendations, tryon_jobs, generated_images, favorites, consent_records, generation_usage, and audit_events.

AI prompts and provider-specific instructions must be managed by the backend, not trusted from arbitrary client input.

## 11. User Interface Requirements

### Main screens
- Discover
- Hairstyles
- Hair Colors
- Makeup
- Template detail
- Photo upload
- Face-analysis summary
- Recommendations
- Virtual try-on
- Before/after comparison
- My Looks
- Favorites
- Admin catalog management

### Gallery cards
Each card shows a reference image, name, category, description, tags, favorite control, selection state and “Try this style” action.

### Template detail
Show larger reference image, front/side/back views when available, description, tags, maintenance level, related styles and try-on action.

### Search and filters
Search by name or tag. Filter by catalog group, category, face-shape tags, length, texture, color family, undertone tags, occasion, maintenance and featured status. All filters must be removable.

## 12. Admin Requirements

Authorized administrators can create/edit templates, upload reference images, set tags and categories, save drafts, publish/archive, preview, feature, version templates, and review usage and generation success metrics.

Use reference images only when the product has appropriate usage rights. Clearly distinguish reference examples from actual customer-generated results.

## 13. Privacy and Responsible Use

- Obtain explicit consent before processing customer photos.
- Explain how photographs are used.
- Store images privately; use short-lived signed URLs.
- Encrypt data in transit and at rest.
- Keep AI provider keys on the backend.
- Provide deletion of source and generated images.
- Define retention periods and role-based access.
- Do not use customer photos for model training without separate explicit consent.
- Do not infer sensitive attributes from facial appearance.
- Label AI-generated previews.
- Allow uncertain analysis results and manual user choice.

## 14. Suggested Development Phases

### Phase 1 — Catalog foundation
Create schema and seed data; add hairstyle, color and makeup templates; build search, filters, detail screens and admin publishing.

### Phase 2 — Manual try-on
Add camera/gallery upload, validation, consent, template selection, asynchronous generation, result view, comparison and deletion.

### Phase 3 — Face analysis
Add image-quality checks and estimates for face shape and visible hair attributes, including uncertainty and confidence.

### Phase 4 — Recommendations
Match analysis and preferences to catalog metadata; explain suggestions; keep all styles accessible; collect optional feedback.

### Phase 5 — Salon workflows
Add customer profiles, sessions, multiple previews, favorites, usage metrics and quotas.

## 15. Acceptance Criteria

1. Men’s and women’s hairstyle templates can be browsed separately.
2. Makeup templates are not restricted by inferred gender.
3. Hair-color templates can be combined with hairstyle templates.
4. Published templates have unique IDs, categories, descriptions and reference images.
5. Users can search and filter the catalog.
6. Users can select any published template regardless of recommendation status.
7. Face-shape and undertone estimates can return “uncertain.”
8. Recommendations include brief explanations without claiming objective suitability.
9. Hairstyle, color and makeup selections are passed distinctly to try-on.
10. Generated results retain the selected template IDs.
11. Users can compare, save, download and delete results.
12. Source photographs are protected by consent, access control and retention policies.
13. The UI distinguishes reference images from generated customer results.

## 16. Product Design Recommendation

Use composable style dimensions rather than creating a separate template for every combination:

**Hairstyle + Hair Color + Makeup + Optional Finish**

Example:
- Hairstyle: Butterfly Cut
- Hair color: Caramel Balayage
- Makeup: Natural Glow
- Finish: Subtle

This reduces duplicate catalog entries and allows customers to customize the final look. Prioritize catalog quality and reliable manual try-on before adding face analysis and personalized recommendations.
