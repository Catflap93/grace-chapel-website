
(() => {
  const $ = id => document.getElementById(id);
  let all = [];

  const bibleBooks = [
    'Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy',
    'Joshua', 'Judges', 'Ruth', '1 Samuel', '2 Samuel',
    '1 Kings', '2 Kings', '1 Chronicles', '2 Chronicles',
    'Ezra', 'Nehemiah', 'Esther', 'Job', 'Psalms',
    'Proverbs', 'Ecclesiastes', 'Song of Solomon', 'Isaiah',
    'Jeremiah', 'Lamentations', 'Ezekiel', 'Daniel', 'Hosea',
    'Joel', 'Amos', 'Obadiah', 'Jonah', 'Micah', 'Nahum',
    'Habakkuk', 'Zephaniah', 'Haggai', 'Zechariah', 'Malachi',
    'Matthew', 'Mark', 'Luke', 'John', 'Acts', 'Romans',
    '1 Corinthians', '2 Corinthians', 'Galatians', 'Ephesians',
    'Philippians', 'Colossians', '1 Thessalonians',
    '2 Thessalonians', '1 Timothy', '2 Timothy', 'Titus',
    'Philemon', 'Hebrews', 'James', '1 Peter', '2 Peter',
    '1 John', '2 John', '3 John', 'Jude', 'Revelation'
  ];

  const escape = s => String(s ?? '').replace(
    /[&<>"']/g,
    c => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;'
    }[c])
  );

  const date = s => s
    ? new Date(s + 'T12:00:00').toLocaleDateString('en-GB', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
      })
    : 'Date not specified';

  const thumb = id =>
    `https://i.ytimg.com/vi/${encodeURIComponent(id)}/hqdefault.jpg`;

  const card = s => `
    <article class="library-card">
      <button
        type="button"
        data-watch="${escape(s.id)}"
        class="sermon-image"
        aria-label="Watch ${escape(s.title)}"
      >
        <img loading="lazy" src="${thumb(s.id)}" alt="">
        <span class="play-mark">▶</span>
      </button>

      <div class="sermon-card-body">
        <p class="eyebrow">${escape(s.book || 'SERMON')}</p>
        <h3>${escape(s.title)}</h3>

        <p class="sermon-meta">
          ${escape(s.preacher || 'Preacher not specified')}
          · ${date(s.preached)}
        </p>

        <p class="sermon-excerpt">
          ${escape((s.description || '').slice(0, 160))}
          ${(s.description || '').length > 160 ? '…' : ''}
        </p>

        <button class="watch-link" data-watch="${escape(s.id)}">
          Watch sermon →
        </button>
      </div>
    </article>
  `;

  function openSermon(id) {
    const s = all.find(x => x.id === id);
    if (!s) return;

    $('dialog-title').textContent = s.title;

    $('dialog-meta').textContent = [
      s.preacher,
      date(s.preached)
    ].filter(Boolean).join(' · ');

    $('dialog-description').textContent = s.description || '';

    $('dialog-youtube').href =
      'https://www.youtube.com/watch?v=' + encodeURIComponent(id);

    $('sermon-player').innerHTML = `
      <iframe
        title="${escape(s.title)}"
        src="https://www.youtube-nocookie.com/embed/${encodeURIComponent(id)}?autoplay=1"
        allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture"
        allowfullscreen
        referrerpolicy="strict-origin-when-cross-origin"
      ></iframe>
    `;

    $('sermon-dialog').showModal();
  }

  function close() {
    $('sermon-dialog').close();
    $('sermon-player').replaceChildren();
  }

  function render() {
    const q = $('sermon-search').value.trim().toLowerCase();
    const b = $('book-filter').value;
    const p = $('preacher-filter').value;

    let rows = all.filter(s =>
      (!b || s.book === b) &&
      (!p || s.preacher === p) &&
      [
        s.title,
        s.book,
        s.preacher,
        s.description,
        s.series
      ].join(' ').toLowerCase().includes(q)
    );

    rows.sort((a, b) =>
      $('sermon-sort').value === 'oldest'
        ? (a.preached || '').localeCompare(b.preached || '')
        : (b.preached || '').localeCompare(a.preached || '')
    );

    $('result-count').textContent =
      `${rows.length} sermon${rows.length === 1 ? '' : 's'} found`;

    $('sermon-results').innerHTML = rows.length
      ? rows.map(card).join('')
      : '<p>No sermons match those filters. Try another search.</p>';
  }

  function options(id, field) {
    const values = [
      ...new Set(all.map(x => x[field]).filter(Boolean))
    ];

    if (field === 'book') {
      values.sort((a, b) => {
        const normalized = name =>
          name === 'Psalm' ? 'Psalms' : name;

        const index = name => {
          const i = bibleBooks.indexOf(normalized(name));
          return i === -1 ? 999 : i;
        };

        return index(a) - index(b) || a.localeCompare(b);
      });
    } else {
      values.sort((a, b) => a.localeCompare(b));
    }

    $(id).innerHTML += values.map(v =>
      `<option value="${escape(v)}">${escape(v)}</option>`
    ).join('');
  }

  document.addEventListener('click', e => {
    const b = e.target.closest('[data-watch]');
    if (b) openSermon(b.dataset.watch);
  });

  $('close-sermon').addEventListener('click', close);

  $('sermon-dialog').addEventListener('click', e => {
    if (e.target === $('sermon-dialog')) close();
  });

  $('sermon-dialog').addEventListener('close', () => {
    $('sermon-player').replaceChildren();
  });

  [
    'sermon-search',
    'book-filter',
    'preacher-filter',
    'sermon-sort'
  ].forEach(id => {
    $(id).addEventListener(
      id === 'sermon-search' ? 'input' : 'change',
      render
    );
  });

  fetch('data/sermons.json')
    .then(r => {
      if (!r.ok) throw Error('Catalogue unavailable');
      return r.json();
    })
    .then(d => {
      all = (d.sermons || []).filter(s =>
        /^[a-zA-Z0-9_-]{11}$/.test(s.id)
      );

      options('book-filter', 'book');
      options('preacher-filter', 'preacher');

      $('catalogue-status').textContent =
        `${all.length} recordings in the current catalogue`;

      $('featured-sermon').innerHTML = all.length
        ? `
          <div class="featured-art">
            <img src="${thumb(all[0].id)}" alt="">
          </div>

          <div class="featured-copy">
            <p class="eyebrow">FEATURED SERMON</p>
            <h3>${escape(all[0].title)}</h3>

            <p>
              ${escape(all[0].preacher || '')}
              · ${date(all[0].preached)}
            </p>

            <p>
              ${escape((all[0].description || '').slice(0, 260))}…
            </p>

            <button
              class="button primary"
              data-watch="${escape(all[0].id)}"
            >
              Watch sermon ▶
            </button>
          </div>
        `
        : '';

      render();
    })
    .catch(() => {
      $('catalogue-status').textContent =
        'Could not load the catalogue.';

      $('sermon-results').textContent =
        'Please open this website through a local web server or Cloudflare Pages; browsers may block JSON loading from file://.';
    });
})();
