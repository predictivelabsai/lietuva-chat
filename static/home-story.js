// Home scroll behaviour: card reveals, heading fades, bento count-up and the life-moments
// row that drifts sideways. Everything settles to its final state under
// reduced motion.
(function () {
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var narrow = window.matchMedia('(max-width: 768px)');
  document.documentElement.classList.add('js');

  // Reveal cards and fade headings once, as they arrive.
  var arriving = document.querySelectorAll('.reveal, .fade');
  if (reduced || !('IntersectionObserver' in window)) {
    arriving.forEach(function (el) { el.classList.add('in'); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        e.target.classList.add('in');
        io.unobserve(e.target);
      });
    }, { rootMargin: '0px 0px -10% 0px' });
    arriving.forEach(function (el, i) { el.style.setProperty('--i', i % 6); io.observe(el); });
  }

  // Bento numbers count up once, the first time they are seen.
  var nums = document.querySelectorAll('.bento-num[data-count]');
  if (!reduced && 'IntersectionObserver' in window) {
    var counter = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        counter.unobserve(e.target);
        var el = e.target, to = Number(el.dataset.count), t0 = performance.now();
        (function tick(now) {
          var u = Math.min(1, (now - t0) / 900);
          el.textContent = String(Math.round(to * (1 - Math.pow(1 - u, 4))));
          if (u < 1) requestAnimationFrame(tick);
        })(t0);
      });
    }, { threshold: 0.6 });
    nums.forEach(function (n) { counter.observe(n); });
  }

  var moments = document.getElementById('moments');
  var track = document.getElementById('moments-track');
  var queued = false;

  function frame() {
    queued = false;
    if (narrow.matches) return;
    var vh = window.innerHeight;
    if (moments && track && !reduced) {
      var m = moments.getBoundingClientRect();
      var q = Math.min(1, Math.max(0, (vh - m.top) / (vh + m.height)));
      var max = Math.max(0, track.scrollWidth - track.clientWidth + 48);
      track.style.setProperty('--drift', (q * max).toFixed(1));
    }
  }
  window.addEventListener('scroll', function () { if (!queued) { queued = true; requestAnimationFrame(frame); } }, { passive: true });
  window.addEventListener('resize', frame);
  frame();
})();
