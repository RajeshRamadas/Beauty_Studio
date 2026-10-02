/*
 * Style catalogue on the client (requirements 11): loads published templates
 * from /api/v1/styles, remembers the Women / Men / All choice and favourites on
 * this device, and renders Home, the category list, a searchable, filterable
 * gallery, the template detail and favourites. Every template can be tried on,
 * whatever any recommendation says.
 */
(function () {
  const AUD_KEY = 'glow_audience';
  const FAV_KEY = 'glow_favourites';
  const $ = id => document.getElementById(id);

  const LABELS = {
    'Hairstyle': ['Hairstyles', 'Cuts, fades, layers, braids and updos'],
    'Hair colour': ['Hair colours', 'Shades, highlights and balayage'],
    'Makeup': ['Makeup', 'Natural to glam, for everyone'],
    'Beard & grooming': ['Beard & grooming', 'Beards, stubble and clean shaves'],
    'Nail art': ['Nail art', 'Designs and finishes'],
    'Overall beauty look': ['Complete looks', 'Hair, colour and makeup together']
  };
  const ORDER = ['Hairstyle', 'Hair colour', 'Makeup', 'Beard & grooming', 'Nail art', 'Overall beauty look'];
  const SHORT = { 'Hairstyle': 'Hairstyle', 'Hair colour': 'Hair colour', 'Makeup': 'Makeup', 'Beard & grooming': 'Beard',
                  'Nail art': 'Nails', 'Overall beauty look': 'Look' };

  // Filters per category: [key on the template, label]. Values come from the catalogue itself.
  const FILTERS = {
    'Hairstyle': [['lengths', 'Length'], ['textures', 'Texture'], ['features', 'Cut / styling'], ['finish', 'Finish'],
                  ['maintenance', 'Maintenance'], ['occasions', 'Occasion'], ['face_shapes', 'Face shape']],
    'Hair colour': [['families', 'Colour family'], ['undertones', 'Undertone'], ['technique', 'Technique']],
    'Makeup': [['subcategory', 'Type'], ['occasions', 'Occasion'], ['intensity', 'Intensity']],
    'Beard & grooming': [['maintenance', 'Maintenance'], ['occasions', 'Occasion'], ['face_shapes', 'Face shape']],
    'Nail art': [],
    'Overall beauty look': [['occasions', 'Occasion']]
  };

  const ICONS = {
    'Hairstyle': '<svg viewBox="0 0 24 24"><path d="M5 20c0-9 2-16 7-16s7 7 7 16"/><path d="M8 20c0-6 1.5-10 4-11"/></svg>',
    'Beard & grooming': '<svg viewBox="0 0 24 24"><path d="M6 9c0 7 3 11 6 11s6-4 6-11"/><path d="M9 14c1 1 2 1.5 3 1.5s2-.5 3-1.5"/></svg>',
    'Makeup': '<svg viewBox="0 0 24 24"><path d="M4 12c3-4 13-4 16 0-3 4-13 4-16 0z"/><path d="M4 12h16"/></svg>',
    'Nail art': '<svg viewBox="0 0 24 24"><path d="M8 21V9a4 4 0 018 0v12"/><path d="M8 13h8"/></svg>',
    'Overall beauty look': '<svg viewBox="0 0 24 24"><path d="M12 3l2.5 5 5.5.8-4 3.9.9 5.5L12 15.6 7.1 18.2 8 12.7 4 8.8 9.5 8z"/></svg>'
  };

  let all = [];
  let audience = 'women';
  let favourites = [];
  try {
    const a = localStorage.getItem(AUD_KEY);
    audience = ['women', 'men', 'all'].includes(a) ? a : 'women';
    favourites = JSON.parse(localStorage.getItem(FAV_KEY) || '[]');
  } catch (e) { /* storage unavailable */ }
  let browse = { category: 'Hairstyle', q: '', filters: {}, featured: false };
  let current = null;  // template open in detail

  function el(tag, cls, text) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }

  const cap = s => s ? s.charAt(0).toUpperCase() + s.slice(1) : s;
  const sentence = s => { s = (s || '').trim(); return s ? cap(s) + (/[.!?]$/.test(s) ? '' : '.') : ''; };

  /* Templates for everyone (makeup, nails) always show; others follow the Women / Men / All choice. */
  const inAudience = t => t.group === 'all' || audience === 'all' || t.group === audience;
  const visible = () => all.filter(inAudience);
  const categories = () => ORDER.filter(c => visible().some(t => t.category === c));
  const inCategory = c => visible().filter(t => t.category === c);
  const byId = id => all.find(t => t.id === id) || null;

  /* A reference photo, a colour swatch, or an icon tile when there's no photo yet. */
  function picture(t, cls) {
    if (t.image) {
      const wrap = el('div', cls + ' pic-wrap');
      const i = el('img');
      i.src = t.image;
      i.alt = t.name;
      i.loading = 'lazy';
      wrap.append(i, el('span', 'ref-badge', 'Reference'));
      return wrap;
    }
    if (t.hex) {
      const s = el('div', cls + ' swatch-tile');
      s.style.setProperty('--sw', t.hex);
      s.setAttribute('role', 'img');
      s.setAttribute('aria-label', t.name + ' colour swatch');
      return s;
    }
    const tile = el('div', cls + ' style-tile');
    tile.innerHTML = ICONS[t.category] || ICONS['Hairstyle'];
    tile.append(el('span', 'tile-note', 'No photo yet'));
    tile.setAttribute('role', 'img');
    tile.setAttribute('aria-label', t.name);
    return tile;
  }

  function isFav(id) { return favourites.includes(id); }

  function favButton(t) {
    const b = el('button', 'fav-btn');
    b.type = 'button';
    const set = () => {
      const on = isFav(t.id);
      b.classList.toggle('on', on);
      b.setAttribute('aria-pressed', on);
      b.setAttribute('aria-label', (on ? 'Remove ' : 'Save ') + t.name + (on ? ' from favourites' : ' to favourites'));
      b.innerHTML = '<svg viewBox="0 0 24 24"><path d="M12 20s-7-4.4-7-10a4 4 0 017-2.6A4 4 0 0119 10c0 5.6-7 10-7 10z"/></svg>';
    };
    set();
    b.onclick = e => { e.stopPropagation(); Styles.toggleFavourite(t.id); set(); };
    return b;
  }

  function tagList(t, n) {
    const row = el('div', 'tag-row');
    (t.tags || []).slice(0, n).forEach(tag => row.append(el('span', 'tag', tag)));
    return row;
  }

  /* Gallery card: picture, name, category, description, tags, favourite, selection state, "Try this style". */
  function card(t) {
    const c = el('article', 'tpl-card');
    const inLook = window.Generator && window.Generator.has(t);
    if (inLook) c.classList.add('selected');
    const pic = el('button', 'tpl-pic');
    pic.type = 'button';
    pic.setAttribute('aria-label', 'Open ' + t.name);
    pic.onclick = () => Styles.openDetail(t.id);
    pic.append(picture(t, 'tpl-img'));
    if (inLook) pic.append(el('span', 'in-look', '✓ In your look'));
    const body = el('div', 'tpl-body');
    const head = el('div', 'tpl-head');
    const name = el('button', 'tpl-name', t.name);
    name.type = 'button';
    name.onclick = () => Styles.openDetail(t.id);
    head.append(name, favButton(t));
    const try_ = el('button', 'btn btn-p btn-sm tpl-try', 'Try this style');
    try_.type = 'button';
    try_.onclick = () => Styles.tryOn(t.id);
    body.append(head, el('p', 'caption', SHORT[t.category] + (t.subcategory ? ' · ' + t.subcategory : '')),
                el('p', 'tpl-desc', t.description), tagList(t, 2), try_);
    c.append(pic, body);
    return c;
  }

  function scrollItem(t) {
    const item = el('button', 'scroll-item');
    item.type = 'button';
    item.onclick = () => Styles.openDetail(t.id);
    item.append(picture(t, 'scroll-img'), el('p', null, t.name), el('p', 'caption', SHORT[t.category]));
    return item;
  }

  function renderToggles() {
    document.querySelectorAll('.aud-toggle[data-kind="audience"]').forEach(group => {
      group.querySelectorAll('button').forEach(b => {
        const on = b.dataset.aud === audience;
        b.classList.toggle('active', on);
        b.setAttribute('aria-pressed', on);
      });
    });
  }

  function categoryCards(container, withCount) {
    if (!container) return;
    container.replaceChildren(...categories().map(c => {
      const btn = el('button', 'card card-click cat-card');
      btn.type = 'button';
      btn.onclick = () => Styles.openCategory(c);
      btn.append(el('h3', null, LABELS[c][0]),
                 el('p', 'caption mt-8', withCount ? inCategory(c).length + ' styles' : LABELS[c][1]));
      return btn;
    }));
  }

  function renderHome() {
    categoryCards($('home-cats'), true);
    const featured = visible().filter(t => t.featured);
    const row = $('home-featured');
    if (row) row.replaceChildren(...featured.slice(0, 10).map(scrollItem));
    const favs = favourites.map(byId).filter(Boolean);
    const favBox = $('home-favs-box');
    if (favBox) {
      favBox.style.display = favs.length ? '' : 'none';
      $('home-favs').replaceChildren(...favs.slice(0, 10).map(scrollItem));
    }
  }

  function values(items, key) {
    const set = new Set();
    items.forEach(t => [].concat(t[key] || []).forEach(v => v && set.add(v)));
    return [...set].sort();
  }

  function matches(t) {
    const q = browse.q.trim().toLowerCase();
    if (q && !(t.name.toLowerCase().includes(q) || (t.description || '').toLowerCase().includes(q) ||
               (t.tags || []).some(tag => tag.includes(q)))) return false;
    if (browse.featured && !t.featured) return false;
    return Object.entries(browse.filters).every(([k, v]) => [].concat(t[k] || []).includes(v));
  }

  function renderFilters(items) {
    const bar = $('filter-bar');
    const defs = FILTERS[browse.category] || [];
    bar.replaceChildren(...defs.map(([key, label]) => {
      const opts = values(items, key);
      if (opts.length < 2) return el('span');
      const s = el('select', 'filter-select');
      s.setAttribute('aria-label', label);
      s.append(Object.assign(el('option', null, label), { value: '' }));
      opts.forEach(o => s.append(Object.assign(el('option', null, cap(o)), { value: o })));
      s.value = browse.filters[key] || '';
      s.classList.toggle('on', !!browse.filters[key]);
      s.onchange = () => {
        if (s.value) browse.filters[key] = s.value; else delete browse.filters[key];
        renderList();
      };
      return s;
    }));
    const feat = el('button', 'chip' + (browse.featured ? ' active' : ''), 'Featured');
    feat.type = 'button';
    feat.setAttribute('aria-pressed', browse.featured);
    feat.onclick = () => { browse.featured = !browse.featured; renderList(); };
    bar.append(feat);

    const active = $('filter-active');
    const chips = Object.entries(browse.filters).map(([k, v]) => {
      const label = (defs.find(d => d[0] === k) || [k, k])[1];
      const b = el('button', 'chip active removable', label + ': ' + cap(v) + '  ×');
      b.type = 'button';
      b.setAttribute('aria-label', 'Remove filter ' + label + ' ' + v);
      b.onclick = () => { delete browse.filters[k]; renderList(); };
      return b;
    });
    if (browse.q) {
      const b = el('button', 'chip active removable', '“' + browse.q + '”  ×');
      b.type = 'button';
      b.onclick = () => { browse.q = ''; $('style-search').value = ''; renderList(); };
      chips.push(b);
    }
    if (chips.length) {
      const clear = el('button', 'btn-link', 'Clear all');
      clear.type = 'button';
      clear.onclick = () => { browse.filters = {}; browse.q = ''; browse.featured = false; $('style-search').value = ''; renderList(); };
      chips.push(clear);
    }
    active.replaceChildren(...chips);
    active.style.display = chips.length ? '' : 'none';
  }

  function renderList() {
    const grid = $('style-grid');
    if (!grid) return;
    if (!categories().includes(browse.category)) browse.category = categories()[0] || 'Hairstyle';
    $('style-title').textContent = LABELS[browse.category][0];
    const aud = $('list-aud');
    // Makeup and nail templates are for everyone, so the Women / Men switch isn't shown there.
    if (aud) aud.style.display = ['Makeup', 'Nail art'].includes(browse.category) ? 'none' : '';
    $('style-for-all').style.display = browse.category === 'Makeup' ? '' : 'none';
    const items = inCategory(browse.category);
    renderFilters(items);
    const shown = items.filter(matches);
    $('style-count').textContent = shown.length + (shown.length === 1 ? ' style' : ' styles');
    grid.replaceChildren(...shown.map(card));
    if (!shown.length) grid.append(el('p', 'caption', 'No styles match. Remove a filter to see more.'));
  }

  function related(t) {
    const tags = new Set(t.tags || []);
    return visible()
      .filter(o => o.category === t.category && o.id !== t.id)
      .map(o => [o, (o.tags || []).filter(x => tags.has(x)).length])
      .sort((a, b) => b[1] - a[1])
      .slice(0, 6).map(x => x[0]);
  }

  function metaRow(label, value) {
    if (!value || (Array.isArray(value) && !value.length)) return null;
    const r = el('div', 'meta-row');
    r.append(el('span', 'caption', label), el('span', null, Array.isArray(value) ? value.map(cap).join(', ') : cap(value)));
    return r;
  }

  function renderDetail() {
    const t = current;
    if (!t) return;
    const hero = $('detail-hero');
    hero.replaceChildren(picture(t, 'detail-tile'));
    const views = Object.entries(t.images || {}).filter(([, url]) => url);
    const thumbs = $('detail-views');
    thumbs.replaceChildren(...(views.length > 1 ? views : []).map(([view, url]) => {
      const b = el('button', 'view-thumb');
      b.type = 'button';
      b.setAttribute('aria-label', 'Show ' + view + ' view');
      const i = el('img');
      i.src = url; i.alt = t.name + ' ' + view;
      b.append(i, el('span', 'caption', cap(view)));
      b.onclick = () => { hero.querySelector('img').src = url; };
      return b;
    }));
    $('detail-title').textContent = t.name;
    $('detail-kind').textContent = LABELS[t.category][0] + (t.subcategory ? ' · ' + t.subcategory : '') +
      (t.group === 'all' ? ' · for everyone' : ' · ' + cap(t.group) + '’s');
    $('detail-desc').textContent = sentence(t.description);
    const meta = $('detail-meta');
    meta.replaceChildren(...[
      metaRow('Length', t.lengths),
      metaRow('Works with', t.textures && (t.textures.length >= 4 ? 'all hair textures' : t.textures.map(x => x + ' hair'))),
      metaRow('Finish', t.finish), metaRow('Maintenance', t.maintenance), metaRow('Occasion', t.occasions),
      metaRow('Often chosen for', t.face_shapes && t.face_shapes.length < 6 ? t.face_shapes.map(s => s + ' faces') : null),
      metaRow('Undertones', t.undertones), metaRow('Technique', t.technique), metaRow('Intensity', t.intensity)
    ].filter(Boolean));
    $('detail-tags').replaceChildren(...(t.tags || []).map(tag => el('span', 'tag', tag)));
    const parts = $('detail-parts');
    const items = (t.parts || []).map(byId).filter(Boolean);
    parts.style.display = items.length ? '' : 'none';
    $('detail-parts-list').replaceChildren(...items.map(scrollItem));
    $('detail-fav').replaceChildren(favButton(t));
    const add = $('detail-add');
    const inLook = window.Generator && window.Generator.has(t);
    add.textContent = inLook ? '✓ In your look' : 'Add to my look';
    add.disabled = !!inLook;
    const rel = related(t);
    $('detail-related-box').style.display = rel.length ? '' : 'none';
    $('detail-related').replaceChildren(...rel.map(scrollItem));
    $('detail-note').textContent = t.image
      ? 'The photo is a reference example, not a result. Your try-on keeps your own face.'
      : 'No reference photo yet: your try-on is created from this description.';
  }

  function renderHero() {
    // The hero's sample photos are women's styles; hide them for men until men's photos are added.
    const pics = document.querySelector('#screen-2 .hero-pics');
    if (pics) pics.style.display = audience === 'men' ? 'none' : '';
  }

  function renderFavourites() {
    const grid = $('fav-grid');
    if (!grid) return;
    const favs = favourites.map(byId).filter(Boolean);
    grid.replaceChildren(...favs.map(card));
    $('fav-empty').style.display = favs.length ? 'none' : '';
  }

  function renderAll() {
    renderToggles();
    renderHero();
    renderHome();
    categoryCards($('cat-list'), false);
    renderList();
    renderFavourites();
    if (current) renderDetail();
    if (window.Generator) window.Generator.render();
  }

  window.Styles = {
    async load() {
      try {
        const res = await fetch('/api/v1/styles');
        if (res.ok) all = await res.json();
      } catch (e) { console.warn('Could not load styles', e); }
      renderAll();
    },
    loaded: () => all.length > 0,
    audience: () => audience,
    setAudience(a) {
      if (!['women', 'men', 'all'].includes(a)) return;
      audience = a;
      try { localStorage.setItem(AUD_KEY, a); } catch (e) { /* storage unavailable */ }
      renderAll();
    },
    openCategory(c, opts) {
      if (browse.category !== c) browse = { category: c, q: '', filters: {}, featured: false };
      if (opts && opts.filters) browse.filters = Object.assign({}, opts.filters);
      $('style-search').value = browse.q;
      renderList();
      window.showScreen('screen-4');
    },
    search(q) { browse.q = q; renderList(); },
    openDetail(id) {
      current = byId(id);
      if (!current) return;
      renderDetail();
      window.showScreen('screen-5');
    },
    /* Add to the look and go to the generator. A complete look adds each of its templates. */
    tryOn(id) {
      Styles.addToLook(id);
      window.showScreen('screen-7');
    },
    addToLook(id) {
      const t = byId(id);
      if (!t) return;
      if (t.category === 'Overall beauty look') {
        window.Generator.clearLook();
        (t.parts || []).map(byId).filter(Boolean).forEach(p => window.Generator.setTemplate(p));
      } else {
        window.Generator.setTemplate(t);
      }
      renderList();
      if (current) renderDetail();
    },
    addCurrent() { if (current) Styles.addToLook(current.id); },
    tryCurrent() { if (current) Styles.tryOn(current.id); },
    toggleFavourite(id) {
      favourites = isFav(id) ? favourites.filter(x => x !== id) : favourites.concat(id);
      try { localStorage.setItem(FAV_KEY, JSON.stringify(favourites)); } catch (e) { /* storage unavailable */ }
      renderHome();
      renderFavourites();
    },
    openFavourites() { renderFavourites(); window.showScreen('screen-17'); },
    find: id => byId(id),
    findByName: name => all.find(t => t.name === name) || null,
    label: c => LABELS[c] ? LABELS[c][0] : c,
    short: c => SHORT[c] || c,
    picture,
    card,
    render: renderAll
  };
})();
