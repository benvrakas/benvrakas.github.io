// Lightbox for gallery images and click-to-load YouTube embeds.
(() => {
  const lb = document.getElementById('lightbox');
  const lbImg = lb && lb.querySelector('img');
  document.addEventListener('click', (e) => {
    const a = e.target.closest('a.lb');
    if (a && lb) {
      e.preventDefault();
      lbImg.src = a.href;
      lbImg.alt = a.querySelector('img')?.alt || '';
      lb.hidden = false;
      return;
    }
    if (lb && !lb.hidden && (e.target === lb || e.target.tagName === 'BUTTON')) { lb.hidden = true; lbImg.src = ''; }
    const yt = e.target.closest('.yt-lite');
    if (yt) {
      const f = document.createElement('iframe');
      f.src = `https://www.youtube-nocookie.com/embed/${yt.dataset.id}?autoplay=1&rel=0`;
      f.allow = 'autoplay; encrypted-media; picture-in-picture';
      f.allowFullscreen = true;
      f.title = yt.getAttribute('aria-label') || 'Video';
      yt.replaceWith(f);
    }
  });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && lb) { lb.hidden = true; } });
})();
