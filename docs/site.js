// Project filters, gallery lightbox (with prev/next + keyboard), click-to-load YouTube.
(() => {
  // filters (home grid + timeline)
  const bar = document.querySelector('.filters');
  if (bar) {
    const apply = (f) => {
      bar.querySelectorAll('button').forEach((b) => b.classList.toggle('on', b.dataset.f === f));
      document.querySelectorAll('[data-areas]').forEach((el) => {
        el.hidden = f !== 'all' && !el.dataset.areas.split(' ').includes(f);
      });
      try { sessionStorage.setItem('bv-filter', f); } catch (e) {}
    };
    bar.addEventListener('click', (e) => { const b = e.target.closest('button'); if (b) apply(b.dataset.f); });
    let saved = 'all';
    try { saved = sessionStorage.getItem('bv-filter') || 'all'; } catch (e) {}
    if (bar.querySelector(`[data-f="${saved}"]`)) apply(saved);
  }

  // lightbox
  const lb = document.getElementById('lightbox');
  const img = lb.querySelector('img'), cap = lb.querySelector('figcaption');
  let set = [], idx = 0;
  const show = (i) => {
    idx = (i + set.length) % set.length;
    img.src = set[idx].href; img.alt = set[idx].dataset.cap || '';
    cap.textContent = set[idx].dataset.cap || '';
    lb.hidden = false;
  };
  const close = () => { lb.hidden = true; img.src = ''; };
  document.addEventListener('click', (e) => {
    const a = e.target.closest('a.lb');
    if (a) {
      e.preventDefault();
      set = [...a.closest('.prose, main').querySelectorAll('a.lb')];
      show(set.indexOf(a));
      return;
    }
    if (!lb.hidden) {
      if (e.target.closest('.lbn')) return show(idx + 1);
      if (e.target.closest('.lbp')) return show(idx - 1);
      if (e.target === lb || e.target.closest('.lbx')) return close();
    }
    const yt = e.target.closest('.yt-lite');
    if (yt) {
      const f = document.createElement('iframe');
      f.src = `https://www.youtube-nocookie.com/embed/${yt.dataset.id}?autoplay=1&rel=0`;
      f.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
      f.allowFullscreen = true;
      f.title = yt.getAttribute('aria-label') || 'Video';
      yt.replaceWith(f);
    }
  });
  document.addEventListener('keydown', (e) => {
    if (lb.hidden) return;
    if (e.key === 'Escape') close();
    if (e.key === 'ArrowRight') show(idx + 1);
    if (e.key === 'ArrowLeft') show(idx - 1);
  });

  // highlight current section in project sidebar
  const toc = document.querySelectorAll('.toc a');
  if (toc.length && 'IntersectionObserver' in window) {
    const map = new Map([...toc].map((a) => [a.getAttribute('href').slice(1), a]));
    const obs = new IntersectionObserver((ents) => {
      ents.forEach((en) => {
        if (en.isIntersecting) {
          toc.forEach((a) => a.classList.remove('on'));
          map.get(en.target.id)?.classList.add('on');
        }
      });
    }, { rootMargin: '-20% 0px -70% 0px' });
    document.querySelectorAll('.prose h2[id]').forEach((h) => obs.observe(h));
  }
})();
