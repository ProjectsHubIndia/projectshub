/* ════════════════════════════════════════════════════════════
   Quantum Pulse Loader — Reusable loader component
   Inject this loader at page load, then hide it after content loads
   ════════════════════════════════════════════════════════════ */

(function () {
    'use strict';

    /**
     * Creates and manages the quantum pulse loader
     * @param {Object} options - Configuration options
     * @param {string} options.containerId - ID of container to mount loader in (default: 'app')
     * @param {number} options.minDisplayTime - Minimum time to show loader in ms (default: 1500)
     * @param {number} options.timeout - Timeout to hide loader if content doesn't load (default: 10000)
     * @returns {Object} Loader controller object
     */
    function createQuantumLoader(options = {}) {
        const config = {
            containerId: options.containerId || 'app',
            minDisplayTime: options.minDisplayTime || 1500,
            timeout: options.timeout || 10000,
        };

        let isHidden = false;
        const loadStartTime = Date.now();

        // Create loader HTML structure
        function createLoaderHTML() {
            const wrapper = document.createElement('div');
            wrapper.id = 'quantum-pulse-loader';
            wrapper.setAttribute('aria-live', 'polite');
            wrapper.setAttribute('aria-label', 'Loading page content');
            wrapper.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
                background: rgba(0, 0, 0, 0.5);
                backdrop-filter: blur(14px);
                z-index: 9999;
                transition: opacity 0.2s ease-out;
            `;

            const inner = document.createElement('div');
            inner.className = 'generating-loader-wrapper';

            inner.innerHTML = `
                <style>
                    @keyframes loaderSpin {
                        to { transform: rotate(360deg); }
                    }
                    @keyframes loaderSpinReverse {
                        to { transform: rotate(-360deg); }
                    }
                    @keyframes loaderPulse {
                        0%, 100% { transform: scale(0.93); opacity: 0.8; }
                        50%       { transform: scale(1.07); opacity: 1; }
                    }
                    @keyframes loaderDots {
                        0%, 20%  { opacity: 0; }
                        40%      { opacity: 1; }
                        100%     { opacity: 0; }
                    }

                    .loader-ring-wrapper {
                        position: relative;
                        width: 170px;
                        height: 170px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin-bottom: 24px;
                    }

                    /* Outer spinning ring */
                    .loader-ring-outer {
                        position: absolute;
                        inset: 0;
                        border-radius: 50%;
                        border: 3px solid rgba(99,102,241,0.12);
                        border-top-color: #6366f1;
                        border-right-color: #22d3ee;
                        animation: loaderSpin 1.4s linear infinite;
                    }

                    /* Inner counter-spinning ring */
                    .loader-ring-inner {
                        position: absolute;
                        inset: 14px;
                        border-radius: 50%;
                        border: 2px solid rgba(168,85,247,0.1);
                        border-top-color: #a855f7;
                        border-left-color: #818cf8;
                        animation: loaderSpinReverse 1.8s linear infinite;
                    }

                    /* Glow circle behind logo */
                    .loader-glow {
                        position: absolute;
                        inset: 30px;
                        border-radius: 50%;
                        background: radial-gradient(circle, rgba(99,102,241,0.18) 0%, transparent 70%);
                        filter: blur(8px);
                    }

                    /* Logo */
                    .loader-logo-svg {
                        width: 88px;
                        height: 88px;
                        object-fit: contain;
                        position: relative;
                        z-index: 2;
                        animation: loaderPulse 2s ease-in-out infinite;
                        filter: drop-shadow(0 0 12px rgba(99,102,241,0.4));
                    }

                    /* Brand text below */
                    .loader-brand {
                        font-family: 'Lexend Deca', 'Figtree', sans-serif;
                        font-size: 0.8rem;
                        font-weight: 600;
                        letter-spacing: 0.18em;
                        text-transform: uppercase;
                        color: rgba(165,180,252,0.75);
                    }

                    .loader-brand-dot {
                        display: inline-block;
                        animation: loaderDots 1.4s ease-in-out infinite;
                    }
                    .loader-brand-dot:nth-child(2) { animation-delay: 0.2s; }
                    .loader-brand-dot:nth-child(3) { animation-delay: 0.4s; }

                    @media (max-width: 576px) {
                        .loader-ring-wrapper { width: 130px; height: 130px; }
                        .loader-logo-svg { width: 66px; height: 66px; }
                        .loader-ring-inner { inset: 10px; }
                    }
                </style>

                <div class="loader-ring-wrapper">
                    <div class="loader-ring-outer"></div>
                    <div class="loader-ring-inner"></div>
                    <div class="loader-glow"></div>
                    <img
                        src="/static/image/TREE%20LOGO%20ONLY/LOGO%20ONLY/ProjectsHub%20Logo%20SVG.svg"
                        alt="ProjectsHub"
                        class="loader-logo-svg"
                    />
                </div>
                <p class="loader-brand">
                    Loading<span class="loader-brand-dot">.</span><span class="loader-brand-dot">.</span><span class="loader-brand-dot">.</span>
                </p>
            `;

            wrapper.appendChild(inner);
            return wrapper;
        }

        // Hide loader with fade effect
        function hideLoader() {
            if (isHidden) return;
            isHidden = true;

            const loaderEl = document.getElementById('quantum-pulse-loader');
            if (!loaderEl) return;

            const elapsed = Date.now() - loadStartTime;
            const remaining = Math.max(0, config.minDisplayTime - elapsed);

            setTimeout(() => {
                loaderEl.style.opacity = '0';
                setTimeout(() => {
                    if (loaderEl && loaderEl.parentNode) {
                        loaderEl.parentNode.removeChild(loaderEl);
                    }
                }, 300);
            }, remaining);
        }

        // Show loader
        function showLoader() {
            // Don't show if already showing
            if (document.getElementById('quantum-pulse-loader')) {
                return;
            }

            const loaderEl = createLoaderHTML();
            document.body.insertBefore(loaderEl, document.body.firstChild);

            // Hide after timeout if nothing else hides it
            setTimeout(() => {
                if (!isHidden) hideLoader();
            }, config.timeout);
        }

        // Public API
        return {
            show: showLoader,
            hide: hideLoader,
            isHidden: () => isHidden,
        };
    }

    // Define init function first
    function initLoader() {
        // Check if any element has data-quantum-loader attribute
        const loaderElement = document.querySelector('[data-quantum-loader]');
        if (loaderElement) {
            const options = {
                containerId: loaderElement.dataset.loaderContainer || 'app',
                minDisplayTime: parseInt(loaderElement.dataset.loaderMinTime) || 1500,
                timeout: parseInt(loaderElement.dataset.loaderTimeout) || 10000,
            };
            window.quantumLoader = createQuantumLoader(options);
            window.quantumLoader.show();

            // Auto-hide when page fully loads
            window.addEventListener('load', () => {
                setTimeout(() => {
                    if (window.quantumLoader) {
                        window.quantumLoader.hide();
                    }
                }, 200);
            });
        }
    }

    // Auto-initialize on page load if data attribute is present
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initLoader);
    } else {
        // If DOMContentLoaded already fired, init immediately
        setTimeout(initLoader, 0);
    }

    // Expose to global scope
    window.createQuantumLoader = createQuantumLoader;
})();
