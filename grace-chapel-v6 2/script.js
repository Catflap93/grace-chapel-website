
const toggle = document.querySelector('.menu-toggle');
const nav = document.getElementById('nav');

if (nav) {
  // Add the Gospel page to the navigation if it isn't already there.
  if (!nav.querySelector('a[href="gospel.html"]')) {
    const gospelLink = document.createElement('a');
    gospelLink.href = 'gospel.html';
    gospelLink.textContent = 'What Is the Gospel?';

    // Place it immediately after What We Believe.
    const beliefsLink = nav.querySelector('a[href="beliefs.html"]');

    if (beliefsLink) {
      beliefsLink.after(gospelLink);
    } else {
      nav.appendChild(gospelLink);
    }
  }

  // Highlight the Gospel link when viewing that page.
  if (window.location.pathname.endsWith('/gospel.html')) {
    const gospelLink = nav.querySelector('a[href="gospel.html"]');
    if (gospelLink) {
      gospelLink.setAttribute('aria-current', 'page');
    }
  }
}

if (toggle && nav) {
  toggle.addEventListener('click', () => {
    const open = nav.classList.toggle('open');
    toggle.setAttribute('aria-expanded', String(open));
  });

  nav.querySelectorAll('a').forEach(a => {
    a.addEventListener('click', () => {
      nav.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
    });
  });
}
