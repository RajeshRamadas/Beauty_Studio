/*
 * Salon map search.
 *
 * Two providers behind one UI:
 *   google  Google Maps JavaScript API + Places API (New). Used when the backend
 *           returns a key from /api/v1/client-config (GOOGLE_MAPS_API_KEY).
 *   osm     Leaflet + OpenStreetMap tiles, Nominatim place search and the
 *           Overpass API. Free, no key. Used when no Google key is configured
 *           or if Google fails to load.
 *
 * Data from either service is untrusted: it is only ever written with textContent,
 * and links are restricted to http(s)/tel.
 */
(function () {
  const DEFAULT_RADIUS_M = 3000;
  const MAX_RADIUS_M = 8000;
  const $ = id => document.getElementById(id);

  let provider = null;        // active provider object
  let startPromise = null;    // resolves once a provider is ready
  let salons = [], filter = 'All', origin = null, handles = {};

  /* ── Helpers ─────────────────────────────────────── */
  function setStatus(text, kind) {
    const el = $('salon-status');
    el.textContent = text || '';
    el.className = 'msg' + (kind ? ' ' + kind : '');
    el.style.display = text ? 'block' : 'none';
  }

  function distanceKm(a, b) {
    const R = 6371, toRad = d => d * Math.PI / 180;
    const dLat = toRad(b.lat - a.lat), dLon = toRad(b.lng - a.lng);
    const h = Math.sin(dLat / 2) ** 2 + Math.cos(toRad(a.lat)) * Math.cos(toRad(b.lat)) * Math.sin(dLon / 2) ** 2;
    return 2 * R * Math.asin(Math.sqrt(h));
  }

  function safeUrl(url) {
    if (!url) return null;
    const u = /^https?:\/\//i.test(url) ? url : 'https://' + url;
    try { const p = new URL(u); return (p.protocol === 'https:' || p.protocol === 'http:') ? p.href : null; } catch (e) { return null; }
  }

  function loadScript(src) {
    return new Promise((resolve, reject) => {
      const s = document.createElement('script');
      s.src = src; s.async = true; s.crossOrigin = 'anonymous';
      s.onload = resolve; s.onerror = () => reject(new Error('Could not load ' + src));
      document.head.appendChild(s);
    });
  }

  function pinElement(cls) {
    const d = document.createElement('div');
    d.className = cls;
    d.appendChild(document.createElement('span'));
    return d;
  }

  function popupNode(s) {
    const pop = document.createElement('div');
    pop.className = 'map-pop';
    const b = document.createElement('b'); b.textContent = s.name;
    const t = document.createElement('div'); t.textContent = s.type + ' · ' + s.km.toFixed(1) + ' km';
    pop.append(b, t);
    return pop;
  }

  /* ── OpenStreetMap provider ──────────────────────── */
  const osm = {
    name: 'osm',
    credit: 'Salon data from OpenStreetMap contributors. Check opening hours with the salon before visiting.',
    map: null, layer: null, you: null,

    async init(el) {
      if (typeof L === 'undefined') {
        const css = document.createElement('link');
        css.rel = 'stylesheet';
        css.href = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css';
        document.head.appendChild(css);
        await loadScript('https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js');
      }
      this.map = L.map(el, { zoomControl: false }).setView([20, 0], 2);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19, attribution: '&copy; OpenStreetMap contributors' }).addTo(this.map);
      L.control.zoom({ position: 'bottomright' }).addTo(this.map);
      this.layer = L.layerGroup().addTo(this.map);
      this.map.on('dragstart', showAreaButton);
    },
    resize() { this.map.invalidateSize(); },
    center() { const c = this.map.getCenter(); return { lat: c.lat, lng: c.lng }; },
    viewRadius() { return this.map.getCenter().distanceTo(this.map.getBounds().getNorthEast()); },
    setView(p, zoom) { this.map.setView([p.lat, p.lng], zoom, { animate: false }); },
    clear() { this.layer.clearLayers(); },
    addMarker(s, onClick) {
      const icon = L.divIcon({ className: 'salon-pin', html: '<span></span>', iconSize: [18, 18], iconAnchor: [9, 9] });
      const m = L.marker([s.pos.lat, s.pos.lng], { icon, title: s.name }).addTo(this.layer);
      m.bindPopup(popupNode(s));
      m.on('click', onClick);
      return m;
    },
    focus(m) { this.map.setView(m.getLatLng(), Math.max(this.map.getZoom(), 15)); m.openPopup(); },
    fit(points) {
      this.resize();
      if (points.length > 1) this.map.fitBounds(points.map(p => [p.lat, p.lng]), { padding: [32, 32], maxZoom: 16, animate: false });
      else this.setView(points[0], 15);
    },
    setYou(p) {
      if (this.you) this.you.remove();
      this.you = L.marker([p.lat, p.lng], { icon: L.divIcon({ className: 'you-pin', html: '<span></span>', iconSize: [16, 16], iconAnchor: [8, 8] }), interactive: false }).addTo(this.map);
    },
    clearYou() { if (this.you) { this.you.remove(); this.you = null; } },

    async geocode(q) {
      const res = await fetch('https://nominatim.openstreetmap.org/search?format=jsonv2&limit=1&q=' + encodeURIComponent(q), { headers: { 'Accept': 'application/json' } });
      const hits = res.ok ? await res.json() : [];
      return hits.length ? { lat: parseFloat(hits[0].lat), lng: parseFloat(hits[0].lon) } : null;
    },

    async nearby(c, radius) {
      const r = Math.round(radius), at = `(around:${r},${c.lat},${c.lng})`;
      const q = `[out:json][timeout:25];(nwr["shop"="hairdresser"]${at};nwr["shop"="beauty"]${at};nwr["beauty"="nails"]${at};);out center tags 60;`;
      const res = await fetch('https://overpass-api.de/api/interpreter', { method: 'POST', body: 'data=' + encodeURIComponent(q), headers: { 'Content-Type': 'application/x-www-form-urlencoded' } });
      if (!res.ok) throw new Error('Salon search is busy. Try again in a moment.');
      const data = await res.json();
      return (data.elements || []).map(el => {
        const pos = el.type === 'node' ? { lat: el.lat, lng: el.lon } : (el.center ? { lat: el.center.lat, lng: el.center.lon } : null);
        const t = el.tags || {};
        if (!pos || !t.name) return null;
        const street = [t['addr:housenumber'], t['addr:street']].filter(Boolean).join(' ');
        return {
          id: el.type + el.id, name: t.name, pos,
          type: t.shop === 'hairdresser' ? 'Hair' : (t.beauty === 'nails' || /nail/i.test(t.name) ? 'Nails' : 'Beauty'),
          address: [street, t['addr:city'] || t['addr:suburb']].filter(Boolean).join(', '),
          phone: t.phone || t['contact:phone'] || null,
          website: safeUrl(t.website || t['contact:website']),
          hours: t.opening_hours || null,
          rating: null, ratingCount: null, mapsUrl: null
        };
      }).filter(Boolean);
    },

    directions(s) { return 'https://www.google.com/maps/dir/?api=1&destination=' + s.pos.lat + ',' + s.pos.lng; }
  };

  /* ── Google provider ─────────────────────────────── */
  const FIELDS = ['id', 'displayName', 'location', 'formattedAddress', 'primaryType', 'businessStatus',
    'rating', 'userRatingCount', 'nationalPhoneNumber', 'websiteURI', 'googleMapsURI', 'regularOpeningHours'];

  function googleType(t) {
    if (t === 'hair_salon' || t === 'hair_care' || t === 'barber_shop') return 'Hair';
    if (t === 'nail_salon') return 'Nails';
    return 'Beauty';
  }

  function todaysHours(place) {
    const days = place.regularOpeningHours && place.regularOpeningHours.weekdayDescriptions;
    if (!days || days.length !== 7) return null;
    return days[(new Date().getDay() + 6) % 7]; // weekdayDescriptions starts on Monday
  }

  const google_ = {
    name: 'google',
    credit: 'Salon data from Google. Check opening hours with the salon before visiting.',
    map: null, info: null, you: null, lib: {},

    async init(el, cfg) {
      await new Promise((resolve, reject) => {
        window.__glowMapsReady = resolve;
        window.gm_authFailure = () => reject(new Error('Google rejected the API key'));
        loadScript('https://maps.googleapis.com/maps/api/js?key=' + encodeURIComponent(cfg.google_api_key) +
          '&v=weekly&loading=async&callback=__glowMapsReady')
          .catch(() => reject(new Error('the Google Maps script could not be downloaded; check your connection or ad blocker')));
      });
      const [{ Map, InfoWindow }, { Place, SearchNearbyRankPreference }, { AdvancedMarkerElement }] = await Promise.all([
        google.maps.importLibrary('maps'), google.maps.importLibrary('places'), google.maps.importLibrary('marker')
      ]);
      this.lib = { Place, SearchNearbyRankPreference, AdvancedMarkerElement };
      this.map = new Map(el, {
        center: { lat: 20, lng: 0 }, zoom: 2, mapId: cfg.google_map_id || 'DEMO_MAP_ID',
        colorScheme: 'DARK', disableDefaultUI: true, zoomControl: true, clickableIcons: false, gestureHandling: 'greedy'
      });
      this.info = new InfoWindow();
      this.map.addListener('dragstart', showAreaButton);
    },
    resize() { /* Google maps resize themselves */ },
    center() { const c = this.map.getCenter(); return { lat: c.lat(), lng: c.lng() }; },
    viewRadius() {
      const ne = this.map.getBounds() && this.map.getBounds().getNorthEast();
      return ne ? distanceKm(this.center(), { lat: ne.lat(), lng: ne.lng() }) * 1000 : DEFAULT_RADIUS_M;
    },
    setView(p, zoom) { this.map.setCenter(p); this.map.setZoom(zoom); },
    clear() { Object.values(handles).forEach(m => { m.map = null; }); this.info.close(); },
    addMarker(s, onClick) {
      const m = new this.lib.AdvancedMarkerElement({ map: this.map, position: s.pos, title: s.name, content: pinElement('salon-pin') });
      m.addListener('click', onClick);
      m._salon = s;
      return m;
    },
    focus(m) {
      this.map.panTo(m.position);
      if (this.map.getZoom() < 15) this.map.setZoom(15);
      this.info.setContent(popupNode(m._salon));
      this.info.open({ map: this.map, anchor: m });
    },
    fit(points) {
      if (points.length > 1) {
        const b = new google.maps.LatLngBounds();
        points.forEach(p => b.extend(p));
        this.map.fitBounds(b, 32);
        google.maps.event.addListenerOnce(this.map, 'idle', () => { if (this.map.getZoom() > 16) this.map.setZoom(16); });
      } else this.setView(points[0], 15);
    },
    setYou(p) {
      this.clearYou();
      this.you = new this.lib.AdvancedMarkerElement({ map: this.map, position: p, content: pinElement('you-pin') });
    },
    clearYou() { if (this.you) { this.you.map = null; this.you = null; } },

    async geocode(q) {
      const { places } = await this.lib.Place.searchByText({ textQuery: q, fields: ['location'], maxResultCount: 1 });
      if (!places || !places.length) return null;
      return { lat: places[0].location.lat(), lng: places[0].location.lng() };
    },

    async nearby(c, radius) {
      const { places } = await this.lib.Place.searchNearby({
        fields: FIELDS,
        locationRestriction: { center: c, radius: Math.min(radius, 50000) },
        includedPrimaryTypes: ['hair_salon', 'beauty_salon', 'nail_salon', 'barber_shop'],
        maxResultCount: 20,
        rankPreference: this.lib.SearchNearbyRankPreference.DISTANCE
      });
      return (places || []).filter(p => p.businessStatus !== 'CLOSED_PERMANENTLY').map(p => ({
        id: p.id, name: p.displayName || 'Salon',
        pos: { lat: p.location.lat(), lng: p.location.lng() },
        type: googleType(p.primaryType),
        address: p.formattedAddress || '',
        phone: p.nationalPhoneNumber || null,
        website: safeUrl(p.websiteURI),
        hours: todaysHours(p),
        rating: typeof p.rating === 'number' ? p.rating : null,
        ratingCount: p.userRatingCount || null,
        mapsUrl: safeUrl(p.googleMapsURI)
      }));
    },

    directions(s) {
      return 'https://www.google.com/maps/dir/?api=1&destination=' + s.pos.lat + ',' + s.pos.lng + '&destination_place_id=' + encodeURIComponent(s.id);
    }
  };

  /* ── Start-up: pick a provider ───────────────────── */
  const GOOGLE_KEY_HELP = 'Google Maps rejected the API key. In Google Cloud, check that billing is on, ' +
    'Maps JavaScript API and Places API (New) are enabled, and the key allows this website (' + location.origin + '/*).';

  function freshMapElement() {
    const inner = document.createElement('div');
    inner.style.cssText = 'width:100%;height:100%;';
    $('salon-map').replaceChildren(inner);
    return inner;
  }

  async function useOsm(reason) {
    provider = null;
    await osm.init(freshMapElement());
    provider = osm;
    $('salon-credit').textContent = provider.credit;
    if (reason) setStatus(reason, 'err');
  }

  async function start() {
    let cfg = {};
    try {
      const r = await fetch('/api/v1/client-config');
      if (r.ok) cfg = (await r.json()).maps || {};
    } catch (e) { /* static hosting or offline: use OSM */ }

    if (cfg.provider === 'google' && cfg.google_api_key) {
      try {
        await google_.init(freshMapElement(), cfg);
        provider = google_;
        // A bad or restricted key can be reported after the map has loaded.
        window.gm_authFailure = () => {
          console.warn('Google Maps rejected the API key; switching to OpenStreetMap.');
          salons = []; origin = null;
          $('salon-list').replaceChildren();
          startPromise = useOsm(GOOGLE_KEY_HELP + ' Showing OpenStreetMap instead; search again to see salons.');
        };
      } catch (e) {
        console.warn('Google Maps unavailable, using OpenStreetMap instead.', e);
        await useOsm(/rejected/.test(e.message) ? GOOGLE_KEY_HELP + ' Showing OpenStreetMap instead.'
          : 'Google Maps could not load (' + e.message + '). Showing OpenStreetMap instead.');
        return;
      }
    }
    if (!provider) { await useOsm(); return; }
    $('salon-credit').textContent = provider.credit;
  }

  function ready() {
    if (!startPromise) {
      startPromise = start().catch(e => {
        startPromise = null;
        setStatus('The map could not load. Check your internet connection and try again.', 'err');
        throw e;
      });
    }
    return startPromise;
  }

  /* ── Search + render ─────────────────────────────── */
  function showAreaButton() { if (origin) $('salon-area-btn').style.display = 'inline-flex'; }

  async function searchAt(c, radius) {
    origin = c;
    $('salon-area-btn').style.display = 'none';
    $('salon-list').replaceChildren();
    $('salon-count').textContent = '';
    setStatus('Finding salons nearby…');
    try {
      const found = await provider.nearby(c, Math.min(radius || DEFAULT_RADIUS_M, MAX_RADIUS_M));
      const seen = new Set();
      salons = found.filter(s => {
        const key = s.name + '|' + s.pos.lat.toFixed(4) + '|' + s.pos.lng.toFixed(4);
        if (seen.has(key)) return false;
        seen.add(key);
        s.km = distanceKm(c, s.pos);
        return true;
      }).sort((a, b) => a.km - b.km);
      render();
    } catch (e) {
      console.warn('Salon search failed', e);
      const msg = provider.name === 'google'
        ? 'Google salon search failed. Check that Places API (New) is enabled for your key. (' + (e.message || e) + ')'
        : (e.message || 'Could not load salons. Try again in a moment.');
      setStatus(msg, 'err');
    }
  }

  function render() {
    const list = $('salon-list');
    const shown = salons.filter(s => filter === 'All' || s.type === filter);
    provider.clear();
    handles = {};
    list.replaceChildren();
    $('salon-count').textContent = shown.length ? shown.length + ' found' : '';

    if (!shown.length) {
      setStatus(salons.length ? 'No ' + filter.toLowerCase() + ' salons here. Try another filter.' : 'No salons found here. Try a wider area or another place.');
      return;
    }
    setStatus('');
    shown.forEach(s => {
      handles[s.id] = provider.addMarker(s, () => highlight(s.id, true));
      list.appendChild(row(s));
    });
    provider.fit(shown.map(s => s.pos).concat(origin ? [origin] : []));
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
    meta.append(tag);
    if (s.rating != null) {
      const r = document.createElement('span'); r.className = 'salon-rating';
      r.textContent = ' · ★ ' + s.rating.toFixed(1) + (s.ratingCount ? ' (' + s.ratingCount.toLocaleString() + ')' : '');
      meta.append(r);
    }
    meta.append(document.createTextNode(' · ' + s.km.toFixed(1) + ' km'));
    head.append(name, meta);
    if (s.address) { const a = document.createElement('div'); a.className = 'salon-meta'; a.textContent = s.address; head.append(a); }
    if (s.hours) { const h = document.createElement('div'); h.className = 'salon-meta'; h.textContent = s.hours; head.append(h); }

    const actions = document.createElement('div');
    actions.className = 'salon-actions';
    actions.append(link('Directions', provider.directions(s), true));
    if (s.phone) actions.append(link('Call', 'tel:' + s.phone.split(';')[0].replace(/[^\d+]/g, ''), false));
    if (s.mapsUrl) actions.append(link('Reviews', s.mapsUrl, false));
    else if (s.website) actions.append(link('Website', s.website, false));
    if (s.mapsUrl && s.website) actions.append(link('Website', s.website, false));

    card.append(head, actions);
    return card;
  }

  function highlight(id, fromMap) {
    document.querySelectorAll('.salon-row.active').forEach(r => r.classList.remove('active'));
    const r = $('salon-' + id);
    if (r) { r.classList.add('active'); if (fromMap) r.scrollIntoView({ behavior: 'smooth', block: 'nearest' }); }
    if (handles[id]) provider.focus(handles[id]);
  }

  /* ── Public API used by index.html ───────────────── */
  window.Salons = {
    open() { ready().then(() => provider.resize()).catch(() => {}); },

    async useMyLocation() {
      try { await ready(); } catch (e) { return; }
      if (!navigator.geolocation) { setStatus('Location is not available on this device. Search for a place instead.', 'err'); return; }
      setStatus('Getting your location…');
      navigator.geolocation.getCurrentPosition(
        p => {
          const c = { lat: p.coords.latitude, lng: p.coords.longitude };
          provider.setYou(c);
          provider.setView(c, 14);
          searchAt(c);
        },
        () => setStatus('Location permission was denied. Search for a place instead.', 'err'),
        { enableHighAccuracy: false, timeout: 10000, maximumAge: 300000 }
      );
    },

    async searchPlace(ev) {
      if (ev) ev.preventDefault();
      const q = $('salon-query').value.trim();
      if (!q) { $('salon-query').focus(); return; }
      try { await ready(); } catch (e) { return; }
      setStatus('Searching for “' + q + '”…');
      try {
        const c = await provider.geocode(q);
        if (!c) { setStatus('We couldn’t find that place. Try a city, area or postcode.', 'err'); return; }
        provider.clearYou();
        provider.setView(c, 14);
        searchAt(c);
      } catch (e) {
        console.warn('Place search failed', e);
        setStatus(provider.name === 'google'
          ? 'Google place search failed. Check that Places API (New) is enabled for your key. (' + (e.message || e) + ')'
          : 'Place search failed. Check your connection and try again.', 'err');
      }
    },

    searchThisArea() { searchAt(provider.center(), provider.viewRadius()); },

    setFilter(value, btn) {
      filter = value;
      document.querySelectorAll('#salon-filters .chip').forEach(c => { c.classList.toggle('active', c === btn); c.setAttribute('aria-pressed', c === btn); });
      if (salons.length) render();
    },

    provider() { return provider ? provider.name : null; }
  };
})();
