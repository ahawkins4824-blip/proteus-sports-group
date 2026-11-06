(() => {
  'use strict';

  const menuToggle = document.getElementById('menu-toggle');
  const mobileMenu = document.getElementById('mobile-menu');

  if (menuToggle && mobileMenu) {
    const setMenuOpen = (open, returnFocus = false) => {
      menuToggle.setAttribute('aria-expanded', String(open));
      menuToggle.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
      mobileMenu.hidden = !open;
      document.body.classList.toggle('menu-open', open);
      if (returnFocus) menuToggle.focus();
    };

    menuToggle.addEventListener('click', () => {
      const open = menuToggle.getAttribute('aria-expanded') !== 'true';
      setMenuOpen(open);
      if (open) mobileMenu.querySelector('a, button')?.focus();
    });

    mobileMenu.addEventListener('click', (event) => {
      if (event.target.closest('a')) setMenuOpen(false);
    });

    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && !mobileMenu.hidden) {
        setMenuOpen(false, true);
      }
    });

    document.addEventListener('click', (event) => {
      if (!mobileMenu.hidden && !mobileMenu.contains(event.target) &&
          !menuToggle.contains(event.target)) {
        setMenuOpen(false);
      }
    });

    const desktop = window.matchMedia('(min-width: 901px)');
    desktop.addEventListener('change', (event) => {
      if (event.matches) setMenuOpen(false);
    });
    if (desktop.matches) setMenuOpen(false);
  }

  const filters = document.querySelector('[data-programme-filters]');
  if (filters) {
    const cards = [...document.querySelectorAll('[data-programme-card]')];
    const buttons = [...filters.querySelectorAll('[data-filter]')];
    const count = document.getElementById('programme-count');
    const empty = document.getElementById('programmes-empty');

    const applyFilter = (filter) => {
      let visible = 0;
      cards.forEach((card) => {
        const audiences = (card.dataset.audience || '').split(/\s+/);
        card.hidden = filter !== 'all' && !audiences.includes(filter);
        if (!card.hidden) visible += 1;
      });
      buttons.forEach((button) => {
        button.setAttribute('aria-pressed', String(button.dataset.filter === filter));
      });
      if (count) count.textContent = `${visible} programme${visible === 1 ? '' : 's'}`;
      if (empty) empty.hidden = visible > 0;
    };

    filters.addEventListener('click', (event) => {
      const button = event.target.closest('[data-filter]');
      if (button && filters.contains(button)) applyFilter(button.dataset.filter);
    });
    applyFilter('all');
  }

  const form = document.getElementById('enquiry-form');
  if (form) {
    const interest = form.elements.namedItem('interest');
    const summary = document.getElementById('enquiry-summary');
    const preview = document.getElementById('enquiry-preview');
    const emailLink = document.getElementById('enquiry-email');
    const copyButton = document.getElementById('copy-enquiry');
    const copyStatus = document.getElementById('copy-status');
    const normalise = (value) => value.toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
    const query = new URLSearchParams(window.location.search);
    const requested = query.get('interest') || query.get('programme');
    const aliases = {
      'individual-performance-coaching': 'Individual & Performance Coaching',
      'academy': 'Proteus Academy',
      'early-years-fundamentals': 'Early Years & Fundamentals',
      'school-sports-coaching': 'School Sports & Coaching',
      'holiday-programmes': 'Holiday Programmes',
      'coach-development': 'Coach Development',
    };

    if (interest && requested) {
      const candidates = [requested, aliases[requested]].filter(Boolean).map(normalise);
      const option = [...interest.options].find((item) =>
        candidates.includes(normalise(item.value)) ||
        candidates.includes(normalise(item.textContent)));
      if (option) interest.value = option.value;
    }

    const valueOf = (name) => String(form.elements.namedItem(name)?.value || '').trim();

    form.addEventListener('submit', (event) => {
      event.preventDefault();
      if (!form.reportValidity() || !summary || !preview || !emailLink) return;

      const selectedInterest = interest?.selectedOptions?.[0]?.textContent.trim() || valueOf('interest');
      const topic = selectedInterest || 'General enquiry';
      const recipient = topic === 'Academy — football' ? 'oliver@proteus.nz'
        : topic === 'Academy — basketball' ? 'isaac@proteus.nz'
        : 'info@proteus.nz';
      const subject = `Website enquiry — ${topic}`;
      const message = [
        'Kia ora Proteus team,',
        '',
        valueOf('message'),
        '',
        `Programme: ${topic}`,
        `Name: ${valueOf('name')}`,
        `Email: ${valueOf('email')}`,
      ].join('\n');

      summary.value = message;
      emailLink.href = `mailto:${recipient}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(message)}`;
      preview.hidden = false;
      if (copyStatus) copyStatus.textContent = '';
      const heading = preview.querySelector('h2, h3, [data-preview-heading]');
      if (heading) {
        heading.setAttribute('tabindex', '-1');
        heading.focus({ preventScroll: true });
      }
      preview.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'nearest' });
    });

    copyButton?.addEventListener('click', async () => {
      if (!summary) return;
      try {
        if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
        await navigator.clipboard.writeText(summary.value);
        if (copyStatus) copyStatus.textContent = 'Enquiry copied. You can paste it into your email.';
      } catch {
        summary.focus();
        summary.select();
        if (copyStatus) copyStatus.textContent = 'Select and copy the enquiry text, then paste it into your email.';
      }
    });
  }

  const copyEmail = document.getElementById('copy-email');
  copyEmail?.addEventListener('click', async () => {
    const address = copyEmail.dataset.email || 'info@proteus.nz';
    const status = document.getElementById('copy-email-status');
    try {
      if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(address);
      if (status) status.textContent = 'Email address copied.';
    } catch {
      if (status) status.textContent = `Email us at ${address}`;
    }
  });

  const header = document.querySelector('.site-header');
  if (header) {
    let scheduled = false;
    const updateHeader = () => {
      header.classList.toggle('is-scrolled', window.scrollY > 12);
      scheduled = false;
    };
    window.addEventListener('scroll', () => {
      if (!scheduled) {
        scheduled = true;
        window.requestAnimationFrame(updateHeader);
      }
    }, { passive: true });
    updateHeader();
  }
})();
