/*
 * Style catalogue on the client: loads /api/v1/styles, remembers the Women/Men
 * choice on this device, and renders the Home categories, Trending row,
 * Categories screen, style lists and the generator's category menu.
 * Styles without an image are tried on from their text description.
 */
(function () {
  const KEY = 'glow_audience';
  const $ = id => document.getElementById(id);
  const LABELS = {
    'Hairstyle': ['Hairstyles', 'Cuts, colour and styling'],
    'Makeup': ['Makeup', 'Natural, glam, bridal and editorial'],
    'Nail art': ['Nail art', 'Patterns, textures and colours'],
    'Beard & grooming': ['Beard & grooming', 'Beards, stubble and clean shaves'],
    'Overall beauty look': ['Full looks', 'Complete head-to-toe looks']
  };
  const ORDER = ['Hairstyle', 'Makeup', 'Nail art', 'Beard & grooming', 'Overall beauty look'];

  let all = [];
  let audience = 'women';
  try { audience = localStorage.getItem(KEY) === 'men' ? 'men' : 'women'; } catch (e) { /* storage unavailable */ }
  let currentCategory = 'Hairstyle';

  function el(tag, cls, text) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }

  const visible = () => all.filter(s => s.audience === audience || s.audience === 'all');
  const categories = () => ORDER.filter(c => visible().some(s => s.category === c));
  const inCategory = c => visible().filter(s => s.category === c);

  /* A photo, or a tile with an icon when the style has no image yet. */
  function picture(style, cls) {
    if (style.image) {
      const i = el('img', cls);
      i.src = style.image;
      i.alt = style.name;
      return i;
    }
    const t = el('div', cls + ' style-tile');
    t.innerHTML = style.category === 'Beard & grooming'
      ? '<svg viewBox="0 0 24 24"><path d="M6 9c0 7 3 11 6 11s6-4 6-11"/><path d="M9 14c1 1 2 1.5 3 1.5s2-.5 3-1.5"/></svg>'
      : '<svg viewBox="0 0 24 24"><path d="M5 20c0-9 2-16 7-16s7 7 7 16"/><path d="M8 20c0-6 1.5-10 4-11"/></svg>';
    t.setAttribute('role', 'img');
    t.setAttribute('aria-label', style.name);
    return t;
  }

  function open(style) { window.selectPreset(style.category, style.name, style.image); }

  function renderToggles() {
    document.querySelectorAll('.aud-toggle').forEach(group => {
      group.querySelectorAll('button').forEach(b => {
        const on = b.dataset.aud === audience;
        b.classList.toggle('active', on);
        b.setAttribute('aria-pressed', on);
      });
    });
  }

  function renderHome() {
    const cats = $('home-cats');
    if (cats) cats.replaceChildren(...categories().map(c => {
      const card = el('button', 'card card-click cat-card');
      card.type = 'button';
      card.onclick = () => Styles.openCategory(c);
      card.append(el('h3', null, LABELS[c][0]), el('p', 'caption mt-8', inCategory(c).length + ' styles'));
      return card;
    }));
    const trend = $('home-trending');
    if (trend) trend.replaceChildren(...inCategory('Hairstyle').slice(0, 5).map(s => {
      const item = el('button', 'scroll-item');
      item.type = 'button';
      item.onclick = () => open(s);
      item.append(picture(s, 'scroll-img'), el('p', null, s.name), el('p', 'caption', LABELS[s.category][0]));
      return item;
    }));
  }

  function renderCategories() {
    const list = $('cat-list');
    if (!list) return;
    list.replaceChildren(...categories().map(c => {
      const card = el('button', 'card card-click cat-card');
      card.type = 'button';
      card.onclick = () => Styles.openCategory(c);
      card.append(el('h3', null, LABELS[c][0]), el('p', 'caption mt-8', LABELS[c][1]));
      return card;
    }));
  }

  function renderList() {
    const grid = $('style-grid');
    if (!grid) return;
    if (!categories().includes(currentCategory)) currentCategory = 'Hairstyle';
    $('style-title').textContent = LABELS[currentCategory][0];
    grid.replaceChildren(...inCategory(currentCategory).map(s => {
      const card = el('button', 'img-card');
      card.type = 'button';
      card.onclick = () => open(s);
      const info = el('div', 'img-card-info');
      info.append(el('p', null, s.name));
      card.append(picture(s, 'img-card-img'), info);
      return card;
    }));
  }

  function renderCategorySelect() {
    const sel = $('cat-select');
    if (!sel) return;
    const keep = sel.value;
    const cats = categories().length ? categories() : ['Hairstyle', 'Makeup', 'Nail art', 'Overall beauty look'];
    sel.replaceChildren(...cats.map(c => { const o = el('option', null, LABELS[c][0]); o.value = c; return o; }));
    if (cats.includes(keep)) sel.value = keep;
  }

  function renderHero() {
    // The hero's sample photos are women's styles; hide them until men's photos are added.
    const pics = document.querySelector('#screen-2 .hero-pics');
    if (pics) pics.style.display = audience === 'men' ? 'none' : '';
  }

  function renderAll() {
    renderToggles();
    renderHero();
    renderHome();
    renderCategories();
    renderList();
    renderCategorySelect();
  }

  window.Styles = {
    async load() {
      try {
        const res = await fetch('/api/v1/styles');
        if (res.ok) all = await res.json();
      } catch (e) { console.warn('Could not load styles', e); }
      renderAll();
    },
    audience: () => audience,
    setAudience(a) {
      if (a !== 'women' && a !== 'men') return;
      audience = a;
      try { localStorage.setItem(KEY, a); } catch (e) { /* storage unavailable */ }
      renderAll();
    },
    openCategory(c) {
      currentCategory = c;
      renderList();
      window.showScreen('screen-4');
    },
    find: name => all.find(s => s.name === name) || null,
    picture
  };
})();
