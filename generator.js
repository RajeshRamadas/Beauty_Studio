/*
 * AI Generator: the look builder (requirements 9 and 16).
 *
 * A look combines one choice per area (hairstyle, hair colour, makeup, beard,
 * nails), each a catalogue template or a personalised style from face analysis,
 * plus an optional reference photo for other areas, an intensity and whether to
 * keep natural roots. Each choice is sent separately, so the result records the
 * template IDs it used.
 */
(function () {
  const $ = id => document.getElementById(id);
  const AREAS = [
    ['Hairstyle', 'Hair style'],
    ['Hair colour', 'Hair colour'],
    ['Makeup', 'Makeup'],
    ['Beard & grooming', 'Beard & grooming'],
    ['Nail art', 'Nails']
  ];
  const MAX_AREAS = 4;

  let look = {};             // area -> {kind: 'template', template} | {kind: 'custom', name, description}
  let refAreas = [];         // areas the reference photo changes
  let intensity = 'medium';
  let keepRoots = false;
  let targetState = 'none';  // none | checking | ok | bad
  let resultSelections = []; // selections of the last result
  let urls = {};

  function el(tag, cls, text) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }

  const audience = () => (window.Styles ? window.Styles.audience() : 'women');
  const label = area => AREAS.find(a => a[0] === area)[1];
  const hasReference = () => !!(($('reference-file').files || [])[0]);
  const usedAreas = () => AREAS.map(a => a[0]).filter(a => look[a] || (hasReference() && refAreas.includes(a)));

  /* Areas shown as rows: the audience's usual ones plus any already chosen. */
  function rowAreas() {
    const a = audience();
    return AREAS.map(x => x[0]).filter(area => look[area] ||
      (area === 'Beard & grooming' ? a !== 'women' : area === 'Nail art' ? a !== 'men' : true));
  }

  function showImage(slot, file) {
    if (urls[slot]) URL.revokeObjectURL(urls[slot]);
    urls[slot] = URL.createObjectURL(file);
    const box = $(slot);
    const img = el('img');
    img.src = urls[slot];
    img.alt = slot === 'gen-target' ? 'Your photo' : 'Reference photo';
    box.replaceChildren(img);
    box.classList.add('filled');
  }

  function showEmpty(slot) {
    const box = $(slot);
    box.classList.remove('filled');
    box.replaceChildren($(slot + '-empty').content.cloneNode(true));
  }

  function lookRow(area) {
    const item = look[area];
    const row = el('div', 'look-row' + (item ? ' set' : ''));
    const thumb = item && item.kind === 'template'
      ? window.Styles.picture(item.template, 'look-thumb')
      : el('div', 'look-thumb style-tile');
    if (!item || item.kind !== 'template') thumb.innerHTML = item ? '<svg viewBox="0 0 24 24"><path d="M12 3l2 5 5 .7-3.7 3.5.9 5.3L12 15l-4.2 2.5.9-5.3L5 8.7 10 8z"/></svg>' : '';
    const text = el('div', 'look-text');
    text.append(el('span', 'caption', label(area)));
    if (item) {
      const name = el('b', null, item.kind === 'template' ? item.template.name : item.name);
      text.append(name);
      if (item.kind === 'custom') text.append(el('span', 'caption', 'Personalised idea'));
    } else if (hasReference() && refAreas.includes(area)) {
      text.append(el('b', null, 'From your reference photo'));
    } else {
      text.append(el('span', 'look-keep', 'Keep my own'));
    }
    const actions = el('div', 'look-actions');
    const choose = el('button', 'btn btn-s btn-sm', item ? 'Change' : 'Choose');
    choose.type = 'button';
    choose.onclick = () => window.Styles.openCategory(area);
    actions.append(choose);
    if (item) {
      const rm = el('button', 'look-remove', '×');
      rm.type = 'button';
      rm.setAttribute('aria-label', 'Remove ' + label(area));
      rm.onclick = () => { delete look[area]; render(); };
      actions.append(rm);
    }
    row.append(thumb, text, actions);
    return row;
  }

  function renderRefChips() {
    const box = $('ref-areas');
    box.style.display = hasReference() ? '' : 'none';
    if (!hasReference()) return;
    const free = AREAS.map(a => a[0]).filter(a => !look[a]);
    refAreas = refAreas.filter(a => free.includes(a));
    $('ref-chips').replaceChildren(...free.map(area => {
      const on = refAreas.includes(area);
      const b = el('button', 'chip area-chip' + (on ? ' active' : ''), (on ? '✓ ' : '') + label(area));
      b.type = 'button';
      b.setAttribute('aria-pressed', on);
      b.onclick = () => {
        refAreas = on ? refAreas.filter(a => a !== area) : refAreas.concat(area);
        render();
      };
      return b;
    }));
  }

  function renderOptions() {
    document.querySelectorAll('#intensity button').forEach(b => {
      const on = b.dataset.v === intensity;
      b.classList.toggle('active', on);
      b.setAttribute('aria-pressed', on);
    });
    const colour = !!look['Hair colour'] || refAreas.includes('Hair colour');
    $('roots-row').style.display = colour ? '' : 'none';
    $('keep-roots').checked = keepRoots;
  }

  function render() {
    if (!$('look-rows')) return;
    $('look-rows').replaceChildren(...rowAreas().map(lookRow));
    renderRefChips();
    renderOptions();
    updateReady();
  }

  /* keepStatus: only refresh the button (used after a generation, so its error stays visible). */
  function updateReady(opts) {
    const btn = $('generate-btn');
    if (!btn || btn.dataset.busy === '1') return;
    const missing = [];
    if (targetState === 'none') missing.push('add your photo');
    else if (targetState === 'checking') missing.push('wait while we check your photo');
    else if (targetState === 'bad') missing.push('retake or choose a clear, complete photo');
    const areas = usedAreas();
    if (!areas.length) missing.push(hasReference() ? 'choose what the reference photo changes' : 'choose at least one style');
    if (areas.length > MAX_AREAS) missing.push('choose up to ' + MAX_AREAS + ' areas');
    btn.disabled = missing.length > 0;
    if (opts && opts.keepStatus) return;
    const st = $('gen-status');
    if (st.classList.contains('err') && missing.length) return;
    st.className = 'msg mt-12';
    st.textContent = missing.length
      ? 'To generate: ' + missing.join(', ') + '.'
      : 'Ready. We’ll change: ' + areas.map(a => label(a).toLowerCase()).join(', ') + '. Everything else stays as in your photo.';
  }

  window.Generator = {
    init() {
      showEmpty('gen-target');
      showEmpty('gen-ref');
      render();
    },
    render,
    updateReady,
    has: t => !!(t && look[t.category] && look[t.category].kind === 'template' && look[t.category].template.id === t.id),

    setTemplate(t) {
      look[t.category] = { kind: 'template', template: t };
      refAreas = refAreas.filter(a => a !== t.category);
      render();
    },

    /* A personalised idea from face analysis, described in words. */
    setCustom(area, name, description) {
      look[area] = { kind: 'custom', name, description };
      refAreas = refAreas.filter(a => a !== area);
      render();
    },

    clearLook() { look = {}; render(); },

    setIntensity(v) { intensity = v; renderOptions(); },
    setKeepRoots(v) { keepRoots = !!v; },
    intensity: () => intensity,

    async setTarget(file) {
      if (!(await window.Consent.ensure())) {
        $('person-file').value = '';
        $('camera-capture').value = '';
        return false;
      }
      showImage('gen-target', file);
      $('person-status').textContent = 'Your photo';
      targetState = 'checking';
      updateReady();
      window.PhotoCheck.check(file, $('gen-target-check'), {
        onResult: ok => { targetState = ok ? 'ok' : 'bad'; updateReady(); },
        retake: () => Generator.openCamera(),
        upload: () => $('person-file').click(),
        label: 'Your photo',
        slot: $('gen-target')
      });
      return true;
    },

    openCamera() {
      window.GuidedCamera.open(f => window.setTargetPhoto(f), $('camera-capture'));
    },

    onReferenceInput(ev) {
      const f = ev.target.files && ev.target.files[0];
      if (!f) return;
      showImage('gen-ref', f);
      $('reference-status').textContent = 'Reference photo';
      $('ref-clear').style.display = '';
      if (!refAreas.length) refAreas = AREAS.map(a => a[0]).filter(a => !look[a]).slice(0, 1);
      render();
    },

    clearReference() {
      $('reference-file').value = '';
      showEmpty('gen-ref');
      $('reference-status').textContent = 'Reference (optional)';
      $('ref-clear').style.display = 'none';
      refAreas = [];
      render();
    },

    /* The request body for /api/v1/generations. */
    form(person) {
      const fd = new FormData();
      fd.append('target_image', person);
      const templates = Object.values(look).filter(i => i.kind === 'template').map(i => i.template.id);
      const custom = Object.entries(look).filter(([, i]) => i.kind === 'custom')
        .map(([area, i]) => ({ area, name: i.name, description: i.description }));
      fd.append('templates', templates.join(','));
      if (custom.length) fd.append('custom_styles', JSON.stringify(custom));
      const ref = ($('reference-file').files || [])[0];
      if (ref && refAreas.length) {
        fd.append('reference_image', ref);
        fd.append('category', refAreas.join(','));
      }
      fd.append('intensity', intensity);
      fd.append('keep_roots', keepRoots && usedAreas().includes('Hair colour') ? 'true' : 'false');
      fd.append('notes', $('custom-notes').value.trim());
      fd.append('consent_version', window.Consent.version());
      return fd;
    },

    setResultSelections(s) { resultSelections = s || []; },
    resultTemplateIds: () => resultSelections.map(s => s.template_id).filter(Boolean)
  };
})();
