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
     * handlers: { onResult(ok), retake(), upload() }
     * Returns a promise resolving to true when the photo is usable.
     */
    async check(file, box, handlers) {
      const id = ++seq;
      box.dataset.seq = id;
      box.className = 'photo-check checking';
      box.replaceChildren(el('span', 'pc-spin'), el('span', null, 'Checking your photo…'));
      let ok = false, data = null;
      try {
        const fd = new FormData();
        fd.append('face_image', file);
        const res = await fetch('/api/v1/check-photo', { method: 'POST', body: fd });
        data = await res.json().catch(() => ({}));
        if (!res.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'We couldn’t check this photo.');
        ok = !!data.usable;
      } catch (e) {
        data = { problems: [{ message: e.message }] };
      }
      if (String(id) !== box.dataset.seq) return ok; // a newer photo replaced this one

      if (ok) {
        box.className = 'photo-check ok';
        box.replaceChildren(el('span', 'pc-icon', '✓'), el('span', null, 'Photo looks good'));
      } else {
        box.className = 'photo-check bad';
        const title = el('p', 'pc-title', 'Please retake or choose another photo');
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
        box.replaceChildren(title, list, actions);
      }
      box.setAttribute('role', ok ? 'status' : 'alert');
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
      const c = document.createElement('canvas');
      c.width = v.videoWidth;
      c.height = v.videoHeight;
      const ctx = c.getContext('2d');
      if (facing === 'user') { ctx.translate(c.width, 0); ctx.scale(-1, 1); } // save as the user saw it
      ctx.drawImage(v, 0, 0);
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
