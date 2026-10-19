/* 2-minute DMV rebate checker. Anonymous until the visitor chooses to email the summary.
   Every amount shown is quoted from window.FACTS (official source + checked date). */
(function () {
  var F = window.FACTS;
  var form = document.getElementById('quiz');
  if (!F || !form) return;
  var steps = Array.prototype.slice.call(form.querySelectorAll('.q'));
  var back = document.getElementById('q-back');
  var next = document.getElementById('q-next');
  var bar = document.getElementById('q-bar');
  var out = document.getElementById('results');
  var i = 0;
  var started = false;

  function val(name) {
    var el = form.querySelector('input[name="' + name + '"]:checked');
    return el ? el.value : '';
  }
  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; });
  }
  function fmtDate(iso) {
    return new Date(iso + 'T12:00:00').toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  }

  // Steps that apply given the answers so far (DC has one electric utility; skip that step).
  function active() {
    return steps.filter(function (s) {
      var only = s.getAttribute('data-only');
      return !only || only.split(' ').indexOf(val('where')) >= 0;
    });
  }

  function show() {
    var list = active();
    steps.forEach(function (s) { s.hidden = s !== list[i]; });
    back.hidden = i === 0;
    next.textContent = i === list.length - 1 ? 'See my results' : 'Next';
    bar.style.width = Math.round((i + 1) / (list.length + 1) * 100) + '%';
  }

  function advance() {
    var list = active();
    var cur = list[i];
    if (cur.querySelector('input[type=radio]') && !cur.querySelector('input:checked')) {
      cur.querySelector('.hint').textContent = 'Pick one to keep going.';
      return;
    }
    if (!started) { started = true; window.mbTrack && window.mbTrack('check_start'); }
    if (val('where') === 'other') { results(); return; }
    if (i < list.length - 1) { i++; show(); window.scrollTo({ top: form.offsetTop - 80, behavior: 'smooth' }); }
    else results();
  }

  next.addEventListener('click', advance);
  back.addEventListener('click', function () { if (i > 0) { i--; show(); } });
  form.addEventListener('change', function (ev) {
    if (ev.target.type === 'radio') setTimeout(advance, 200);
  });

  function answers() {
    return {
      where: val('where'), utility: val('utility'), heat: val('heat'),
      project: val('project'), home: val('home'), income: val('income'), timeline: val('timeline')
    };
  }
  window.mbCheckAnswers = function () {
    // Income answer is a yes/no about showing programs, never a number; it is not sent.
    var a = answers(); delete a.income; a.matched = matched(a).map(function (p) { return p.id; }); return a;
  };

  var ORDER = { open: 0, ending: 0, review: 1, upcoming: 2, 'not-launched': 3, closed: 4, ended: 5 };
  var LABEL = { open: 'In effect', ending: 'Ending', review: 'Under review', upcoming: 'Not yet live', 'not-launched': 'Not yet live', closed: 'Expired', ended: 'Expired' };

  function matched(a) {
    var fuel = a.heat === 'oil' ? 'oil' : a.heat === 'gas' ? 'gas' : 'other';
    return F.programs.filter(function (p) {
      if (p.juris !== a.where && p.juris !== 'ALL') return false;
      if (p.kinds.indexOf(a.project || 'unsure') < 0) return false;
      if (p.utilities && a.utility && a.utility !== 'unsure' && p.utilities.indexOf(a.utility) < 0) return false;
      if (p.fuels && a.heat !== 'unsure' && p.fuels.indexOf(fuel) < 0) return false;
      if (p.income && a.income !== 'yes') return false;
      return true;
    }).sort(function (x, y) { return ORDER[x.status] - ORDER[y.status]; });
  }

  function card(p) {
    var checked = F.checked[p.juris] || F.checked.MD;
    var src = p.sources.map(function (s) {
      return '<li><a href="' + esc(s.url) + '" target="_blank" rel="noopener" data-official="' + esc(p.id) + '">' + esc(s.label) + '</a></li>';
    }).join('');
    return '<article class="card prog-card st-' + p.status + '">' +
      '<p class="mt0"><span class="badge badge-' + p.status + '">' + LABEL[p.status] + '</span></p>' +
      '<h3>' + esc(p.name) + '</h3>' +
      '<p class="amount">' + esc(p.amount) + '</p>' +
      '<p class="small">' + esc(p.status_note) + '</p>' +
      '<p class="small muted">' + esc(p.note) + '</p>' +
      '<details><summary class="small">Official sources (checked ' + fmtDate(checked) + ')</summary><ul class="small">' + src + '</ul></details>' +
      '</article>';
  }

  function deadlineList(a) {
    var today = new Date().toISOString().slice(0, 10);
    var list = F.deadlines.filter(function (d) {
      return d.juris === a.where && (d.end || d.date) >= today;
    });
    if (a.where === 'MD' && a.utility && a.utility !== 'unsure') {
      list = list.filter(function (d) {
        var t = d.title;
        if (/^Pepco and Delmarva/.test(t)) return a.utility === 'Pepco' || a.utility === 'Delmarva Power';
        if (/^Pepco Home/.test(t)) return a.utility === 'Pepco';
        if (/^Potomac Edison/.test(t)) return a.utility === 'Potomac Edison';
        if (/^Washington Gas/.test(t)) return a.heat === 'gas' || a.heat === 'unsure';
        return true;
      });
    }
    if (!list.length) return '';
    return '<h2 class="mt">Dates that matter for you</h2><ul class="deadlines">' + list.map(function (d) {
      var dt = new Date(d.date + 'T12:00:00');
      return '<li class="dl-' + d.status + '"><div class="dl-date"><small>' + dt.toLocaleDateString('en-US', { month: 'short' }) + '</small><span>' + dt.getDate() + '</span></div>' +
        '<div><h3>' + esc(d.title) + '</h3><p>' + esc(d.detail) + '</p>' +
        '<p class="src">Source: <a href="' + esc(d.source.url) + '" target="_blank" rel="noopener" data-official="deadline">' + esc(d.source.label) + '</a>, checked ' + fmtDate(F.checked[d.juris]) + '</p></div></li>';
    }).join('') + '</ul>';
  }

  function results() {
    var a = answers();
    window.mbTrack && window.mbTrack('check_complete', { where: a.where, project: a.project || 'unsure' });
    var html = '';

    if (a.where === 'other') {
      html = '<div class="result-head"><h2>We only cover DC, Maryland and Northern Virginia for now.</h2>' +
        '<p>Get a note when we add your area. We only email if you say yes.</p></div>';
      out.innerHTML = html + document.getElementById('tpl-alerts').innerHTML;
      finish();
      return;
    }

    var list = matched(a);
    var live = list.filter(function (p) { return p.status === 'open' || p.status === 'ending'; });
    var ending = list.filter(function (p) { return p.status === 'ending'; });
    var place = { MD: 'Maryland', DC: 'DC', VA: 'Northern Virginia' }[a.where];

    html += '<div class="result-head"><p class="eyebrow" style="color:#9fb0c0">Your results for ' + place + '</p>' +
      '<h2>' + live.length + ' program' + (live.length === 1 ? '' : 's') + ' may fit your home right now.</h2>' +
      '<p>' + (ending.length ? ending.length + ' of them ' + (ending.length === 1 ? 'has' : 'have') + ' an end date coming up. ' : '') +
      'Each program decides who qualifies and how much it pays. Below is what each one says, in its own words, with a link to check it yourself.</p></div>';

    if (a.home === 'building') {
      html += '<div class="callout callout-info mt"><b>Managing a building of 5+ units?</b> Building rules and programs are different. <a href="/buildings/">See the building guide</a>.</div>';
    }
    if (a.home === 'rent') {
      html += '<div class="callout callout-info mt"><b>Renting?</b> Most of these need the owner to sign off. Send this page to your landlord. The share buttons below make it easy.</div>';
    }
    if (a.where === 'MD' && (a.utility === 'Pepco' || a.utility === 'Delmarva Power') && (a.heat === 'gas' || a.heat === 'oil') && a.timeline !== 'later') {
      html += '<div class="callout callout-warn mt"><b>Switching from ' + (a.heat === 'gas' ? 'gas' : 'oil or propane') + ' in ' + esc(a.utility) + ' territory?</b> The higher switching amounts need the install finished by Nov 30, 2026 <span class="days-left" data-days-until="2026-11-30"></span>. Ask your contractor about timing in writing.</div>';
    }

    html += '<div class="grid mt">' + list.map(card).join('') + '</div>';
    if (!list.length) html += '<p class="mt">No programs match these answers today. Alerts are the best next step. We will email you when something opens.</p>';

    html += deadlineList(a);
    html += document.getElementById('tpl-plan').innerHTML;
    html += document.getElementById('tpl-next').innerHTML;
    out.innerHTML = html;
    finish();
  }

  function finish() {
    form.hidden = true;
    document.getElementById('quiz-intro').hidden = true;
    out.hidden = false;
    out.querySelectorAll('[data-share]').forEach(window.mbBuildShare);
    out.querySelectorAll('[data-days-until]').forEach(function (el) {
      var days = Math.ceil((new Date(el.getAttribute('data-days-until') + 'T23:59:59-05:00') - new Date()) / 86400000);
      el.textContent = days > 0 ? '(' + days + ' days left)' : '';
    });
    window.mbBindForms(out);
    window.scrollTo({ top: out.offsetTop - 80, behavior: 'smooth' });
  }

  show();
})();
