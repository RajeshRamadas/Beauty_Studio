/*
 * Face analysis screen: upload or take a photo, get face shape, skin tone,
 * undertone and hair profile, plus recommended hairstyles, makeup, full looks,
 * hair colours and tips. Each recommendation can be tried on with the same photo.
 * Results come from an AI model and are rendered with textContent only.
 */
(function () {
  const $ = id => document.getElementById(id);
  let photo = null;
  let chosenSection = 'auto';  // auto | women | men

  function el(tag, cls, text) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }

  function setStatus(text, kind) {
    const s = $('fa-status');
    s.textContent = text || '';
    s.className = 'msg' + (kind ? ' ' + kind : '');
    s.style.display = text ? 'block' : 'none';
  }

  function chip(label, value) {
    const c = el('div', 'fa-chip');
    c.append(el('span', 'caption', label), el('b', null, value));
    return c;
  }

  function recCard(item) {
    const c = el('div', 'fa-rec');
    const img = window.Styles.picture({ name: item.name, category: item.category, image: item.image_url }, 'fa-rec-img');
    const body = el('div', 'fa-rec-body');
    const btn = el('button', 'btn btn-p btn-sm', 'Try on');
    btn.type = 'button';
    btn.onclick = () => FaceAnalysis.tryOn(item);
    body.append(el('p', 'salon-name', item.name), el('p', 'caption', item.reason), btn);
    c.append(img, body);
    return c;
  }

  function section(title, nodes) {
    if (!nodes.length) return null;
    const s = el('section', 'mb-20');
    s.append(el('h2', 'mb-12', title));
    const list = el('div', 'fa-list');
    list.append(...nodes);
    s.append(list);
    return s;
  }

  function sectionBanner(d) {
    const other = d.style_section === 'men' ? 'women' : 'men';
    const why = d.style_section_source === 'photo' ? ' (suggested from your photo)' : d.style_section_source === 'you' ? ' (your choice)' : '';
    const b = el('div', 'fa-banner');
    b.append(el('span', null, 'Showing ' + (d.style_section === 'men' ? 'men’s' : 'women’s') + ' styles' + why + '.'));
    const sw = el('button', 'btn-link', 'Show ' + (other === 'men' ? 'men’s' : 'women’s') + ' styles instead');
    sw.type = 'button';
    sw.onclick = () => { FaceAnalysis.setSection(other); FaceAnalysis.run(); };
    b.append(sw);
    return b;
  }

  function render(d) {
    const out = $('fa-results');
    out.replaceChildren();
    if (!d.face_detected) {
      setStatus((d.issue || 'We couldn’t see one clear face.') + ' Try a well-lit, front-facing photo with only you in it.', 'err');
      return;
    }
    setStatus('');
    if (d.style_section === 'women' || d.style_section === 'men') window.Styles.setAudience(d.style_section);

    const profile = el('div', 'card');
    profile.append(el('h2', 'mb-12', 'Your profile'));
    const grid = el('div', 'fa-chips');
    grid.append(chip('Face shape', d.face_shape), chip('Skin tone', d.skin_tone), chip('Undertone', d.undertone));
    const hair = d.hair || {};
    if (hair.texture && hair.texture !== 'Not visible') grid.append(chip('Hair texture', hair.texture));
    if (hair.length && hair.length !== 'Not visible') grid.append(chip('Hair length', hair.length));
    if (hair.thickness && hair.thickness !== 'Not visible') grid.append(chip('Hair thickness', hair.thickness));
    if (hair.colour) grid.append(chip('Hair colour', hair.colour));
    if (d.style_section === 'men' && d.facial_hair) grid.append(chip('Facial hair', d.facial_hair));
    profile.append(grid);
    if (d.face_shape_reason) profile.append(el('p', 'caption mt-12', d.face_shape_reason));
    if (d.summary) profile.append(el('p', 'mt-12 fa-summary', d.summary));
    out.append(profile);

    const r = d.recommendations || {};
    out.append(sectionBanner(d));
    [['Hairstyles for you', r.hairstyles], ['Makeup for you', r.makeup], ['Beard & grooming for you', r.grooming], ['Full looks', r.full_looks]].forEach(([t, items]) => {
      const s = section(t, (items || []).map(recCard));
      if (s) out.append(s);
    });

    const colours = (d.hair_colours || []).filter(c => /^#[0-9A-Fa-f]{6}$/.test(c.hex)).map(c => {
      const row = el('div', 'fa-colour');
      const sw = el('span', 'fa-swatch');
      sw.style.background = c.hex;
      const txt = el('div');
      txt.append(el('p', 'salon-name', c.name), el('p', 'caption', c.reason));
      row.append(sw, txt);
      return row;
    });
    const cs = section('Hair colours that suit you', colours);
    if (cs) out.append(cs);

    if ((d.tips || []).length) {
      const t = el('div', 'card');
      t.append(el('h2', 'mb-12', 'Tips'));
      const ul = el('ul', 'fa-tips');
      d.tips.forEach(tip => ul.append(el('li', null, tip)));
      t.append(ul);
      out.append(t);
    }
    out.append(el('p', 'caption mt-12', 'Suggestions are AI-generated and approximate. Use them as inspiration.'));
    out.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  window.FaceAnalysis = {
    pick(ev) {
      const f = ev.target.files && ev.target.files[0];
      ev.target.value = '';
      if (f) FaceAnalysis.pickFile(f);
    },

    pickFile(f) {
      photo = null;  // only set once the photo passes the check
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
        upload: () => $('fa-file').click()
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
      setStatus('Looking at your face shape, skin tone and hair. This takes a few seconds.');
      $('fa-results').replaceChildren();
      const fd = new FormData();
      fd.append('face_image', photo);
      fd.append('section', chosenSection);
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

    setSection(value) {
      chosenSection = ['women', 'men'].includes(value) ? value : 'auto';
      document.querySelectorAll('#fa-section button').forEach(b => {
        const on = b.dataset.sec === chosenSection;
        b.classList.toggle('active', on);
        b.setAttribute('aria-pressed', on);
      });
    },

    tryOn(item) {
      if (photo && typeof window.setTargetPhoto === 'function') window.setTargetPhoto(photo);
      window.selectPreset(item.category, item.name, item.image_url);
    }
  };
})();
