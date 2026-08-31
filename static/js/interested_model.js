(function () {
  'use strict';

  /* ─────────────────────────────────────────
     1. CSS
  ───────────────────────────────────────── */
  var CSS = `
    :root {
      --im-blue:   #3b82f6;
      --im-purple: #a855f7;
      --im-grad:   linear-gradient(135deg,#3b82f6,#a855f7);
      --im-grad-t: linear-gradient(135deg,#60a5fa,#c084fc,#a5b4fc);
      --im-surface: rgba(255,255,255,0.9);
      --im-border:  rgba(0,0,0,0.09);
      --im-text:    #0f172a;
      --im-sub:     #475569;
      --im-muted:   #94a3b8;
      --im-ph:      rgba(0,0,0,0.28);
      --im-radius:  20px;
      --im-pill:    9999px;
      --im-ease:    cubic-bezier(0.23,1,0.32,1);
    }

    /* Overlay */
    .im-overlay {
      position: fixed;
      inset: 0;
      z-index: 9998;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 1rem;
      opacity: 0;
      pointer-events: none;
      background: transparent;
      backdrop-filter: blur(0px);
      -webkit-backdrop-filter: blur(0px);
      transition: opacity 0.4s var(--im-ease), backdrop-filter 0.4s var(--im-ease);
    }
    .im-overlay.is-open {
      opacity: 1;
      pointer-events: auto;
      background: rgba(15,23,42,0.35);
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
    }

    /* Modal card */
    .im-modal {
      position: relative;
      z-index: 9999;
      background: var(--im-surface);
      border: 1px solid var(--im-border);
      border-radius: var(--im-radius);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      box-shadow:
        0 4px 6px -1px rgba(0,0,0,0.07),
        0 20px 60px rgba(0,0,0,0.12),
        0 0 0 1px rgba(255,255,255,0.9) inset;
      max-width: 480px;
      width: 100%;
      max-height: 90vh;
      overflow: hidden;
      animation: im-slide-in 0.4s var(--im-ease);
    }
    .im-overlay.is-closing .im-modal {
      animation: im-slide-out 0.3s var(--im-ease) forwards;
    }
    /* Shimmer strip */
    .im-modal::before {
      content: '';
      position: absolute;
      inset-x: 0; top: 0;
      height: 100px;
      border-radius: var(--im-radius) var(--im-radius) 0 0;
      pointer-events: none;
      background: linear-gradient(180deg,rgba(255,255,255,0.85) 0%,rgba(255,255,255,0.3) 40%,transparent 100%);
      z-index: 0;
    }
    /* Grid texture */
    .im-modal::after {
      content: '';
      position: absolute;
      inset: 0;
      pointer-events: none;
      background-image:
        linear-gradient(rgba(0,0,0,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,0,0,0.025) 1px, transparent 1px);
      background-size: 60px 60px;
      -webkit-mask-image: linear-gradient(to bottom right,#000,transparent 60%);
      mask-image: linear-gradient(to bottom right,#000,transparent 60%);
      z-index: 0;
      border-radius: var(--im-radius);
    }
    @keyframes im-slide-in {
      from { opacity:0; transform:scale(0.92) translateY(24px); }
      to   { opacity:1; transform:scale(1) translateY(0); }
    }
    @keyframes im-slide-out {
      from { opacity:1; transform:scale(1) translateY(0); }
      to   { opacity:0; transform:scale(0.92) translateY(24px); }
    }

    /* Header */
    .im-header {
      position: relative; z-index: 1;
      padding: 2rem 2rem 1rem;
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
    }
    .im-title {
      font-family: 'Figtree','Georgia',serif;
      font-size: 1.6rem;
      font-weight: 800;
      color: var(--im-text);
      letter-spacing: -0.5px;
      line-height: 1.1;
    }
    .im-title-accent {
      background: var(--im-grad-t);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
    .im-close-btn {
      background: rgba(0,0,0,0.04);
      border: 1px solid var(--im-border);
      cursor: pointer;
      padding: 0.5rem;
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--im-muted);
      transition: background 0.2s, color 0.2s, transform 0.2s;
      border-radius: 10px;
      flex-shrink: 0;
    }
    .im-close-btn:hover {
      background: rgba(0,0,0,0.08);
      color: var(--im-text);
      transform: scale(1.1);
    }

    /* Progress bar */
    .im-progress-bar {
      position: relative; z-index: 1;
      height: 3px;
      background: rgba(0,0,0,0.07);
      margin: 0 2rem 1.25rem;
      border-radius: 3px;
      overflow: hidden;
    }
    .im-progress-fill {
      height: 100%;
      background: var(--im-grad);
      border-radius: 3px;
      transition: width 0.5s var(--im-ease);
      width: 0%;
    }

    /* Step counter */
    .im-step-counter {
      position: relative; z-index: 1;
      text-align: center;
      font-size: 0.75rem;
      font-weight: 500;
      color: var(--im-muted);
      margin-bottom: 1rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }

    /* Body */
    .im-body {
      position: relative; z-index: 1;
      padding: 0 2rem 2rem;
      min-height: 200px;
      display: flex;
      flex-direction: column;
    }

    /* Steps */
    .im-step {
      display: none;
      flex-direction: column;
      gap: 1.25rem;
      animation: im-step-enter 0.45s var(--im-ease);
    }
    .im-step.is-active { display: flex; }
    .im-step.is-exiting {
      display: flex;
      animation: im-step-exit 0.28s var(--im-ease) forwards;
    }
    @keyframes im-step-enter {
      from { opacity:0; transform:translateX(36px) scale(0.96); }
      to   { opacity:1; transform:translateX(0) scale(1); }
    }
    @keyframes im-step-exit {
      from { opacity:1; transform:translateX(0) scale(1); }
      to   { opacity:0; transform:translateX(-36px) scale(0.96); }
    }

    /* Step question */
    .im-step-question {
      font-family: 'Figtree','Georgia',serif;
      font-size: 1.05rem;
      font-weight: 700;
      color: var(--im-text);
      line-height: 1.35;
    }

    /* Input */
    .im-input {
      font-family: 'Lexend Deca','Segoe UI',sans-serif;
      background: rgba(0,0,0,0.03);
      border: 1px solid var(--im-border);
      border-radius: 12px;
      padding: 0.9rem 1.1rem;
      font-size: 0.95rem;
      color: var(--im-text);
      transition: all 0.25s ease;
      width: 100%;
      outline: none;
    }
    .im-input::placeholder { color: var(--im-ph); }
    .im-input:focus {
      background: rgba(59,130,246,0.04);
      border-color: var(--im-blue);
      box-shadow: 0 0 0 3px rgba(59,130,246,0.12);
    }
    .im-input.has-error {
      border-color: #ef4444;
      background: rgba(239,68,68,0.04);
      box-shadow: 0 0 0 3px rgba(239,68,68,0.1);
      animation: im-shake 0.4s ease;
    }
    @keyframes im-shake {
      0%,100% { transform:translateX(0); }
      20%     { transform:translateX(-7px); }
      40%     { transform:translateX(7px); }
      60%     { transform:translateX(-3px); }
      80%     { transform:translateX(3px); }
    }
    .im-error-msg {
      color: #ef4444;
      font-size: 0.8rem;
      display: none;
    }
    .im-error-msg.show {
      display: block;
      animation: im-fadein 0.2s ease;
    }
    @keyframes im-fadein {
      from { opacity:0; transform:translateY(-4px); }
      to   { opacity:1; transform:translateY(0); }
    }

    /* Nav buttons */
    .im-step-nav {
      display: flex;
      gap: 0.65rem;
      margin-top: auto;
      padding-top: 1.5rem;
    }
    .im-btn {
      flex: 1;
      padding: 0.9rem 1rem;
      border-radius: var(--im-pill);
      font-family: 'Lexend Deca','Segoe UI',sans-serif;
      font-size: 0.9rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.25s var(--im-ease);
      border: none;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
    }
    .im-btn-secondary {
      background: rgba(0,0,0,0.04);
      color: var(--im-sub);
      border: 1px solid var(--im-border);
    }
    .im-btn-secondary:hover {
      background: rgba(0,0,0,0.08);
      color: var(--im-text);
      border-color: rgba(0,0,0,0.15);
    }
    .im-btn-primary {
      background: var(--im-grad);
      color: #fff;
      box-shadow: 0 4px 14px rgba(99,102,241,0.28);
    }
    .im-btn-primary:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: 0 8px 24px rgba(99,102,241,0.42);
    }
    .im-btn-primary:disabled { opacity:0.5; cursor:not-allowed; }

    /* Spinner */
    .im-spinner {
      display: none;
      width: 16px; height: 16px;
      border: 2px solid rgba(255,255,255,0.35);
      border-top-color: #fff;
      border-radius: 50%;
      animation: im-spin 0.7s linear infinite;
    }
    .im-btn-primary.loading .im-spinner { display: block; }
    .im-btn-primary.loading .im-btn-text { display: none; }
    @keyframes im-spin { to { transform:rotate(360deg); } }

    /* Success */
    .im-success {
      display: none;
      text-align: center;
      padding: 3rem 2rem;
    }
    .im-success.show {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 280px;
      animation: im-fadein 0.5s ease;
    }
    .im-success-icon {
      width: 68px; height: 68px;
      margin-bottom: 1.5rem;
      background: var(--im-grad);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 8px 24px rgba(99,102,241,0.3);
      animation: im-pop 0.5s var(--im-ease) 0.15s both;
    }
    @keyframes im-pop {
      from { transform:scale(0); }
      to   { transform:scale(1); }
    }
    .im-success-title {
      font-family: 'Figtree','Georgia',serif;
      font-size: 1.5rem;
      font-weight: 800;
      color: var(--im-text);
      margin-bottom: 0.5rem;
    }
    .im-success-message {
      font-size: 0.9rem;
      color: var(--im-sub);
      line-height: 1.6;
    }

    /* Privacy note */
    .im-privacy {
      font-size: 0.75rem;
      color: var(--im-muted);
      text-align: center;
      margin-top: 0.75rem;
    }

    /* Responsive */
    @media (max-width: 560px) {
      .im-modal { border-radius: 16px; }
      .im-header { padding: 1.5rem 1.5rem 0.75rem; }
      .im-body { padding: 0 1.5rem 1.5rem; }
      .im-progress-bar { margin: 0 1.5rem 1rem; }
      .im-title { font-size: 1.35rem; }
      .im-input { font-size: 16px; }
    }
  `;

  /* ─────────────────────────────────────────
     2. HTML
  ───────────────────────────────────────── */
  var HTML = `
    <div class="im-overlay" id="im-overlay" role="presentation">
      <div class="im-modal" role="dialog" aria-modal="true" aria-labelledby="im-title">

        <!-- Header -->
        <div class="im-header">
          <h2 class="im-title" id="im-title">
            I'm <span class="im-title-accent">Interested</span>
          </h2>
          <button class="im-close-btn" id="im-close-btn" aria-label="Close">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                 stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <!-- Progress bar -->
        <div class="im-progress-bar">
          <div class="im-progress-fill" id="im-progress-fill"></div>
        </div>
        <div class="im-step-counter" id="im-step-counter">Step 1 of 2</div>

        <!-- Body -->
        <div class="im-body">

          <!-- Step 1: Email -->
          <div class="im-step is-active" data-step="1">
            <div class="im-step-question">What's your email address?</div>
            <div>
              <input type="email" id="im-email" class="im-input"
                     placeholder="you@example.com" autocomplete="email" />
              <span class="im-error-msg" id="im-email-err">Please enter a valid email address.</span>
            </div>
            <div class="im-step-nav">
              <button class="im-btn im-btn-primary" id="im-next-btn">
                <span class="im-spinner"></span>
                <span class="im-btn-text">Next →</span>
              </button>
            </div>
          </div>

          <!-- Step 2: Mobile -->
          <div class="im-step" data-step="2">
            <div class="im-step-question">What's your mobile number?</div>
            <div>
              <input type="tel" id="im-phone" class="im-input"
                     placeholder="+91 98765 43210" autocomplete="tel" />
              <span class="im-error-msg" id="im-phone-err">Please enter a valid phone number (min 10 digits).</span>
            </div>
            <div class="im-step-nav">
              <button class="im-btn im-btn-secondary" id="im-back-btn">← Back</button>
              <button class="im-btn im-btn-primary" id="im-submit-btn">
                <span class="im-spinner"></span>
                <span class="im-btn-text">Send 🚀</span>
              </button>
            </div>
          </div>

          <!-- Success -->
          <div class="im-success" id="im-success">
            <div class="im-success-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#fff"
                   stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
            </div>
            <h3 class="im-success-title">We'll be in touch! 🎉</h3>
            <p class="im-success-message">Thanks for your interest. Expect a message within 24 hours.</p>
          </div>

        </div><!-- /im-body -->
      </div><!-- /im-modal -->
    </div><!-- /im-overlay -->
  `;

  /* ─────────────────────────────────────────
     3. LOGIC
  ───────────────────────────────────────── */
  var currentStep = 1;
  var totalSteps  = 2;

  function init() {
    var overlay    = document.getElementById('im-overlay');
    var openBtn    = document.getElementById('im-open-btn');
    var closeBtn   = document.getElementById('im-close-btn');
    var nextBtn    = document.getElementById('im-next-btn');
    var backBtn    = document.getElementById('im-back-btn');
    var submitBtn  = document.getElementById('im-submit-btn');
    var emailInput = document.getElementById('im-email');
    var phoneInput = document.getElementById('im-phone');
    var emailErr   = document.getElementById('im-email-err');
    var phoneErr   = document.getElementById('im-phone-err');
    var progressFill = document.getElementById('im-progress-fill');
    var stepCounter  = document.getElementById('im-step-counter');
    var success      = document.getElementById('im-success');

    function updateProgress() {
      progressFill.style.width = (currentStep / totalSteps * 100) + '%';
      stepCounter.textContent  = 'Step ' + currentStep + ' of ' + totalSteps;
    }

    function goToStep(step) {
      var cur  = document.querySelector('.im-step[data-step="' + currentStep + '"]');
      var next = document.querySelector('.im-step[data-step="' + step + '"]');
      if (!cur || !next) return;

      if (step > currentStep) {
        cur.classList.add('is-exiting');
        cur.classList.remove('is-active');
        setTimeout(function () {
          cur.classList.remove('is-exiting');
          next.classList.add('is-active');
          var inp = next.querySelector('input');
          if (inp) setTimeout(function(){ inp.focus(); }, 80);
        }, 240);
      } else {
        cur.classList.remove('is-active');
        next.classList.add('is-active');
        var inp = next.querySelector('input');
        if (inp) setTimeout(function(){ inp.focus(); }, 80);
      }
      currentStep = step;
      updateProgress();
    }

    function isValidEmail(v) { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v); }
    function isValidPhone(v) { return /^\+?[\d\s\-()]{10,}$/.test(v); }

    function setError(input, errEl, show) {
      input.classList.toggle('has-error', show);
      errEl.classList.toggle('show', show);
    }

    // Clear on type
    emailInput.addEventListener('input', function () {
      if (isValidEmail(emailInput.value)) setError(emailInput, emailErr, false);
    });
    phoneInput.addEventListener('input', function () {
      if (isValidPhone(phoneInput.value)) setError(phoneInput, phoneErr, false);
    });

    // Open
    openBtn.addEventListener('click', function () {
      overlay.classList.add('is-open');
      document.body.style.overflow = 'hidden';
      setTimeout(function () { emailInput.focus(); }, 300);
    });

    // Close
    function closeModal() {
      overlay.classList.add('is-closing');
      setTimeout(function () {
        overlay.classList.remove('is-open', 'is-closing');
        document.body.style.overflow = '';
        resetForm();
      }, 300);
    }
    closeBtn.addEventListener('click', closeModal);
    overlay.addEventListener('click', function (e) { if (e.target === overlay) closeModal(); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && overlay.classList.contains('is-open')) closeModal();
    });

    // Next (step 1 → step 2)
    nextBtn.addEventListener('click', function () {
      if (!isValidEmail(emailInput.value.trim())) {
        setError(emailInput, emailErr, true);
        return;
      }
      setError(emailInput, emailErr, false);
      goToStep(2);
    });

    // Back
    backBtn.addEventListener('click', function () { goToStep(1); });

    // Submit (step 2)
    submitBtn.addEventListener('click', function () {
      if (!isValidPhone(phoneInput.value.trim())) {
        setError(phoneInput, phoneErr, true);
        return;
      }
      setError(phoneInput, phoneErr, false);

      submitBtn.classList.add('loading');
      submitBtn.disabled = true;

      var payload = {
        email       : emailInput.value.trim(),
        phone       : phoneInput.value.trim(),
        submittedAt : new Date().toISOString()
      };
      console.log('📬 Interested Submission:', payload);

      // ← swap with your real fetch('/api/interested/', ...) here
      setTimeout(function () {
        submitBtn.classList.remove('loading');
        submitBtn.disabled = false;
        // hide steps + progress
        document.querySelectorAll('.im-step').forEach(function(s){ s.classList.remove('is-active'); });
        document.getElementById('im-step-counter').style.display = 'none';
        document.querySelector('.im-progress-bar').style.display = 'none';
        success.classList.add('show');
        setTimeout(closeModal, 3500);
      }, 1500);
    });

    function resetForm() {
      currentStep = 1;
      emailInput.value = '';
      phoneInput.value = '';
      setError(emailInput, emailErr, false);
      setError(phoneInput, phoneErr, false);
      document.querySelectorAll('.im-step').forEach(function(s){
        s.classList.remove('is-active','is-exiting');
      });
      document.querySelector('.im-step[data-step="1"]').classList.add('is-active');
      document.getElementById('im-step-counter').style.display = '';
      document.querySelector('.im-progress-bar').style.display = '';
      success.classList.remove('show');
      updateProgress();
    }

    // Init progress
    updateProgress();
  }

  /* ─────────────────────────────────────────
     4. BOOTSTRAP
  ───────────────────────────────────────── */
  function bootstrap() {
    // Inject CSS
    if (!document.getElementById('im-styles')) {
      var style = document.createElement('style');
      style.id = 'im-styles';
      style.textContent = CSS;
      document.head.appendChild(style);
    }
    // Inject Modal HTML
    if (!document.getElementById('im-overlay')) {
      var div = document.createElement('div');
      div.innerHTML = HTML;
      document.body.appendChild(div);
    }
    // Wire logic
    init();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bootstrap);
  } else {
    bootstrap();
  }

})();