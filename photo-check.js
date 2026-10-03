/*
 * Photo quality gate and guided camera.
 *
 * PhotoCheck.check(file, box, handlers) asks the server whether a face photo is
 * complete and clear, shows the result in `box`, and offers Retake / Upload
 * another when it is not. GuidedCamera.open(onCapture) shows a live camera with
 * a face-and-hair outline so the whole head is framed; it falls back to the
 * phone's own camera when live video isn't available.
 */
(function () {
  const $ = id => document.getElementById(id);

  function el(tag, cls, text) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }

  let seq = 0;

  window.PhotoCheck = {
    /**
     * handlers: { onResult(ok), retake(), upload(), label?, slot? }
     * label names the photo in messages (e.g. "Your photo"); slot is outlined while the photo has a problem.
     * Returns a promise resolving to true when the photo is usable.
     */
    async check(file, box, handlers) {
      const id = ++seq;
      box.dataset.seq = id;
      const label = handlers.label || 'This photo';
      if (handlers.slot) handlers.slot.classList.remove('pc-bad');
      box.className = 'photo-check checking';
      box.replaceChildren(el('span', 'pc-spin'), el('span', null, 'Checking your photo…'));
      // Outcomes: 'ok', 'bad' (a problem with the photo itself) or
      // 'unavailable' (the check couldn't run: server or network issue).
      let outcome = 'bad', data = null, note = '';
      try {
        const fd = new FormData();
        fd.append('face_image', file);
        fd.append('consent_version', window.Consent ? window.Consent.version() : '');
        const res = await fetch('/api/v1/check-photo', { method: 'POST', body: fd });
        data = await res.json().catch(() => ({}));
        const detail = typeof data.detail === 'string' ? data.detail : '';
        if (res.ok) {
          outcome = data.usable ? 'ok' : 'bad';
        } else if (res.status === 428) {
          data = { problems: [{ message: 'Agree to how your photo is used before we can check it.' }] };
        } else if (res.status === 400 || res.status === 413) {
          data = { problems: [{ message: detail || 'This file can’t be used as a photo.' }] };  // the file itself is the problem
        } else {
          outcome = 'unavailable';
          note = res.status === 404
            ? 'The photo check isn’t available on this server yet (it may need restarting).'
            : (detail || 'The photo check isn’t available right now.');
        }
      } catch (e) {
        outcome = 'unavailable';
        note = 'We couldn’t reach the server to check this photo.';
      }
      if (String(id) !== box.dataset.seq) return outcome !== 'bad'; // a newer photo replaced this one
      const ok = outcome !== 'bad';

      if (outcome === 'ok') {
        box.className = 'photo-check ok';
        box.replaceChildren(el('span', 'pc-icon', '✓'), el('span', null, 'Photo looks good'));
        const fixes = (data && data.enhancements) || [];
        if (fixes.length) box.append(el('span', 'pc-fixes', 'We’ll auto-adjust it: ' + fixes.join(', ').toLowerCase() + '.'));
      } else if (outcome === 'unavailable') {
        box.className = 'photo-check warn';
        box.replaceChildren(el('span', null, note + ' You can continue, but make sure your whole face and hair are clear and well lit.'));
      } else {
        box.className = 'photo-check bad';
        const title = el('p', 'pc-title', label + ' needs to be retaken or replaced');
        const which = el('p', 'pc-file', 'File: ' + (file.name || 'camera photo'));
        const list = el('ul', 'pc-list');
        (data.problems || []).forEach(p => list.append(el('li', null, p.message)));
        const actions = el('div', 'pc-actions');
        const retake = el('button', 'btn btn-p btn-sm', 'Retake photo');
        retake.type = 'button';
        retake.onclick = handlers.retake;
        const upload = el('button', 'btn btn-s btn-sm', 'Upload another');
        upload.type = 'button';
        upload.onclick = handlers.upload;
        actions.append(retake, upload);
        box.replaceChildren(title, which, list, actions);
        if (handlers.slot) handlers.slot.classList.add('pc-bad');
      }
      box.setAttribute('role', outcome === 'bad' ? 'alert' : 'status');
      handlers.onResult(ok);
      return ok;
    },

    reset(box) {
      seq++;
      box.className = 'photo-check';
      box.replaceChildren();
    }
  };

  /* ── Guided camera ───────────────────────────────── *
   * Live tips while framing (light, distance, centring, steadiness), optional
   * auto-capture once everything is right, and a short burst on capture that
   * keeps the sharpest frame.
   */
  let stream = null, onCaptureCb = null, fallbackInput = null, facing = 'user';
  let loop = null, prevSmall = null, readyTicks = 0, busy = false;
  let auto = true;
  try { auto = localStorage.getItem('glow_autocapture') !== 'off'; } catch (e) { /* storage unavailable */ }
  const detector = ('FaceDetector' in window) ? (() => { try { return new window.FaceDetector({ fastMode: true, maxDetectedFaces: 2 }); } catch (e) { return null; } })() : null;
  const TICK_MS = 200, READY_TICKS = 6, BURST = 4, BURST_GAP_MS = 90;

  /* The part of the video the user sees (the preview is object-fit: cover). */
  function visibleRect(v) {
    const vw = v.videoWidth, vh = v.videoHeight;
    const ew = v.clientWidth || vw, eh = v.clientHeight || vh;
    const scale = Math.max(ew / vw, eh / vh);
    const sw = Math.min(vw, Math.round(ew / scale)), sh = Math.min(vh, Math.round(eh / scale));
    return { sx: Math.round((vw - sw) / 2), sy: Math.round((vh - sh) / 2), sw, sh };
  }

  function grab(v, r, width) {
    const c = document.createElement('canvas');
    c.width = width || r.sw;
    c.height = Math.round(c.width * r.sh / r.sw);
    c.getContext('2d', { willReadFrequently: true }).drawImage(v, r.sx, r.sy, r.sw, r.sh, 0, 0, c.width, c.height);
    return c;
  }

  function grey(c, x, y, w, h) {
    const d = c.getContext('2d', { willReadFrequently: true }).getImageData(x, y, w, h).data;
    const g = new Float32Array(w * h);
    for (let i = 0, j = 0; i < d.length; i += 4, j++) g[j] = 0.299 * d[i] + 0.587 * d[i + 1] + 0.114 * d[i + 2];
    return g;
  }

  /* Variance of the Laplacian over the face area: higher is sharper. */
  function sharpness(c) {
    const w = Math.round(c.width * 0.5), h = Math.round(c.height * 0.45);
    const x = Math.round(c.width * 0.25), y = Math.round(c.height * 0.2);
    const scale = Math.min(1, 320 / w);
    const small = document.createElement('canvas');
    small.width = Math.max(8, Math.round(w * scale));
    small.height = Math.max(8, Math.round(h * scale));
    small.getContext('2d').drawImage(c, x, y, w, h, 0, 0, small.width, small.height);
    const W = small.width, H = small.height, g = grey(small, 0, 0, W, H);
    let sum = 0, sum2 = 0, n = 0;
    for (let yy = 1; yy < H - 1; yy++) for (let xx = 1; xx < W - 1; xx++) {
      const i = yy * W + xx;
      const lap = 4 * g[i] - g[i - 1] - g[i + 1] - g[i - W] - g[i + W];
      sum += lap; sum2 += lap * lap; n++;
    }
    return n ? sum2 / n - (sum / n) ** 2 : 0;
  }

  function setTip(text, state) {
    $('cam-live').textContent = text;
    $('cam-modal').dataset.state = state;  // ok | warn
  }

  async function tick() {
    const v = $('cam-video');
    if (!v.videoWidth || busy) return;
    const r = visibleRect(v);
    const small = grab(v, r, 96);
    const W = small.width, H = small.height;
    // Brightness of the face area (inside the outline).
    const face = grey(small, Math.round(W * 0.25), Math.round(H * 0.2), Math.round(W * 0.5), Math.round(H * 0.45));
    const light = face.reduce((a, b) => a + b, 0) / face.length;
    // Movement between frames.
    const all = grey(small, 0, 0, W, H);
    let motion = 0;
    if (prevSmall && prevSmall.length === all.length) {
      for (let i = 0; i < all.length; i++) motion += Math.abs(all[i] - prevSmall[i]);
      motion /= all.length;
    }
    prevSmall = all;

    let tip = null;
    if (light < 70) tip = 'Too dark: face a window or a bright light';
    else if (light > 215) tip = 'Too bright: step out of direct light';
    if (!tip && detector) {
      try {
        const faces = await detector.detect(grab(v, r, 320));
        if (!faces.length) tip = 'Look straight at the camera';
        else if (faces.length > 1) tip = 'Only one person in the photo, please';
        else {
          const b = faces[0].boundingBox, fw = b.width / 320, cx = (b.x + b.width / 2) / 320;
          const cy = (b.y + b.height / 2) / Math.round(320 * r.sh / r.sw);
          if (fw < 0.28) tip = 'Move a little closer';
          else if (fw > 0.62) tip = 'Move back a little so your hair fits';
          else if (Math.abs(cx - 0.5) > 0.12 || Math.abs(cy - 0.46) > 0.14) tip = 'Centre your face in the outline';
        }
      } catch (e) { /* detection unavailable on this frame */ }
    }
    if (!tip && motion > 6) tip = 'Hold still';

    if (tip) { readyTicks = 0; setTip(tip, 'warn'); return; }
    readyTicks++;
    if (auto) {
      const left = Math.ceil((READY_TICKS - readyTicks) * TICK_MS / 1000);
      setTip(left > 0 ? 'Perfect, hold still… ' + left : 'Taking photo…', 'ok');
      if (readyTicks >= READY_TICKS) GuidedCamera.capture();
    } else {
      setTip('Looks good: tap the button', 'ok');
    }
  }

  function renderAuto() {
    const b = $('cam-auto');
    b.textContent = 'Auto-capture: ' + (auto ? 'On' : 'Off');
    b.setAttribute('aria-pressed', auto);
  }

  function stop() {
    if (loop) { clearInterval(loop); loop = null; }
    if (stream) { stream.getTracks().forEach(t => t.stop()); stream = null; }
    $('cam-modal').hidden = true;
    document.body.classList.remove('cam-open');
  }

  async function start() {
    if (stream) stream.getTracks().forEach(t => t.stop());
    stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: facing, width: { ideal: 1920 }, height: { ideal: 1440 } }, audio: false
    });
    const v = $('cam-video');
    v.srcObject = stream;
    v.classList.toggle('mirror', facing === 'user');
    await v.play();
    prevSmall = null; readyTicks = 0; busy = false;
    if (loop) clearInterval(loop);
    loop = setInterval(tick, TICK_MS);
  }

  const wait = ms => new Promise(r => setTimeout(r, ms));

  window.GuidedCamera = {
    /** fallback: the <input type=file capture> to use when live camera isn't available */
    async open(onCapture, fallback) {
      onCaptureCb = onCapture;
      fallbackInput = fallback;
      if (!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia)) { fallback.click(); return; }
      $('cam-modal').hidden = false;
      document.body.classList.add('cam-open');
      $('cam-error').hidden = true;
      renderAuto();
      setTip('Fit your whole face and hair inside the outline', 'warn');
      try { await start(); }
      catch (e) {
        stop();
        fallback.click();
      }
    },

    async flip() {
      facing = facing === 'user' ? 'environment' : 'user';
      try { await start(); } catch (e) { facing = 'user'; }
    },

    toggleAuto() {
      auto = !auto;
      try { localStorage.setItem('glow_autocapture', auto ? 'on' : 'off'); } catch (e) { /* storage unavailable */ }
      readyTicks = 0;
      renderAuto();
    },

    /* Takes a short burst and keeps the sharpest frame. */
    async capture() {
      const v = $('cam-video');
      if (!v.videoWidth || busy) return;
      busy = true;
      setTip('Hold still…', 'ok');
      const r = visibleRect(v);
      let best = null, bestScore = -1;
      for (let i = 0; i < BURST; i++) {
        if (i) await wait(BURST_GAP_MS);
        const frame = grab(v, r);
        const score = sharpness(frame);
        if (score > bestScore) { best = frame; bestScore = score; }
      }
      // Save as the user saw it (the front camera preview is mirrored).
      let out = best;
      if (facing === 'user') {
        out = document.createElement('canvas');
        out.width = best.width; out.height = best.height;
        const ctx = out.getContext('2d');
        ctx.translate(out.width, 0); ctx.scale(-1, 1);
        ctx.drawImage(best, 0, 0);
      }
      out.toBlob(blob => {
        busy = false;
        if (!blob) return;
        const file = new File([blob], 'camera-photo.jpg', { type: 'image/jpeg' });
        stop();
        onCaptureCb && onCaptureCb(file);
      }, 'image/jpeg', 0.95);
    },

    useDeviceCamera() { stop(); if (fallbackInput) fallbackInput.click(); },
    close: stop,
    _sharpness: sharpness
  };

  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && !$('cam-modal').hidden) stop();
  });
})();
