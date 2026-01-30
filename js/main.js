/* ============================================
   FIRST CONTACT, LAST CONTACT
   Site JavaScript
   ============================================ */

(function() {
  'use strict';

  // ============ Theme Toggle ============
  const themeToggle = document.querySelector('.theme-toggle');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');

  function getTheme() {
    const stored = localStorage.getItem('theme');
    if (stored) return stored;
    return prefersDark.matches ? 'dark' : 'light';
  }

  function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    updateThemeIcon(theme);
  }

  function updateThemeIcon(theme) {
    if (!themeToggle) return;
    const sunIcon = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>`;
    const moonIcon = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/></svg>`;
    themeToggle.innerHTML = theme === 'dark' ? sunIcon : moonIcon;
    themeToggle.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
  }

  // Initialize theme
  setTheme(getTheme());

  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme');
      setTheme(current === 'dark' ? 'light' : 'dark');
    });
  }

  // ============ Reading Progress Bar ============
  const progressFill = document.querySelector('.progress-bar__fill');

  function updateProgress() {
    if (!progressFill) return;

    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;

    progressFill.style.width = `${Math.min(100, Math.max(0, progress))}%`;
  }

  // ============ Header Hide/Show on Scroll ============
  const header = document.querySelector('.site-header');
  let lastScroll = 0;
  const scrollThreshold = 100;

  function handleHeaderScroll() {
    if (!header) return;

    const currentScroll = window.scrollY;

    if (currentScroll <= 0) {
      header.classList.remove('hidden');
      return;
    }

    if (currentScroll > lastScroll && currentScroll > scrollThreshold) {
      // Scrolling down
      header.classList.add('hidden');
    } else if (currentScroll < lastScroll) {
      // Scrolling up
      header.classList.remove('hidden');
    }

    lastScroll = currentScroll;
  }

  // ============ Scroll Event Handler ============
  let ticking = false;

  window.addEventListener('scroll', () => {
    if (!ticking) {
      requestAnimationFrame(() => {
        updateProgress();
        handleHeaderScroll();
        ticking = false;
      });
      ticking = true;
    }
  });

  // Initial progress update
  updateProgress();

  // ============ Reading Progress Storage ============
  const STORAGE_KEY = 'fcls_reading_progress';

  function getReadingProgress() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {};
    } catch {
      return {};
    }
  }

  function markChapterRead(chapterNum) {
    const progress = getReadingProgress();
    progress[chapterNum] = {
      read: true,
      timestamp: Date.now()
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(progress));
  }

  function isChapterRead(chapterNum) {
    const progress = getReadingProgress();
    return progress[chapterNum]?.read || false;
  }

  // Mark current chapter as read when scrolled to bottom
  const chapterContent = document.querySelector('.chapter__content');
  if (chapterContent) {
    const chapterNum = document.body.dataset.chapter;

    if (chapterNum) {
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting && entry.intersectionRatio > 0.5) {
            markChapterRead(chapterNum);
            observer.disconnect();
          }
        });
      }, { threshold: 0.5 });

      // Observe the chapter footer (means they reached the end)
      const footer = document.querySelector('.chapter__footer');
      if (footer) {
        observer.observe(footer);
      }
    }
  }

  // ============ Update TOC with Read Status ============
  const tocItems = document.querySelectorAll('.toc__item');
  tocItems.forEach(item => {
    const link = item.querySelector('.toc__link');
    if (link) {
      const href = link.getAttribute('href');
      const match = href?.match(/(\d+)\.html/);
      if (match) {
        const chapterNum = match[1];
        if (isChapterRead(chapterNum)) {
          item.classList.add('toc__item--read');
        }
      }
    }
  });

  // ============ Calculate Reading Time ============
  function calculateReadingTime(text) {
    const wordsPerMinute = 200;
    const words = text.trim().split(/\s+/).length;
    const minutes = Math.ceil(words / wordsPerMinute);
    return minutes;
  }

  // Update reading time display if present
  const readingTimeEl = document.querySelector('[data-reading-time]');
  if (readingTimeEl && chapterContent) {
    const text = chapterContent.textContent;
    const minutes = calculateReadingTime(text);
    readingTimeEl.textContent = `${minutes} min read`;
  }

  // ============ Keyboard Navigation ============
  document.addEventListener('keydown', (e) => {
    // Don't trigger if user is typing in an input
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

    const prevLink = document.querySelector('.chapter-pagination__link--prev');
    const nextLink = document.querySelector('.chapter-pagination__link--next');

    if (e.key === 'ArrowLeft' && prevLink) {
      prevLink.click();
    } else if (e.key === 'ArrowRight' && nextLink) {
      nextLink.click();
    }
  });

  // ============ Smooth Scroll for Internal Links ============
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });

})();
