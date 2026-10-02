/*
 * Shop: catalogue from shop-data.js, category filter, bag with quantities.
 * The bag is kept in localStorage on this device only.
 * Payments are not connected yet, so checkout says so instead of taking an order.
 */
(function () {
  const STORE_KEY = 'glow_bag_v1';
  const data = window.GLOW_SHOP || { currency: '$', categories: ['All'], products: [] };
  const byId = Object.fromEntries(data.products.map(p => [p.id, p]));
  let category = 'All';
  let bag = load();

  const $ = id => document.getElementById(id);
  const money = n => data.currency + n.toFixed(2);

  function load() {
    try {
      const raw = JSON.parse(localStorage.getItem(STORE_KEY) || '{}');
      return Object.fromEntries(Object.entries(raw).filter(([id, q]) => byId[id] && q > 0));
    } catch (e) { return {}; }
  }
  function save() { try { localStorage.setItem(STORE_KEY, JSON.stringify(bag)); } catch (e) { /* storage unavailable */ } }

  const count = () => Object.values(bag).reduce((a, b) => a + b, 0);
  const subtotal = () => Object.entries(bag).reduce((sum, [id, q]) => sum + byId[id].price * q, 0);

  function el(tag, cls, text) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }

  function thumb(p, cls) {
    if (p.image) { const i = el('img', cls); i.src = p.image; i.alt = p.name; return i; }
    const t = el('div', cls + ' prod-tile');
    t.dataset.cat = p.category;
    t.append(el('span', null, p.category));
    return t;
  }

  function stepper(p) {
    const q = bag[p.id] || 0;
    if (!q) {
      const b = el('button', 'prod-add', 'Add to bag');
      b.type = 'button';
      b.onclick = () => Shop.add(p.id, 1);
      return b;
    }
    const w = el('div', 'stepper');
    const minus = el('button', null, '−'); minus.type = 'button'; minus.setAttribute('aria-label', 'Remove one ' + p.name); minus.onclick = () => Shop.add(p.id, -1);
    const plus = el('button', null, '+'); plus.type = 'button'; plus.setAttribute('aria-label', 'Add one more ' + p.name); plus.onclick = () => Shop.add(p.id, 1);
    w.append(minus, el('span', null, String(q)), plus);
    return w;
  }

  function card(p) {
    const c = el('div', 'prod-card');
    const body = el('div', 'prod-card-body');
    body.append(el('h3', 'mb-4', p.name), el('p', 'caption', p.brand), el('div', 'prod-price', money(p.price)), stepper(p));
    c.append(thumb(p, 'prod-img'), body);
    return c;
  }

  function renderBadges() {
    const n = count();
    document.querySelectorAll('.bag-count').forEach(b => { b.textContent = n; b.style.display = n ? 'inline-flex' : 'none'; });
  }

  function renderShop() {
    const chips = $('shop-filters');
    chips.replaceChildren(...data.categories.map(cat => {
      const b = el('button', 'chip' + (cat === category ? ' active' : ''), cat);
      b.type = 'button';
      b.setAttribute('aria-pressed', cat === category);
      b.onclick = () => { category = cat; renderShop(); };
      return b;
    }));
    const items = data.products.filter(p => category === 'All' || p.category === category);
    $('shop-grid').replaceChildren(...items.map(card));
    renderBadges();
  }

  function renderBag() {
    const list = $('bag-list');
    const ids = Object.keys(bag);
    $('bag-empty').style.display = ids.length ? 'none' : 'block';
    $('bag-summary').style.display = ids.length ? 'block' : 'none';
    $('bag-msg').style.display = 'none';
    list.replaceChildren(...ids.map(id => {
      const p = byId[id];
      const row = el('div', 'bag-row');
      const info = el('div', 'bag-info');
      info.append(el('div', 'salon-name', p.name), el('div', 'caption', p.brand + ' · ' + money(p.price)));
      const remove = el('button', 'btn-link', 'Remove');
      remove.type = 'button';
      remove.onclick = () => Shop.add(id, -bag[id]);
      info.append(remove);
      const right = el('div', 'bag-right');
      right.append(el('div', 'prod-price', money(p.price * bag[id])), stepper(p));
      row.append(thumb(p, 'bag-img'), info, right);
      return row;
    }));
    $('bag-subtotal').textContent = money(subtotal());
    renderBadges();
  }

  function renderLook() {
    const box = $('shop-look');
    if (!box) return;
    const style = ($('style-name') && $('style-name').value.trim()) || '';
    const matches = data.products.filter(p => (p.forStyles || []).includes(style)).slice(0, 4);
    box.style.display = matches.length ? 'block' : 'none';
    $('shop-look-grid').replaceChildren(...matches.map(card));
  }

  window.Shop = {
    add(id, delta) {
      bag[id] = Math.max(0, (bag[id] || 0) + delta);
      if (!bag[id]) delete bag[id];
      save();
      renderShop();
      renderBag();
      renderLook();
    },
    openShop() { renderShop(); },
    openBag() { renderBag(); },
    showLook() { renderLook(); },
    checkout() {
      const m = $('bag-msg');
      m.className = 'msg';
      m.textContent = 'Online payment isn’t connected yet, so orders can’t be placed in the app. Your bag is saved on this device.';
      m.style.display = 'block';
    },
    init() { renderBadges(); }
  };
})();
