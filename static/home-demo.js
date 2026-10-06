// Home demo window: plays one conversation per life moment.
// The question types in, the assistant "reads" its sources, then the answer and source chips appear.
(function () {
  var win = document.querySelector('.demo-window');
  if (!win) return;
  var script = JSON.parse(win.dataset.script);
  var tabs = Array.from(win.querySelectorAll('.demo-tab'));
  var topic = win.querySelector('.demo-window-topic');
  var q = win.querySelector('.demo-q');
  var readingSrc = win.querySelector('.demo-reading-src');
  var a = win.querySelector('.demo-a');
  var chips = win.querySelector('.demo-chips');
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var i = 0, timers = [], paused = false;

  function later(fn, ms) { timers.push(setTimeout(fn, ms)); }
  function clear() { timers.forEach(clearTimeout); timers = []; }
  function type(el, text, ms, done) {
    var n = 0;
    (function step() {
      el.textContent = text.slice(0, ++n);
      if (n < text.length) later(step, ms); else if (done) done();
    })();
  }

  function render(k, animate) {
    clear();
    i = k;
    win.dataset.topic = String(k + 1);
    var c = script[k];
    tabs.forEach(function (t, j) {
      t.classList.toggle('is-active', j === k);
      t.setAttribute('aria-pressed', j === k ? 'true' : 'false');
    });
    topic.textContent = tabs[k].lastChild.textContent;
    readingSrc.textContent = c.src.join(' · ');
    chips.replaceChildren.apply(chips, c.src.map(function (d) {
      var s = document.createElement('span'); s.className = 'demo-chip'; s.textContent = d; return s;
    }));
    if (!animate) { q.textContent = c.q; a.textContent = c.a; win.dataset.phase = 'done'; return; }
    win.dataset.phase = 'asking';
    q.textContent = ''; a.textContent = '';
    type(q, c.q, 28, function () {
      later(function () {
        win.dataset.phase = 'reading';
        later(function () {
          win.dataset.phase = 'answering';
          type(a, c.a, 9, function () {
            win.dataset.phase = 'done';
            if (!paused) later(function () { render((i + 1) % script.length, true); }, 5200);
          });
        }, 1400);
      }, 350);
    });
  }

  tabs.forEach(function (t, k) { t.addEventListener('click', function () { paused = true; render(k, !reduced); }); });
  if (reduced || !('IntersectionObserver' in window)) { render(0, false); return; }
  // Start when the window scrolls into view, so the first conversation is not missed.
  new IntersectionObserver(function (entries, io) {
    if (entries[0].isIntersecting) { io.disconnect(); later(function () { render(0, true); }, 400); }
  }, { threshold: 0.4 }).observe(win);
})();
