/*
 * Photo consent (requirements 13): before any photo is checked, analysed or
 * used for a try-on, the user sees how it is used and agrees. The accepted
 * version is remembered on this device and sent with every photo request; the
 * server refuses photos without the current version.
 */
(function () {
  const KEY = 'glow_photo_consent';
  const $ = id => document.getElementById(id);
  let config = null;
  let pending = null;

  async function load() {
    if (config) return config;
    try {
      const r = await fetch('/api/v1/client-config');
      const c = await r.json();
      config = c.privacy || {};
    } catch (e) { config = {}; }
    return config;
  }

  function stored() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }

  function close(result) {
    $('consent-modal').hidden = true;
    document.body.classList.remove('cam-open');
    if (pending) { pending(result); pending = null; }
  }

  window.Consent = {
    /** The accepted version, or '' when the user hasn't agreed to the current text. */
    version() {
      const v = stored();
      return config && v === config.photo_consent_version ? v : '';
    },

    /** Resolves true once the user has agreed (asking if needed), false if they decline. */
    async ensure() {
      const c = await load();
      if (!c.photo_consent_version) return false;
      if (stored() === c.photo_consent_version) return true;
      $('consent-retention').textContent = c.retention_days || 30;
      $('consent-modal').hidden = false;
      document.body.classList.add('cam-open');
      return new Promise(resolve => { pending = resolve; });
    },

    accept() {
      try { localStorage.setItem(KEY, config.photo_consent_version); } catch (e) { /* storage unavailable */ }
      close(true);
    },

    decline() { close(false); },

    /** Show the text again (Profile → Photo privacy); declining withdraws consent on this device. */
    async review() {
      try { localStorage.removeItem(KEY); } catch (e) { /* storage unavailable */ }
      return Consent.ensure();
    },

    init() { load(); }
  };
})();
