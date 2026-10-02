/*
 * AI Generator screen: side-by-side previews of the user's photo and the style,
 * and a multi-select of what to change (hair style, hair colour, makeup, nails,
 * beard & grooming). The selected areas are sent as a comma-separated category.
 */
(function () {
  const $ = id => document.getElementById(id);
  const AREAS = {
    women: [['Hairstyle', 'Hair style'], ['Hair colour', 'Hair colour'], ['Makeup', 'Makeup'], ['Nail art', 'Nails']],
    men: [['Hairstyle', 'Hair style'], ['Hair colour', 'Hair colour'], ['Beard & grooming', 'Beard & grooming']]
  };
  // What a catalogue style's category pre-selects.
  const PRESELECT = {
    'Hairstyle': ['Hairstyle'],
    'Makeup': ['Makeup'],
    'Nail art': ['Nail art'],
    'Beard & grooming': ['Beard & grooming'],
    'Overall beauty look': { women: ['Hairstyle', 'Makeup'], men: ['Hairstyle', 'Beard & grooming'] }
  };

  let selected = ['Hairstyle'];
  let targetState = 'none';  // none | checking | ok | bad
  let refStyle = null;      // catalogue style used without a reference image
  let urls = {};

  const audience = () => (window.Styles ? window.Styles.audience() : 'women');
  const options = () => AREAS[audience()] || AREAS.women;

  function showImage(slot, file) {
    if (urls[slot]) URL.revokeObjectURL(urls[slot]);
    urls[slot] = URL.createObjectURL(file);
    const box = $(slot);
    const img = document.createElement('img');
    img.src = urls[slot];
    img.alt = slot === 'gen-target' ? 'Your photo' : 'Style reference';
    box.replaceChildren(img);
    box.classList.add('filled');
  }

  function showEmpty(slot) {
    const box = $(slot);
    box.classList.remove('filled');
    const tpl = $(slot + '-empty');
    box.replaceChildren(tpl.content.cloneNode(true));
  }

  function renderChips() {
    const valid = options().map(o => o[0]);
    selected = selected.filter(a => valid.includes(a));
    $('area-chips').replaceChildren(...options().map(([value, label]) => {
      const b = document.createElement('button');
      b.type = 'button';
      const on = selected.includes(value);
      b.className = 'chip area-chip' + (on ? ' active' : '');
      b.setAttribute('aria-pressed', on);
      b.textContent = (on ? '✓ ' : '') + label;
      b.onclick = () => {
        selected = on ? selected.filter(a => a !== value) : selected.concat(value);
        renderChips();
      };
      return b;
    }));
    updateReady();
  }

  function hasTarget() { return targetState === 'ok'; }
  function hasReference() { return !!(($('reference-file').files || [])[0]) || !!refStyle; }

  /* keepStatus: only refresh the button (used after a generation, so its error stays visible). */
  function updateReady(opts) {
    const btn = $('generate-btn');
    if (!btn || btn.dataset.busy === '1') return;
    const missing = [];
    if (targetState === 'none') missing.push('add your photo');
    else if (targetState === 'checking') missing.push('wait while we check your photo');
    else if (targetState === 'bad') missing.push('retake or choose a clear, complete photo');
    if (!hasReference()) missing.push('add a style (upload one or browse styles)');
    if (!selected.length) missing.push('choose what to change');
    btn.disabled = missing.length > 0;
    if (opts && opts.keepStatus) return;
    const st = $('gen-status');
    if (st.classList.contains('err') && missing.length) return;
    st.className = 'msg mt-12';
    st.textContent = missing.length
      ? 'To generate: ' + missing.join(', ') + '.'
      : 'Ready. We’ll change: ' + selected.map(a => options().find(o => o[0] === a)[1].toLowerCase()).join(', ') + '.';
  }

  window.Generator = {
    init() {
      showEmpty('gen-target');
      showEmpty('gen-ref');
      renderChips();
    },
    renderChips,
    updateReady,
    areas: () => selected.slice(),

    setTarget(file) {
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
    },

    openCamera() {
      window.GuidedCamera.open(f => window.setTargetPhoto(f), $('camera-capture'));
    },

    /* A reference image, from upload or a catalogue style's sample photo. */
    setReferenceFile(file, label, fromCatalogue) {
      refStyle = null;
      if (!fromCatalogue) $('style-name').value = '';
      showImage('gen-ref', file);
      $('reference-status').textContent = label || 'Your reference';
      updateReady();
    },

    /* A catalogue style with no photo: generated from its description. */
    /** A personalised (non-catalogue) style chosen for try-on without a reference photo, or null. */
    customStyle: () => (refStyle && refStyle.custom ? refStyle : null),

    setReferenceStyle(style) {
      refStyle = style;
      $('reference-file').value = '';
      const box = $('gen-ref');
      box.replaceChildren(window.Styles.picture(style, 'gen-tile'));
      box.classList.add('filled');
      $('reference-status').textContent = style.name + ' · no photo needed';
      updateReady();
    },

    preselect(category) {
      const p = PRESELECT[category];
      if (!p) return;
      selected = Array.isArray(p) ? p.slice() : (p[audience()] || p.women).slice();
      renderChips();
    },

    onReferenceInput(ev) {
      const f = ev.target.files && ev.target.files[0];
      if (f) Generator.setReferenceFile(f, 'Your reference', false);
    }
  };
})();
