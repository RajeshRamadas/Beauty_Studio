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
        const res = await fetch('/api/v1/check-photo', { method: 'POST', body: fd });
        data = await res.json().catch(() => ({}));
        const detail = typeof data.detail === 'string' ? data.detail : '';
        if (res.ok) {
          outcome = data.usable ? 'ok' : 'bad';
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

  /* ── Guided camera ───────────────────────────────── */
  let stream = null, onCaptureCb = null, fallbackInput = null, facing = 'user';

  function stop() {
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
  }

  window.GuidedCamera = {
    /** fallback: the <input type=file capture> to use when live camera isn't available */
    async open(onCapture, fallback) {
      onCaptureCb = onCapture;
      fallbackInput = fallback;
      if (!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia)) { fallback.click(); return; }
      $('cam-modal').hidden = false;
      document.body.classList.add('cam-open');
      $('cam-error').hidden = true;
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

    capture() {
      const v = $('cam-video');
      if (!v.videoWidth) return;
      // The preview fills the screen (object-fit: cover), so save only the part
      // the user actually saw and framed, not the wider hidden edges.
      const vw = v.videoWidth, vh = v.videoHeight;
      const ew = v.clientWidth || vw, eh = v.clientHeight || vh;
      const scale = Math.max(ew / vw, eh / vh);
      const sw = Math.min(vw, Math.round(ew / scale)), sh = Math.min(vh, Math.round(eh / scale));
      const sx = Math.round((vw - sw) / 2), sy = Math.round((vh - sh) / 2);
      const c = document.createElement('canvas');
      c.width = sw;
      c.height = sh;
      const ctx = c.getContext('2d');
      if (facing === 'user') { ctx.translate(sw, 0); ctx.scale(-1, 1); } // save as the user saw it (mirrored)
      ctx.drawImage(v, sx, sy, sw, sh, 0, 0, sw, sh);
      c.toBlob(blob => {
        if (!blob) return;
        const file = new File([blob], 'camera-photo.jpg', { type: 'image/jpeg' });
        stop();
        onCaptureCb && onCaptureCb(file);
      }, 'image/jpeg', 0.92);
    },

    useDeviceCamera() { stop(); if (fallbackInput) fallbackInput.click(); },
    close: stop
  };

  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && !$('cam-modal').hidden) stop();
  });
})();
