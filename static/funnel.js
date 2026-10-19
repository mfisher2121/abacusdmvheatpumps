/* Funnel helpers: referral codes, lead forms, share buttons, countdowns, events.
   No personal data goes into analytics events. Storage is a convenience only. */
(function () {
  var CFG = window.MB || {};
  var SITE = CFG.site || location.origin;

  function get(store, k) { try { return window[store].getItem(k); } catch (e) { return null; } }
  function set(store, k, v) { try { window[store].setItem(k, v); } catch (e) {} }

  // Cookieless event (Plausible if installed). Props must never hold personal data.
  function track(name, props) {
    try { if (window.plausible) window.plausible(name, { props: props || {} }); } catch (e) {}
  }
  window.mbTrack = track;

  /* ---------- referral codes ---------- */
  var params = new URLSearchParams(location.search);
  var incoming = params.get('ref');
  if (incoming && /^[a-z0-9]{4,12}$/i.test(incoming)) {
    set('sessionStorage', 'mb_came_from', incoming.toLowerCase());
    track('arrived_by_share', { channel: params.get('utm_medium') || 'link' });
  }
  function myRef() {
    var r = get('localStorage', 'mb_ref');
    if (!r) {
      r = Math.random().toString(36).slice(2, 8);
      set('localStorage', 'mb_ref', r);
    }
    return r;
  }
  window.mbRef = myRef;

  function shareUrl(path, medium) {
    var u = new URL(path || '/check/', SITE);
    u.searchParams.set('ref', myRef());
    u.searchParams.set('utm_source', 'neighbor');
    u.searchParams.set('utm_medium', medium || 'share');
    return u.toString();
  }
  window.mbShareUrl = shareUrl;

  /* ---------- outbound official links (North Star) ---------- */
  document.addEventListener('click', function (ev) {
    var a = ev.target.closest && ev.target.closest('a[data-official]');
    if (a) track('official_apply_click', { program: a.getAttribute('data-official') || 'source' });
  });

  /* ---------- mobile menu ---------- */
  var mb = document.querySelector('.menu-btn');
  if (mb) mb.addEventListener('click', function () {
    var nav = document.querySelector('.top nav');
    var open = nav.classList.toggle('open');
    mb.setAttribute('aria-expanded', open ? 'true' : 'false');
  });

  /* ---------- countdowns: days until a sourced date (ET end of day) ---------- */
  document.querySelectorAll('[data-days-until]').forEach(function (el) {
    var end = new Date(el.getAttribute('data-days-until') + 'T23:59:59-05:00');
    var days = Math.ceil((end - new Date()) / 86400000);
    if (days > 1) el.textContent = days + ' days left';
    else if (days === 1) el.textContent = 'Last day';
    else el.textContent = 'Date has passed';
  });

  /* ---------- lead forms ---------- */
  function bindForms(root) {
  root.querySelectorAll('form[data-lead]').forEach(function (form) {
    if (form.hasAttribute('data-bound')) return;
    form.setAttribute('data-bound', '');
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var msg = form.querySelector('.form-msg');
      var btn = form.querySelector('button[type=submit]');
      if (!form.checkValidity()) { form.reportValidity(); return; }

      var data = { type: form.getAttribute('data-lead') };
      Array.prototype.forEach.call(form.elements, function (el) {
        if (!el.name) return;
        if (el.type === 'checkbox') data[el.name] = el.checked;
        else if (el.type === 'radio') { if (el.checked) data[el.name] = el.value; }
        else data[el.name] = el.value.trim();
      });
      // Consent text shown at submit time, so the record says exactly what was agreed to.
      data.consent_text = Array.prototype.map.call(
        form.querySelectorAll('.consent'),
        function (l) { var c = l.querySelector('input'); return (c && c.checked ? '[x] ' : '[ ] ') + l.textContent.trim().replace(/\s+/g, ' '); }
      );
      if (window.mbCheckAnswers && form.hasAttribute('data-with-answers')) data.answers = window.mbCheckAnswers();
      data.page = location.pathname;
      data.ref = myRef();
      data.came_from = get('sessionStorage', 'mb_came_from') || '';
      ['utm_source', 'utm_medium', 'utm_campaign'].forEach(function (k) { if (params.get(k)) data[k] = params.get(k); });

      btn.disabled = true;
      msg.className = 'form-msg';
      msg.textContent = 'Sending...';
      fetch('/api/lead', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
        .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
        .then(function () {
          track('lead_submit', { type: data.type });
          var next = form.getAttribute('data-next');
          if (next) { location.href = next + (next.indexOf('?') < 0 ? '?' : '&') + 't=' + encodeURIComponent(data.type); return; }
          form.reset();
          msg.className = 'form-msg ok';
          msg.textContent = form.getAttribute('data-ok') || 'Thank you. Check your inbox.';
          btn.disabled = false;
        })
        .catch(function () {
          msg.className = 'form-msg err';
          msg.innerHTML = 'That did not go through. Please email <a href="mailto:' + CFG.email + '">' + CFG.email + '</a> and we will add you by hand.';
          btn.disabled = false;
        });
    });
  });
  }
  window.mbBindForms = bindForms;
  bindForms(document);

  /* ---------- share widgets ---------- */
  // <div data-share data-path="/check/" data-text="..."></div>
  function buildShare(box) {
    var path = box.getAttribute('data-path') || '/check/';
    var text = box.getAttribute('data-text') || '';
    var title = box.getAttribute('data-title') || document.title;
    var where = box.getAttribute('data-where') || 'page';
    function url(m) { return shareUrl(path, m); }
    function done(ch) { track('share_click', { channel: ch, where: where }); }
    var html = '';
    if (navigator.share) html += '<button type="button" class="primary" data-ch="native">Share</button>';
    html += '<a data-ch="sms" href="sms:?&body=' + encodeURIComponent(text + ' ' + url('sms')) + '">Text it</a>';
    html += '<a data-ch="email" href="mailto:?subject=' + encodeURIComponent(title) + '&body=' + encodeURIComponent(text + '\n\n' + url('email')) + '">Email</a>';
    html += '<a data-ch="whatsapp" target="_blank" rel="noopener" href="https://wa.me/?text=' + encodeURIComponent(text + ' ' + url('whatsapp')) + '">WhatsApp</a>';
    html += '<a data-ch="facebook" target="_blank" rel="noopener" href="https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(url('facebook')) + '">Facebook</a>';
    html += '<button type="button" data-ch="copy">Copy for Nextdoor</button>';
    box.innerHTML = '<div class="share">' + html + '</div><p class="small muted mt0" style="margin-top:.6rem" aria-live="polite"></p>';
    var note = box.querySelector('p');
    box.addEventListener('click', function (ev) {
      var el = ev.target.closest('[data-ch]');
      if (!el) return;
      var ch = el.getAttribute('data-ch');
      done(ch);
      if (ch === 'native') {
        navigator.share({ title: title, text: text, url: url('native') }).catch(function () {});
      } else if (ch === 'copy') {
        var t = text + '\n\n' + url('nextdoor');
        (navigator.clipboard ? navigator.clipboard.writeText(t) : Promise.reject()).then(
          function () { note.textContent = 'Copied. Paste it into Nextdoor, a group chat, or your HOA list.'; },
          function () { note.textContent = t; }
        );
      }
    });
  }
  document.querySelectorAll('[data-share]').forEach(buildShare);
  window.mbBuildShare = buildShare;

  // Show the visitor's personal link wherever [data-reflink] appears.
  document.querySelectorAll('[data-reflink]').forEach(function (el) {
    el.textContent = shareUrl(el.getAttribute('data-reflink') || '/check/', 'link');
  });
})();
