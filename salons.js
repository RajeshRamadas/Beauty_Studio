/*
 * Salon map search: real salons from OpenStreetMap.
 * - Map: Leaflet + OpenStreetMap tiles (no API key).
 * - Place search: Nominatim geocoding.
 * - Salons: Overpass API (shop=hairdresser, shop=beauty, beauty=nails).
 * Data from these services is untrusted: it is only ever written with textContent.
 */
(function () {
  const OVERPASS_URL = 'https://overpass-api.de/api/interpreter';
  const NOMINATIM_URL = 'https://nominatim.openstreetmap.org/search';
  const DEFAULT_RADIUS_M = 3000;
  const MAX_RADIUS_M = 8000;
  const MAX_RESULTS = 60;

  let map = null, markerLayer = null, youMarker = null, autoMove = false;
  let salons = [], filter = 'All', origin = null, markersById = {};

  const $ = id => document.getElementById(id);

  function setStatus(text, kind) {
    const el = $('salon-status');
    el.textContent = text || '';
    el.className = 'msg' + (kind ? ' ' + kind : '');
    el.style.display = text ? 'block' : 'none';
  }

  function ensureMap() {
    if (map) { setTimeout(() => map.invalidateSize(), 50); return true; }
    if (typeof L === 'undefined') { setStatus('The map could not load. Check your internet connection.', 'err'); return false; }
    map = L.map('salon-map', { zoomControl: false, attributionControl: true }).setView([20, 0], 2);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);
    L.control.zoom({ position: 'bottomright' }).addTo(map);
    markerLayer = L.layerGroup().addTo(map);
    // Offer "Search this area" only after the user pans or zooms the map themselves.
    map.on('movestart', () => {
      if (!autoMove && origin) $('salon-area-btn').style.display = 'inline-flex';
    });
    map.on('moveend', () => { autoMove = false; });
    setTimeout(() => map.invalidateSize(), 50);
    return true;
  }

  function salonType(tags) {
    if (tags.shop === 'hairdresser') return 'Hair';
    if (tags.beauty === 'nails' || /nail/i.test(tags.name || '')) return 'Nails';
    return 'Beauty';
  }

  function distanceKm(a, b) {
    const R = 6371, toRad = d => d * Math.PI / 180;
    const dLat = toRad(b.lat - a.lat), dLon = toRad(b.lng - a.lng);
    const h = Math.sin(dLat / 2) ** 2 + Math.cos(toRad(a.lat)) * Math.cos(toRad(b.lat)) * Math.sin(dLon / 2) ** 2;
    return 2 * R * Math.asin(Math.sqrt(h));
  }

  function address(tags) {
    const street = [tags['addr:housenumber'], tags['addr:street']].filter(Boolean).join(' ');
    return [street, tags['addr:city'] || tags['addr:suburb']].filter(Boolean).join(', ');
  }

  function safeUrl(url) {
    if (!url) return null;
    const u = /^https?:\/\//i.test(url) ? url : 'https://' + url;
    try { const p = new URL(u); return (p.protocol === 'https:' || p.protocol === 'http:') ? p.href : null; } catch (e) { return null; }
  }

  async function searchAt(lat, lng, radius) {
    origin = L.latLng(lat, lng);
    $('salon-area-btn').style.display = 'none';
    setStatus('Finding salons nearby…');
    $('salon-list').replaceChildren();
    const r = Math.round(Math.min(radius || DEFAULT_RADIUS_M, MAX_RADIUS_M));
    const q = `[out:json][timeout:25];(nwr["shop"="hairdresser"](around:${r},${lat},${lng});nwr["shop"="beauty"](around:${r},${lat},${lng});nwr["beauty"="nails"](around:${r},${lat},${lng}););out center tags ${MAX_RESULTS};`;
    try {
      const res = await fetch(OVERPASS_URL, { method: 'POST', body: 'data=' + encodeURIComponent(q), headers: { 'Content-Type': 'application/x-www-form-urlencoded' } });
      if (!res.ok) throw new Error('Salon search is busy. Try again in a moment.');
      const data = await res.json();
      const seen = new Set();
      salons = (data.elements || []).map(el => {
        const pos = el.type === 'node' ? { lat: el.lat, lng: el.lon } : (el.center ? { lat: el.center.lat, lng: el.center.lon } : null);
        const tags = el.tags || {};
        if (!pos || !tags.name) return null;
        const key = tags.name + '|' + pos.lat.toFixed(4) + '|' + pos.lng.toFixed(4);
        if (seen.has(key)) return null;
        seen.add(key);
        return {
          id: el.type + el.id, name: tags.name, type: salonType(tags), pos,
          km: distanceKm({ lat, lng }, pos), address: address(tags),
          phone: tags.phone || tags['contact:phone'] || null,
          website: safeUrl(tags.website || tags['contact:website']),
          hours: tags.opening_hours || null
        };
      }).filter(Boolean).sort((a, b) => a.km - b.km);
      render();
    } catch (e) {
      setStatus(e.message || 'Could not load salons.', 'err');
    }
  }

  function render() {
    const list = $('salon-list');
    const shown = salons.filter(s => filter === 'All' || s.type === filter);
    markerLayer.clearLayers();
    markersById = {};
    list.replaceChildren();
    $('salon-count').textContent = shown.length ? shown.length + ' found' : '';

    if (!shown.length) {
      setStatus(salons.length ? 'No ' + filter.toLowerCase() + ' salons here. Try another filter.' : 'No salons found here. Try a wider area or another place.');
      return;
    }
    setStatus('');

    const bounds = [];
    shown.forEach(s => {
      const icon = L.divIcon({ className: 'salon-pin', html: '<span></span>', iconSize: [18, 18], iconAnchor: [9, 9] });
      const m = L.marker([s.pos.lat, s.pos.lng], { icon, title: s.name }).addTo(markerLayer);
      const pop = document.createElement('div');
      const b = document.createElement('b'); b.textContent = s.name;
      const t = document.createElement('div'); t.textContent = s.type + ' · ' + s.km.toFixed(1) + ' km';
      pop.append(b, t);
      m.bindPopup(pop);
      m.on('click', () => highlight(s.id, true));
      markersById[s.id] = m;
      bounds.push([s.pos.lat, s.pos.lng]);
      list.appendChild(row(s));
    });
    if (origin) bounds.push([origin.lat, origin.lng]);
    map.invalidateSize();
    autoMove = true;
    if (bounds.length > 1) map.fitBounds(bounds, { padding: [32, 32], maxZoom: 16, animate: false });
    else map.setView(bounds[0], 15, { animate: false });
    autoMove = false;
  }

  function link(text, href, primary) {
    const a = document.createElement('a');
    a.className = 'btn btn-sm ' + (primary ? 'btn-p' : 'btn-s');
    a.textContent = text;
    a.href = href;
    if (/^https?:/.test(href)) { a.target = '_blank'; a.rel = 'noopener noreferrer'; }
    return a;
  }

  function row(s) {
    const card = document.createElement('div');
    card.className = 'salon-row';
    card.id = 'salon-' + s.id;

    const head = document.createElement('button');
    head.className = 'salon-head';
    head.type = 'button';
    head.onclick = () => highlight(s.id, false);
    const name = document.createElement('div'); name.className = 'salon-name'; name.textContent = s.name;
    const meta = document.createElement('div'); meta.className = 'salon-meta';
    const tag = document.createElement('b'); tag.textContent = s.type;
    meta.append(tag, document.createTextNode(' · ' + s.km.toFixed(1) + ' km' + (s.address ? ' · ' + s.address : '')));
    head.append(name, meta);
    if (s.hours) { const h = document.createElement('div'); h.className = 'salon-meta'; h.textContent = s.hours; head.append(h); }

    const actions = document.createElement('div');
    actions.className = 'salon-actions';
    actions.append(link('Directions', 'https://www.google.com/maps/dir/?api=1&destination=' + s.pos.lat + ',' + s.pos.lng, true));
    if (s.phone) actions.append(link('Call', 'tel:' + s.phone.split(';')[0].replace(/[^\d+]/g, ''), false));
    if (s.website) actions.append(link('Website', s.website, false));

    card.append(head, actions);
    return card;
  }

  function highlight(id, scrollList) {
    document.querySelectorAll('.salon-row.active').forEach(r => r.classList.remove('active'));
    const r = $('salon-' + id);
    if (r) { r.classList.add('active'); if (scrollList) r.scrollIntoView({ behavior: 'smooth', block: 'nearest' }); }
    const m = markersById[id];
    if (m && !scrollList) { map.setView(m.getLatLng(), Math.max(map.getZoom(), 15)); m.openPopup(); }
  }

  function setYou(lat, lng) {
    if (youMarker) youMarker.remove();
    youMarker = L.marker([lat, lng], { icon: L.divIcon({ className: 'you-pin', html: '<span></span>', iconSize: [16, 16], iconAnchor: [8, 8] }), title: 'You', interactive: false }).addTo(map);
  }

  window.Salons = {
    open() { ensureMap(); },

    useMyLocation() {
      if (!ensureMap()) return;
      if (!navigator.geolocation) { setStatus('Location is not available on this device. Search for a place instead.', 'err'); return; }
      setStatus('Getting your location…');
      navigator.geolocation.getCurrentPosition(
        p => { setYou(p.coords.latitude, p.coords.longitude); searchAt(p.coords.latitude, p.coords.longitude); },
        () => setStatus('Location permission was denied. Search for a place instead.', 'err'),
        { enableHighAccuracy: false, timeout: 10000, maximumAge: 300000 }
      );
    },

    async searchPlace(ev) {
      if (ev) ev.preventDefault();
      if (!ensureMap()) return;
      const q = $('salon-query').value.trim();
      if (!q) { $('salon-query').focus(); return; }
      setStatus('Searching for “' + q + '”…');
      try {
        const res = await fetch(NOMINATIM_URL + '?format=jsonv2&limit=1&q=' + encodeURIComponent(q), { headers: { 'Accept': 'application/json' } });
        const hits = res.ok ? await res.json() : [];
        if (!hits.length) { setStatus('We couldn’t find that place. Try a city, area or postcode.', 'err'); return; }
        const lat = parseFloat(hits[0].lat), lng = parseFloat(hits[0].lon);
        if (youMarker) { youMarker.remove(); youMarker = null; }
        autoMove = true;
        map.setView([lat, lng], 14, { animate: false });
        autoMove = false;
        searchAt(lat, lng);
      } catch (e) {
        setStatus('Place search failed. Check your connection and try again.', 'err');
      }
    },

    searchThisArea() {
      const c = map.getCenter();
      const b = map.getBounds();
      searchAt(c.lat, c.lng, c.distanceTo(b.getNorthEast()));
    },

    setFilter(value, btn) {
      filter = value;
      document.querySelectorAll('#salon-filters .chip').forEach(c => { c.classList.toggle('active', c === btn); c.setAttribute('aria-pressed', c === btn); });
      if (salons.length) render();
    }
  };
})();
