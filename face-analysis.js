/*
 * Face analysis screen (requirements 8): estimates of visible characteristics,
 * each with a confidence or "Uncertain", catalogue templates ranked for them
 * (re-ranked without the AI when preferences change), and new personalised
 * ideas. Suggestions are optional: every style stays available to browse.
 * The user chooses which catalogue to get suggestions from; nothing is inferred.
 * Results come from an AI model and are rendered with textContent only.
 */
(function () {
  const $ = id => document.getElementById(id);
  let photo = null;
  let side = null;  // optional profile photo
  let chosenGroup = null;  // women | men | all; defaults to the Home choice
  let lastAnalysis = null;
  let prefs = {};

  const PREFS = [
    ['length', 'Length', ['very short', 'short', 'medium', 'long']],
    ['maintenance', 'Maintenance', ['low', 'medium', 'high']],
    ['occasion', 'Occasion', ['everyday', 'professional', 'formal', 'occasion', 'evening', 'party', 'creative']]
  ];

  function el(tag, cls, text) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }

  const cap = s => s ? s.charAt(0).toUpperCase() + s.slice(1) : s;
  const group = () => chosenGroup || (window.Styles ? window.Styles.audience() : 'all');

  function setStatus(text, kind) {
    const s = $('fa-status');
    s.textContent = text || '';
    s.className = 'msg' + (kind ? ' ' + kind : '');
    s.style.display = text ? 'block' : 'none';
  }

  /* An estimate chip: value plus how sure the model is. */
  function chip(label, est) {
    const c = el('div', 'fa-chip');
    const uncertain = !est || est.value === 'Uncertain';
    c.append(el('span', 'caption', label), el('b', null, uncertain ? 'Uncertain' : est.value));
    if (!uncertain) c.append(el('span', 'conf conf-' + est.confidence, est.confidence + ' confidence'));
    return c;
  }

  function plainChip(label, value) {
    const c = el('div', 'fa-chip');
    c.append(el('span', 'caption', label), el('b', null, value));
    return c;
  }

  function section(title, nodes, browse) {
    const s = el('section', 'mb-20');
    const head = el('div', 'row mb-12');
    head.append(el('h2', null, title));
    if (browse) {
      const b = el('button', 'btn-link', 'Browse all');
      b.type = 'button';
      b.onclick = () => window.Styles.openCategory(browse);
      head.append(b);
    }
    s.append(head);
    const list = el('div', 'fa-list');
    list.append(...nodes);
    s.append(list);
    return s;
  }

  /* A catalogue template with its label and the reasons it was suggested. */
  function templateCard(t) {
    const c = el('div', 'fa-rec');
    const pic = window.Styles.picture(t, 'fa-rec-img');
    const body = el('div', 'fa-rec-body');
    body.append(el('span', 'rec-label' + (t.label === 'Suggested' ? ' on' : ''), t.label));
    const name = el('button', 'tpl-name', t.name);
    name.type = 'button';
    name.onclick = () => window.Styles.openDetail(t.id);
    body.append(name, el('p', 'fa-desc', t.description));
    if ((t.reasons || []).length) body.append(el('p', 'caption', t.reasons.join(' · ')));
    const btn = el('button', 'btn btn-p btn-sm', 'Try this style');
    btn.type = 'button';
    btn.onclick = () => FaceAnalysis.tryTemplate(t.id);
    body.append(btn);
    c.append(pic, body);
    return c;
  }

  function ideaCard(item) {
    const c = el('div', 'fa-rec');
    const tile = el('div', 'fa-rec-img style-tile');
    tile.innerHTML = '<svg viewBox="0 0 24 24"><path d="M12 3l2 5 5 .7-3.7 3.5.9 5.3L12 15l-4.2 2.5.9-5.3L5 8.7 10 8z"/></svg>';
    const body = el('div', 'fa-rec-body');
    body.append(el('p', 'salon-name', item.name), el('p', 'fa-desc', item.description), el('p', 'caption', item.reason));
    const actions = el('div', 'row gap-8');
    const btn = el('button', 'btn btn-p btn-sm', 'Try on');
    btn.type = 'button';
    btn.onclick = () => FaceAnalysis.tryIdea(item);
    actions.append(btn);
    if (item.closest_template) {
      const sim = el('button', 'btn-link', 'Similar: ' + item.closest_template.name);
      sim.type = 'button';
      sim.onclick = () => window.Styles.openDetail(item.closest_template.id);
      actions.append(sim);
    }
    body.append(actions);
    c.append(tile, body);
    return c;
  }

  function prefsCard() {
    const card = el('div', 'card');
    card.append(el('h3', 'mb-4', 'Your preferences (optional)'), el('p', 'caption mb-12', 'Narrow the catalogue suggestions. Remove any time.'));
    const row = el('div', 'pref-row');
    PREFS.forEach(([key, label, opts]) => {
      const s = el('select', 'filter-select' + (prefs[key] ? ' on' : ''));
      s.setAttribute('aria-label', label);
      s.append(Object.assign(el('option', null, label + ': any'), { value: '' }));
      opts.forEach(o => s.append(Object.assign(el('option', null, cap(o)), { value: o })));
      s.value = prefs[key] || '';
      s.onchange = () => { if (s.value) prefs[key] = s.value; else delete prefs[key]; FaceAnalysis.rerank(); };
      row.append(s);
    });
    card.append(row);
    return card;
  }

  function renderCatalogue(cat) {
    const box = $('fa-catalogue');
    box.replaceChildren();
    if (!cat) return;
    box.append(el('h2', 'mb-4', 'From our catalogue'),
               el('p', 'caption mb-12', 'Ranked by matching each style’s tags with your estimates. Every style stays available.'),
               prefsCard());
    if (cat.hairstyles.length) box.append(section('Hairstyles', cat.hairstyles.map(templateCard), 'Hairstyle'));
    else box.append(el('p', 'caption mb-20', 'No hairstyles match these preferences. Remove one to see more.'));
    if (cat.hair_colour_note) {
      const s = section('Hair colours', [el('p', 'caption', cat.hair_colour_note)], 'Hair colour');
      box.append(s);
    } else if (cat.hair_colours.length) {
      box.append(section('Hair colours', cat.hair_colours.map(templateCard), 'Hair colour'));
    }
    if (cat.makeup.length) box.append(section('Makeup', cat.makeup.map(templateCard), 'Makeup'));
    if (cat.beard.length) box.append(section('Beard & grooming', cat.beard.map(templateCard), 'Beard & grooming'));
  }

  function render(d) {
    const out = $('fa-results');
    out.replaceChildren();
    lastAnalysis = d;
    if (!d.face_detected) {
      setStatus((d.issue || 'We couldn’t see one clear face.') + ' Try a well-lit, front-facing photo with only you in it.', 'err');
      return;
    }
    setStatus('');

    const profile = el('div', 'card');
    profile.append(el('h2', 'mb-4', 'Your profile'),
                   el('p', 'caption mb-12', 'Estimates from one photo, not facts. Lighting and camera can change them.'));
    const grid = el('div', 'fa-chips');
    grid.append(chip('Face shape', d.face_shape), chip('Undertone', d.undertone), chip('Skin tone', d.skin_tone));
    const hair = d.hair || {};
    if (hair.visible_length && hair.visible_length !== 'Not visible') grid.append(plainChip('Hair length', hair.visible_length));
    if (hair.texture && hair.texture !== 'Not visible') grid.append(plainChip('Hair texture', hair.texture));
    if (hair.natural_color_estimate) grid.append(plainChip('Hair colour', hair.natural_color_estimate));
    if (d.facial_hair && !/^none$/i.test(d.facial_hair)) grid.append(plainChip('Facial hair', d.facial_hair));
    profile.append(grid);
    if (d.face_shape_reason && d.face_shape.value !== 'Uncertain') profile.append(el('p', 'caption mt-12', d.face_shape_reason));
    const q = d.image_quality || {};
    if (q.lighting && q.lighting !== 'good') profile.append(el('p', 'msg', 'The lighting looks ' + q.lighting + ', so these estimates are less certain.'));
    if (q.face_visible && !q.suitable_for_tryon) profile.append(el('p', 'msg', 'This photo may not give a good try-on. A front-facing photo in even light works best.'));
    const used = [];
    if (d.photos_used === 2) used.push('Front and side photos used');
    if ((d.enhancements || []).length) used.push('Auto-adjusted: ' + d.enhancements.join(', ').toLowerCase());
    if (used.length) profile.append(el('p', 'caption mt-12', used.join(' · ') + '.'));
    if (d.summary) profile.append(el('p', 'mt-12 fa-summary', d.summary));
    out.append(profile);

    const cat = el('div', 'mt-16');
    cat.id = 'fa-catalogue';
    out.append(cat);
    renderCatalogue(d.catalogue);

    const ideas = d.ideas || {};
    const ideaNodes = [['Hairstyle ideas', ideas.hairstyles], ['Makeup ideas', ideas.makeup], ['Grooming ideas', ideas.grooming]]
      .filter(([, items]) => (items || []).length)
      .map(([title, items]) => section(title, items.map(ideaCard)));
    if (ideaNodes.length) {
      out.append(el('h2', 'mb-4', 'New ideas for you'),
                 el('p', 'caption mb-12', 'Designed by AI for your features. They’re not in the catalogue yet; try them on as described.'),
                 ...ideaNodes);
    }

    if ((d.tips || []).length) {
      const t = el('div', 'card');
      t.append(el('h2', 'mb-12', 'Tips'));
      const ul = el('ul', 'fa-tips');
      d.tips.forEach(tip => ul.append(el('li', null, tip)));
      t.append(ul);
      out.append(t);
    }
    out.append(el('p', 'caption mt-12', 'Suggestions are AI-generated and approximate. Choose any style you like.'));
    out.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function useAnalysedPhoto() {
    if (photo && typeof window.setTargetPhoto === 'function') window.setTargetPhoto(photo);
  }

  window.FaceAnalysis = {
    pick(ev) {
      const f = ev.target.files && ev.target.files[0];
      ev.target.value = '';
      if (f) FaceAnalysis.pickFile(f);
    },

    async pickFile(f) {
      photo = null;  // only set once the photo passes the check
      if (!(await window.Consent.ensure())) return;
      const url = URL.createObjectURL(f);
      $('fa-preview').src = url;
      $('fa-preview').style.display = 'block';
      $('fa-placeholder').style.display = 'none';
      $('fa-run').disabled = true;
      $('fa-results').replaceChildren();
      setStatus('');
      window.PhotoCheck.check(f, $('fa-check'), {
        onResult: ok => { photo = ok ? f : null; $('fa-run').disabled = !ok; },
        retake: () => FaceAnalysis.openCamera(),
        upload: () => $('fa-file').click(),
        label: 'Your photo',
        slot: document.querySelector('.fa-photo')
      });
    },

    openCamera() {
      window.GuidedCamera.open(f => FaceAnalysis.pickFile(f), $('fa-camera'));
    },

    async run() {
      if (!photo) { setStatus('Add a clear, complete photo first.', 'err'); return; }
      const btn = $('fa-run');
      btn.disabled = true;
      btn.textContent = 'Analysing…';
      setStatus('Looking at your face shape, undertone and hair. This takes a few seconds.');
      $('fa-results').replaceChildren();
      const fd = new FormData();
      fd.append('face_image', photo);
      if (side) fd.append('side_image', side);
      fd.append('group', group());
      fd.append('consent_version', window.Consent.version());
      Object.entries(prefs).forEach(([k, v]) => fd.append(k, v));
      const headers = {};
      const token = typeof authToken !== 'undefined' ? authToken : null; // shared global from index.html
      if (token) headers['Authorization'] = 'Bearer ' + token;
      try {
        const res = await fetch('/api/v1/analyze-face', { method: 'POST', body: fd, headers });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'Analysis failed. Please try again.');
        render(data);
      } catch (e) {
        setStatus(e.message, 'err');
      } finally {
        btn.disabled = false;
        btn.textContent = 'Analyse my face';
      }
    },

    /* Preferences changed: re-rank the catalogue for the same analysis, without another AI call. */
    async rerank() {
      if (!lastAnalysis) return;
      try {
        const res = await fetch('/api/v1/recommendations', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ group: lastAnalysis.group, analysis: lastAnalysis, preferences: prefs })
        });
        if (res.ok) {
          lastAnalysis.catalogue = await res.json();
          renderCatalogue(lastAnalysis.catalogue);
        }
      } catch (e) { /* keep the current suggestions */ }
    },

    async pickSide(ev) {
      const f = ev.target.files && ev.target.files[0];
      ev.target.value = '';
      if (!f || !(await window.Consent.ensure())) return;
      if (f.size > 12 * 1024 * 1024) { $('fa-side-status').textContent = 'That photo is larger than 12 MB. Choose a smaller one.'; return; }
      side = f;
      const img = el('img');
      img.src = URL.createObjectURL(f);
      img.alt = 'Side photo';
      $('fa-side-thumb').replaceChildren(img);
      $('fa-side-status').textContent = 'Added. We’ll use both photos for face shape and hair.';
      $('fa-side-remove').style.display = '';
    },

    clearSide() {
      side = null;
      $('fa-side-thumb').innerHTML = '<svg viewBox="0 0 24 24"><path d="M9 4c4 0 7 3 7 7 0 1-.3 2-.8 2.8L17 16l-2 .5V19a2 2 0 01-2 2H9"/><path d="M9 4C6 4 5 7 5 9"/></svg>';
      $('fa-side-status').textContent = 'A profile photo makes face shape and hair estimates more accurate.';
      $('fa-side-remove').style.display = 'none';
    },

    setGroup(value) {
      chosenGroup = ['women', 'men', 'all'].includes(value) ? value : null;
      FaceAnalysis.renderGroup();
    },

    renderGroup() {
      document.querySelectorAll('#fa-group button').forEach(b => {
        const on = b.dataset.g === group();
        b.classList.toggle('active', on);
        b.setAttribute('aria-pressed', on);
      });
    },

    tryTemplate(id) {
      useAnalysedPhoto();
      window.Styles.tryOn(id);
    },

    tryIdea(item) {
      useAnalysedPhoto();
      window.Generator.setCustom(item.category, item.name, item.description);
      window.showScreen('screen-7');
    }
  };
})();
