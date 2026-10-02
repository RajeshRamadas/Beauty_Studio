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
 *   forStyles optional list of style names this product suits ("shop the look")
 */
window.GLOW_SHOP = {
  currency: '$',
  categories: ['All', 'Hair care', 'Colour', 'Makeup', 'Nails', 'Tools'],
  products: [
    { id: 'hc-repair-oil',  name: 'Repair Hair Oil',          brand: 'Glow Pro',  category: 'Hair care', price: 24, forStyles: ['Glamour Waves', 'Beach Waves'] },
    { id: 'hc-curl-cream',  name: 'Defining Curl Cream',      brand: 'Glow Pro',  category: 'Hair care', price: 18, forStyles: ['Volumetric Curls', 'Beach Waves'] },
    { id: 'hc-heat-spray',  name: 'Heat Protect Spray',       brand: 'Glow Pro',  category: 'Hair care', price: 16, forStyles: ['Glamour Waves', 'Short Bob'] },
    { id: 'co-gloss',       name: 'Colour Gloss Treatment',   brand: 'Glow Colour', category: 'Colour', price: 32, forStyles: [] },
    { id: 'co-caramel',     name: 'Caramel Tint Mask',        brand: 'Glow Colour', category: 'Colour', price: 22, forStyles: ['Glamour Waves'] },
    { id: 'mk-glass-serum', name: 'Glass Skin Serum',         brand: 'Glow Skin', category: 'Makeup',    price: 28, forStyles: ['Korean Glass Skin', 'Natural Glow'] },
    { id: 'mk-bold-lip',    name: 'Velvet Bold Lip',          brand: 'Glow Skin', category: 'Makeup',    price: 19, forStyles: ['Bold Lip', 'Red Carpet'] },
    { id: 'mk-bronze',      name: 'Bronze Glow Palette',      brand: 'Glow Skin', category: 'Makeup',    price: 34, forStyles: ['Party Bronze', 'Evening Gala'] },
    { id: 'nl-chrome',      name: 'Rose Gold Chrome Powder',  brand: 'Glow Nails', category: 'Nails',    price: 12, forStyles: ['Rose Gold Chrome'] },
    { id: 'nl-french',      name: 'French Tip Kit',           brand: 'Glow Nails', category: 'Nails',    price: 15, forStyles: ['French Ombre'] },
    { id: 'tl-wave-wand',   name: 'Ceramic Wave Wand',        brand: 'Glow Tools', category: 'Tools',    price: 69, forStyles: ['Glamour Waves', 'Beach Waves'] },
    { id: 'tl-brush',       name: 'Round Blow-dry Brush',     brand: 'Glow Tools', category: 'Tools',    price: 21, forStyles: ['Short Bob', 'Curtain Bangs'] }
  ]
};
