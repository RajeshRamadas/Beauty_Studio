/*
 * Product catalogue for the Shop screen.
 * Edit this file to change what the shop sells. Prices are sample values.
 *
 * Fields:
 *   id        unique string
 *   name      product name
 *   brand     brand or line name
 *   category  one of GLOW_SHOP.categories (except "All")
 *   price     number, in GLOW_SHOP.currency
 *   image     optional image path served by the app (falls back to an icon tile)
 *   forTemplates optional list of catalogue template IDs this product suits ("shop the look");
 *               an ID ending in * matches every template starting with it
 */
window.GLOW_SHOP = {
  currency: '$',
  categories: ['All', 'Hair care', 'Colour', 'Makeup', 'Nails', 'Tools'],
  products: [
    { id: 'hc-repair-oil',  name: 'Repair Hair Oil',          brand: 'Glow Pro',  category: 'Hair care', price: 24, forTemplates: ['hair_women_glamour_waves', 'hair_women_beach_waves', 'hair_women_long_layers'] },
    { id: 'hc-curl-cream',  name: 'Defining Curl Cream',      brand: 'Glow Pro',  category: 'Hair care', price: 18, forTemplates: ['hair_women_defined_curls', 'hair_women_soft_curls', 'hair_men_natural_curls', 'hair_men_curly_top_fade'] },
    { id: 'hc-heat-spray',  name: 'Heat Protect Spray',       brand: 'Glow Pro',  category: 'Hair care', price: 16, forTemplates: ['hair_women_glamour_waves', 'hair_women_classic_bob', 'hair_women_sleek_straight'] },
    { id: 'co-gloss',       name: 'Colour Gloss Treatment',   brand: 'Glow Colour', category: 'Colour', price: 32, forTemplates: ['colour_*'] },
    { id: 'co-caramel',     name: 'Caramel Tint Mask',        brand: 'Glow Colour', category: 'Colour', price: 22, forTemplates: ['colour_women_caramel_balayage', 'colour_men_caramel_highlights', 'colour_women_honey_blonde'] },
    { id: 'mk-glass-serum', name: 'Glass Skin Serum',         brand: 'Glow Skin', category: 'Makeup',    price: 28, forTemplates: ['makeup_natural_glow', 'makeup_dewy', 'makeup_radiant'] },
    { id: 'mk-bold-lip',    name: 'Velvet Bold Lip',          brand: 'Glow Skin', category: 'Makeup',    price: 19, forTemplates: ['makeup_classic_red_lip', 'makeup_party'] },
    { id: 'mk-bronze',      name: 'Bronze Glow Palette',      brand: 'Glow Skin', category: 'Makeup',    price: 34, forTemplates: ['makeup_soft_glam', 'makeup_evening', 'makeup_festive', 'makeup_soft_smokey_eye'] },
    { id: 'nl-chrome',      name: 'Rose Gold Chrome Powder',  brand: 'Glow Nails', category: 'Nails',    price: 12, forTemplates: ['nails_rose_gold_chrome'] },
    { id: 'nl-french',      name: 'French Tip Kit',           brand: 'Glow Nails', category: 'Nails',    price: 15, forTemplates: ['nails_french_ombre'] },
    { id: 'tl-wave-wand',   name: 'Ceramic Wave Wand',        brand: 'Glow Tools', category: 'Tools',    price: 69, forTemplates: ['hair_women_glamour_waves', 'hair_women_beach_waves', 'hair_women_wavy_bob'] },
    { id: 'tl-brush',       name: 'Round Blow-dry Brush',     brand: 'Glow Tools', category: 'Tools',    price: 21, forTemplates: ['hair_women_classic_bob', 'hair_women_curtain_bangs', 'hair_women_long_bob_lob', 'hair_women_butterfly_cut'] }
  ]
};
