(() => {
  const menu = document.querySelector('.mobile-menu');
  const nav = document.querySelector('#primary-nav');
  if (menu && nav) {
    menu.addEventListener('click', () => {
      const open = nav.classList.toggle('open');
      menu.setAttribute('aria-expanded', String(open));
      menu.setAttribute('aria-label', open ? 'メニューを閉じる' : 'メニューを開く');
      menu.textContent = open ? '×' : '☰';
    });
    nav.addEventListener('click', event => {
      if (event.target.closest('a')) {
        nav.classList.remove('open');
        menu.setAttribute('aria-expanded', 'false');
      }
    });
  }

  const listing = document.querySelector('[data-listing]');
  if (listing) {
    const input = listing.querySelector('#article-search');
    const tiles = [...listing.querySelectorAll('.article-tile')];
    const filters = [...listing.querySelectorAll('.article-filter')];
    const count = listing.querySelector('#results-count');
    const empty = listing.querySelector('#empty-results');
    const normalize = text => String(text || '').normalize('NFKC').toLocaleLowerCase('ja-JP').replace(/\s+/g, ' ').trim();
    const params = new URLSearchParams(location.search);
    if (input && params.has('q')) input.value = params.get('q') || '';

    const update = () => {
      const words = normalize(input?.value || '').split(' ').filter(Boolean);
      let visible = 0;
      for (const tile of tiles) {
        const text = normalize([tile.dataset.title, tile.dataset.summary, tile.dataset.tags, tile.dataset.character, tile.dataset.stage].join(' '));
        const matches = words.every(word => text.includes(word)) && filters.every(filter => !filter.value || tile.dataset[filter.dataset.field] === filter.value);
        tile.hidden = !matches;
        if (matches) visible++;
      }
      if (count) count.textContent = String(visible);
      if (empty) empty.hidden = visible > 0;
      const url = new URL(location.href);
      if (input?.value.trim()) url.searchParams.set('q', input.value.trim());
      else url.searchParams.delete('q');
      // file:// previews cannot rewrite a file URL as a server route.
      if (location.protocol !== 'file:') {
        history.replaceState(null, '', url.pathname + url.search + url.hash);
      }
    };
    input?.addEventListener('input', update);
    filters.forEach(filter => filter.addEventListener('change', update));
    update();
    document.addEventListener('keydown', event => {
      if (event.key === '/' && input && !/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement?.tagName || '')) {
        event.preventDefault(); input.focus();
      }
    });
  }

  const tocLinks = [...document.querySelectorAll('.toc a')];
  if (tocLinks.length && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          tocLinks.forEach(a => a.classList.toggle('active', a.hash === '#' + entry.target.id));
        }
      }
    }, {rootMargin: '-110px 0px -70% 0px'});
    tocLinks.forEach(a => {
      const heading = document.querySelector(a.hash);
      if (heading) observer.observe(heading);
    });
  }
})();
