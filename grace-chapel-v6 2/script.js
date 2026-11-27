
const toggle = document.querySelector('.menu-toggle');
const nav = document.getElementById('nav');

if (nav) {
  // Add the Gospel page to the navigation.
  if (!nav.querySelector('a[href="gospel.html"]')) {
    const gospelLink = document.createElement('a');
    gospelLink.href = 'gospel.html';
    gospelLink.textContent = 'What Is the Gospel?';

    const beliefsLink = nav.querySelector('a[href="beliefs.html"]');

    if (beliefsLink) {
      beliefsLink.after(gospelLink);
    } else {
      nav.appendChild(gospelLink);
    }
  }

  // Highlight the Gospel link when viewing that page.
  if (/\/gospel(?:\.html)?\/?$/.test(window.location.pathname)) {
    const gospelLink = nav.querySelector('a[href="gospel.html"]');

    if (gospelLink) {
      gospelLink.setAttribute('aria-current', 'page');
    }
  }

  // Add the Contact link to every page.
  if (!nav.querySelector('a[href$="#contact"]')) {
    const contactLink = document.createElement('a');
    contactLink.href = 'index.html#contact';
    contactLink.textContent = 'Contact';

    nav.appendChild(contactLink);
  }
}

// Add the church email address to the footer.
const footer = document.querySelector('footer');
const churchEmail = 'goodnews4folkestone@outlook.com';

if (footer && !footer.querySelector(`a[href="mailto:${churchEmail}"]`)) {
  const emailParagraph = document.createElement('p');
  emailParagraph.style.overflowWrap = 'anywhere';

  const emailLink = document.createElement('a');
  emailLink.href = `mailto:${churchEmail}`;
  emailLink.textContent = churchEmail;

  emailParagraph.appendChild(emailLink);

  const footerDetails = Array.from(footer.children).find(
    element => element.tagName === 'DIV' &&
    !element.classList.contains('brand')
  );

  if (footerDetails) {
    const firstParagraph = footerDetails.querySelector('p');

    if (firstParagraph) {
      firstParagraph.after(emailParagraph);
    } else {
      footerDetails.appendChild(emailParagraph);
    }
  } else {
    footer.appendChild(emailParagraph);
  }
}

// Mobile navigation.
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
