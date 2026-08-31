/*  
   SCROLL REVEAL
*/
const revealEls = document.querySelectorAll('.pd-reveal');
const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(e => {
        if (e.isIntersecting) {
            e.target.classList.add('is-visible');
            revealObserver.unobserve(e.target);
        }
    });
}, { threshold: 0.08 });
revealEls.forEach(el => revealObserver.observe(el));

// SCROLL PROGRESS BAR — null-safe
const progressBar = document.getElementById('progressBar');
if (progressBar) {
    window.addEventListener('scroll', () => {
        const scrolled = window.scrollY;
        const total = document.documentElement.scrollHeight - window.innerHeight;
        progressBar.style.width = (scrolled / total * 100) + '%';
    }, { passive: true });
}

/*  
   THEME TOGGLE — your HTML uses .icon-moon / .icon-sun classes, NOT ids
*/
const themeBtn = document.getElementById('themeToggle');
const iconMoon = document.querySelector('.icon-moon');
const iconSun = document.querySelector('.icon-sun');
let isLight = false;

if (localStorage.getItem('theme') === 'light') {
    document.body.classList.add('light');
    isLight = true;
    if (iconMoon) iconMoon.classList.add('hidden');
    if (iconSun) iconSun.classList.remove('hidden');
}

if (themeBtn) {
    themeBtn.addEventListener('click', () => {
        isLight = !isLight;
        document.body.classList.toggle('light', isLight);
        localStorage.setItem('theme', isLight ? 'light' : 'dark');
        if (iconMoon) iconMoon.classList.toggle('hidden', isLight);
        if (iconSun) iconSun.classList.toggle('hidden', !isLight);
    });
}

// LIGHTBOX
const lightbox = document.getElementById('lightbox');
const lbImg = document.getElementById('lbImg');
const lbCaption = document.getElementById('lbCaption');
const lbCounter = document.getElementById('lbCounter');
const lbClose = document.getElementById('lbClose');
const lbPrev = document.getElementById('lbPrev');
const lbNext = document.getElementById('lbNext');

let allItems = [];
let currentIdx = 0;

if (lightbox && lbClose && lbPrev && lbNext) {

    function buildItemList() {
        allItems = [];
        document.querySelectorAll('[data-src]').forEach(el => {
            const imgEl = el.querySelector('img');
            allItems.push({
                src: imgEl ? imgEl.src : el.dataset.src,
                caption: el.dataset.caption || '',
            });
        });
    }

    function openLightbox(idx) {
        buildItemList();
        currentIdx = idx;
        showSlide(currentIdx);
        lightbox.classList.add('is-active');
        document.body.style.overflow = 'hidden';
    }

    function closeLightbox() {
        lightbox.classList.remove('is-active');
        document.body.style.overflow = '';
    }

    function showSlide(idx) {
        const item = allItems[idx];
        lbImg.src = item.src;
        lbImg.alt = item.caption;
        lbCaption.textContent = item.caption;
        lbCounter.textContent = `${idx + 1} / ${allItems.length}`;
    }

    document.querySelectorAll('#screenshotGrid .pd-gallery-item').forEach((el, i) => {
        el.addEventListener('click', () => openLightbox(i));
    });

    document.querySelectorAll('#diagramList .pd-diagram-card').forEach((el, i) => {
        el.addEventListener('click', () => {
            buildItemList();
            const screenshotCount = document.querySelectorAll('#screenshotGrid .pd-gallery-item').length;
            openLightbox(screenshotCount + i);
        });
    });

    lbClose.addEventListener('click', closeLightbox);
    lightbox.addEventListener('click', e => { if (e.target === lightbox) closeLightbox(); });

    lbPrev.addEventListener('click', () => {
        currentIdx = (currentIdx - 1 + allItems.length) % allItems.length;
        showSlide(currentIdx);
    });
    lbNext.addEventListener('click', () => {
        currentIdx = (currentIdx + 1) % allItems.length;
        showSlide(currentIdx);
    });

    document.addEventListener('keydown', e => {
        if (!lightbox.classList.contains('is-active')) return;
        if (e.key === 'Escape') closeLightbox();
        if (e.key === 'ArrowLeft') { currentIdx = (currentIdx - 1 + allItems.length) % allItems.length; showSlide(currentIdx); }
        if (e.key === 'ArrowRight') { currentIdx = (currentIdx + 1) % allItems.length; showSlide(currentIdx); }
    });

} // end lightbox guard