/* Optional motion for the immersive homepage. All content works without it. */
(() => {
  'use strict';

  const body = document.body;
  if (!body?.classList.contains('home-immersive')) return;

  const revealEverything = () => {
    document.querySelectorAll('.reveal').forEach((element) => element.classList.add('is-visible'));
  };

  try {
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    const motionToggle = document.getElementById('motion-toggle');
    const heroVideo = document.getElementById('hero-motion');
    const heroToggle = document.getElementById('hero-video-toggle');
    const filmDialog = document.getElementById('film-dialog');
    const filmVideo = document.getElementById('film-video');
    const instagramReel = document.getElementById('instagram-reel');
    const readingProgress = document.getElementById('reading-progress');
    const reveals = [...document.querySelectorAll('.reveal')];
    const clamp = (value, minimum = 0, maximum = 1) => Math.min(maximum, Math.max(minimum, value));
    const padded = (value) => String(value).padStart(2, '0');
    let userPaused = false;
    let heroPaused = false;
    let heroVisible = false;
    let heroPlayPending = false;
    let reelVisible = false;
    let frame = 0;
    let lastFilmOpener = null;
    const hasIntersectionObserver = 'IntersectionObserver' in window;

    const motionPaused = () => userPaused || reducedMotion.matches;
    const scrollBehaviour = () => motionPaused() ? 'auto' : 'smooth';
    const isOnScreen = (element) => {
      const rect = element.getBoundingClientRect();
      return rect.height > 0 && rect.width > 0 && rect.bottom > 0 && rect.top < window.innerHeight;
    };

    const canPlayHero = () => Boolean(heroVideo && heroVisible && !heroPaused &&
      !motionPaused() && !document.hidden && !filmDialog?.open);

    const syncHeroVideo = () => {
      if (!heroVideo) return;
      if (!canPlayHero()) {
        heroVideo.pause();
        return;
      }
      if (!heroVideo.paused || heroPlayPending) return;
      heroPlayPending = true;
      const attempt = heroVideo.play();
      Promise.resolve(attempt).then(() => {
        // Preferences or visibility can change while the play request is pending.
        if (!canPlayHero()) heroVideo.pause();
      }).catch(() => {
        // The poster remains a complete hero when autoplay or media loading fails.
      }).finally(() => { heroPlayPending = false; });
    };

    const parallax = [...document.querySelectorAll('[data-parallax]')].map((element) => {
      const speed = Number.parseFloat(element.dataset.parallax);
      return { element, speed: Number.isFinite(speed) ? clamp(speed, -1, 1) : 0.1, offset: 0 };
    });
    const visibleParallax = new Set();

    const carousels = [...document.querySelectorAll('[data-carousel]')].map((element) => {
      const track = element.querySelector('[data-carousel-track]');
      if (!track) return null;
      return {
        element, track,
        slides: [...track.querySelectorAll('[data-slide]')],
        previous: element.querySelector('[data-carousel-prev]'),
        next: element.querySelector('[data-carousel-next]'),
        status: element.querySelector('[data-carousel-status]'),
        progress: element.querySelector('[data-carousel-progress]'),
        dirty: true,
      };
    }).filter(Boolean);

    // Read layout first, then apply visual state. Scroll is never intercepted.
    const updateFrame = () => {
      frame = 0;
      const viewport = window.innerHeight;
      const paused = motionPaused();
      const scrollTop = window.scrollY || document.documentElement.scrollTop;
      const scrollRange = document.documentElement.scrollHeight - viewport;
      const readProgress = scrollRange > 0 ? clamp(scrollTop / scrollRange) : 1;
      const parallaxUpdates = [];
      if (!hasIntersectionObserver && heroVideo) {
        heroVisible = isOnScreen(heroVideo);
        syncHeroVideo();
      }
      if (!hasIntersectionObserver && instagramReel) {
        reelVisible = isOnScreen(instagramReel);
        if (!reelVisible) instagramReel.pause();
      }

      for (const item of parallax) {
        if (paused) {
          if (item.offset !== 0) parallaxUpdates.push([item, 0]);
          continue;
        }
        if (!visibleParallax.has(item.element)) continue;
        const rect = item.element.getBoundingClientRect();
        // Remove the previous offset from the measurement to avoid feedback.
        const center = rect.top - item.offset + rect.height / 2;
        parallaxUpdates.push([item, clamp((viewport / 2 - center) * item.speed, -140, 140)]);
      }

      const carouselUpdates = carousels.filter((carousel) => carousel.dirty).map((carousel) => {
        carousel.dirty = false;
        const maxScroll = Math.max(0, carousel.track.scrollWidth - carousel.track.clientWidth);
        const left = clamp(carousel.track.scrollLeft, 0, maxScroll);
        const start = carousel.track.getBoundingClientRect().left;
        let index = 0;
        let closest = Infinity;
        carousel.slides.forEach((slide, position) => {
          const distance = Math.abs(slide.getBoundingClientRect().left - start);
          if (distance < closest) { closest = distance; index = position; }
        });
        if (maxScroll > 2 && maxScroll - left <= 2) index = Math.max(0, carousel.slides.length - 1);
        return { carousel, index, left, maxScroll };
      });

      readingProgress?.style.setProperty('--read-progress', String(readProgress));
      for (const [item, offset] of parallaxUpdates) {
        item.offset = offset;
        item.element.style.setProperty('--parallax-y', `${offset.toFixed(2)}px`);
      }
      for (const { carousel, index, left, maxScroll } of carouselUpdates) {
        if (carousel.previous) carousel.previous.disabled = left <= 2;
        if (carousel.next) carousel.next.disabled = maxScroll - left <= 2;
        if (carousel.status) {
          const status = `${padded(carousel.slides.length ? index + 1 : 0)} / ${padded(carousel.slides.length)}`;
          if (carousel.status.textContent !== status) carousel.status.textContent = status;
        }
        carousel.progress?.style.setProperty('--carousel-progress', String(maxScroll > 1 ? left / maxScroll : 1));
      }
    };

    const scheduleFrame = () => {
      if (!frame) frame = window.requestAnimationFrame(updateFrame);
    };

    let revealObserver = null;
    if (hasIntersectionObserver) {
      revealObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            revealObserver.unobserve(entry.target);
          }
        });
      }, { rootMargin: '0px 0px -5% 0px', threshold: 0 });
      reveals.forEach((element) => {
        if (motionPaused() || isOnScreen(element)) element.classList.add('is-visible');
        else revealObserver.observe(element);
      });

      const parallaxObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) visibleParallax.add(entry.target);
          else visibleParallax.delete(entry.target);
        });
        scheduleFrame();
      }, { rootMargin: '15% 0px', threshold: 0 });
      parallax.forEach(({ element }) => {
        if (isOnScreen(element)) visibleParallax.add(element);
        parallaxObserver.observe(element);
      });

      if (heroVideo) {
        const heroObserver = new IntersectionObserver((entries) => {
          heroVisible = entries[0]?.isIntersecting || false;
          syncHeroVideo();
        }, { threshold: 0 });
        heroObserver.observe(heroVideo);
      }
      if (instagramReel) {
        const reelObserver = new IntersectionObserver((entries) => {
          reelVisible = entries[0]?.isIntersecting || false;
          if (!reelVisible) instagramReel.pause();
        }, { threshold: 0 });
        reelObserver.observe(instagramReel);
      }
    } else {
      revealEverything();
      parallax.forEach(({ element }) => visibleParallax.add(element));
    }

    const labelButton = (button, text) => {
      if (!button) return;
      (button.querySelector('[data-motion-label]') || button).textContent = text;
    };

    const applyMotionPreference = () => {
      const paused = motionPaused();
      body.classList.toggle('motion-paused', paused);
      body.classList.toggle('motion-reduced', reducedMotion.matches);
      if (motionToggle) {
        motionToggle.setAttribute('aria-pressed', String(paused));
        motionToggle.disabled = reducedMotion.matches;
        labelButton(motionToggle, reducedMotion.matches ? 'Motion reduced' : userPaused ? 'Play motion' : 'Pause motion');
        motionToggle.title = reducedMotion.matches ? 'Your system preference reduces motion.' : '';
      }
      if (heroToggle) {
        const locallyPaused = paused || heroPaused;
        heroToggle.setAttribute('aria-pressed', String(locallyPaused));
        heroToggle.disabled = reducedMotion.matches;
        labelButton(heroToggle, locallyPaused ? 'Play background motion' : 'Pause background motion');
      }
      if (paused) {
        revealEverything();
        revealObserver?.disconnect();
        parallax.forEach((item) => {
          item.offset = 0;
          item.element.style.setProperty('--parallax-y', '0px');
        });
        filmVideo?.pause();
        instagramReel?.pause();
      }
      carousels.forEach((carousel) => { carousel.dirty = true; });
      syncHeroVideo();
      scheduleFrame();
    };

    motionToggle?.addEventListener('click', () => {
      userPaused = !userPaused;
      applyMotionPreference();
    });
    heroToggle?.addEventListener('click', () => {
      heroPaused = !heroPaused;
      applyMotionPreference();
    });
    if (reducedMotion.addEventListener) reducedMotion.addEventListener('change', applyMotionPreference);
    else reducedMotion.addListener(applyMotionPreference);

    if (heroVideo) {
      heroVideo.muted = true;
      heroVideo.defaultMuted = true;
      heroVideo.playsInline = true;
      heroVisible = isOnScreen(heroVideo);
      heroVideo.addEventListener('playing', () => heroVideo.classList.add('is-playing'));
      heroVideo.addEventListener('pause', () => heroVideo.classList.remove('is-playing'));
    }
    if (instagramReel) {
      reelVisible = isOnScreen(instagramReel);
      // Native controls start playback. Visibility changes only ever pause it.
      instagramReel.addEventListener('play', () => {
        if (!reelVisible || document.hidden || filmDialog?.open) instagramReel.pause();
      });
    }

    const moveCarousel = (carousel, direction) => {
      const firstSlide = carousel.slides[0];
      const styles = window.getComputedStyle(carousel.track);
      const gap = Number.parseFloat(styles.columnGap || styles.gap) || 0;
      const distance = firstSlide ? firstSlide.getBoundingClientRect().width + gap : carousel.track.clientWidth;
      carousel.track.scrollBy({ left: distance * direction, behavior: scrollBehaviour() });
    };
    carousels.forEach((carousel) => {
      carousel.previous?.addEventListener('click', () => moveCarousel(carousel, -1));
      carousel.next?.addEventListener('click', () => moveCarousel(carousel, 1));
      carousel.track.addEventListener('scroll', () => {
        carousel.dirty = true;
        scheduleFrame();
      }, { passive: true });
      carousel.track.addEventListener('keydown', (event) => {
        if (event.target !== carousel.track || !['ArrowLeft', 'ArrowRight'].includes(event.key)) return;
        event.preventDefault();
        moveCarousel(carousel, event.key === 'ArrowLeft' ? -1 : 1);
      });
      if ('ResizeObserver' in window) {
        const observer = new ResizeObserver(() => {
          carousel.dirty = true;
          scheduleFrame();
        });
        observer.observe(carousel.track);
      }
    });

    if (filmDialog && typeof filmDialog.showModal === 'function') {
      document.querySelectorAll('[data-open-film]').forEach((opener) => {
        opener.addEventListener('click', () => {
          if (filmDialog.open) return;
          lastFilmOpener = opener;
          filmDialog.showModal();
          body.classList.add('film-open');
          instagramReel?.pause();
          syncHeroVideo();
          filmDialog.querySelector('[data-close-film]')?.focus({ preventScroll: true });
          // This call follows an explicit click; no film playback occurs on scroll.
          if (filmVideo) Promise.resolve(filmVideo.play()).catch(() => {});
        });
      });
      filmDialog.querySelectorAll('[data-close-film]').forEach((button) => {
        button.addEventListener('click', () => filmDialog.close());
      });
      filmDialog.addEventListener('click', (event) => {
        if (event.target !== filmDialog) return;
        const panel = filmDialog.querySelector('.film-dialog-panel') || filmDialog;
        const rect = panel.getBoundingClientRect();
        if (event.clientX < rect.left || event.clientX > rect.right ||
            event.clientY < rect.top || event.clientY > rect.bottom) filmDialog.close();
      });
      filmDialog.addEventListener('close', () => {
        filmVideo?.pause();
        if (filmVideo) {
          try { filmVideo.currentTime = 0; } catch { /* Metadata may not be loaded. */ }
        }
        body.classList.remove('film-open');
        if (lastFilmOpener?.isConnected) lastFilmOpener.focus({ preventScroll: true });
        syncHeroVideo();
      });
    }

    const sportButtons = [...document.querySelectorAll('.academy-switch [data-sport]')];
    const sportLink = document.getElementById('academy-sport-link');
    const sportContact = document.getElementById('academy-sport-contact');
    const sportDescription = document.getElementById('academy-sport-description');
    const otherSportLink = document.getElementById('academy-other-sport');
    const selectSport = (sport) => {
      if (!['football', 'basketball'].includes(sport)) return;
      sportButtons.forEach((button) => button.setAttribute('aria-pressed', String(button.dataset.sport === sport)));
      const email = sport === 'football' ? 'oliver@proteus.nz' : 'isaac@proteus.nz';
      if (sportLink) sportLink.href = `/contact/?interest=${encodeURIComponent(`Academy — ${sport}`)}`;
      if (sportContact) {
        sportContact.textContent = email;
        if (sportContact.tagName === 'A') sportContact.href = `mailto:${email}`;
      }
      if (sportDescription) sportDescription.textContent = `${sport === 'football' ? 'Football' : 'Basketball'} development. Your next step starts here.`;
      if (otherSportLink) {
        const otherSport = sport === 'football' ? 'basketball' : 'football';
        otherSportLink.href = `/contact/?interest=${encodeURIComponent(`Academy — ${otherSport}`)}`;
        otherSportLink.textContent = `enquire about ${otherSport} ↗`;
      }
    };
    sportButtons.forEach((button) => button.addEventListener('click', () => selectSport(button.dataset.sport)));
    if (sportButtons.length) selectSport(sportButtons.find((button) => button.getAttribute('aria-pressed') === 'true')?.dataset.sport || 'football');

    window.addEventListener('scroll', scheduleFrame, { passive: true });
    window.addEventListener('resize', () => {
      carousels.forEach((carousel) => { carousel.dirty = true; });
      if (heroVideo) heroVisible = isOnScreen(heroVideo);
      if (instagramReel) {
        reelVisible = isOnScreen(instagramReel);
        if (!reelVisible) instagramReel.pause();
      }
      syncHeroVideo();
      scheduleFrame();
    }, { passive: true });
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        filmVideo?.pause();
        instagramReel?.pause();
      }
      syncHeroVideo();
      scheduleFrame();
    });
    document.fonts?.ready.then(() => {
      carousels.forEach((carousel) => { carousel.dirty = true; });
      scheduleFrame();
    }).catch(() => {});

    // Set the hiding/enhancement class only after all required setup succeeds.
    applyMotionPreference();
    body.classList.add('motion-ready');
    scheduleFrame();
  } catch {
    body.classList.remove('motion-ready');
    body.classList.add('motion-paused');
    document.getElementById('hero-motion')?.pause();
    document.getElementById('instagram-reel')?.pause();
    revealEverything();
  }
})();
