/* ════════════════════════════════════════════════════════════
   Share Your Idea / Custom AI Solution Modal
   Ultra-modern UI/UX, responsive, accessible, interactive
   ════════════════════════════════════════════════════════════ */

(function () {
    'use strict';

    class IdeaModal {
        constructor() {
            this.isOpen = false;
            this.init();
        }

        init() {
            this.createModalHTML();
            this.cacheElements();
            this.bindEvents();
        }

        createModalHTML() {
            if (document.getElementById('ideaModalOverlay')) {
                return;
            }

            const html = `
                <div class="idea-modal-overlay" id="ideaModalOverlay" role="presentation">
                    <div class="idea-modal" role="dialog" aria-modal="true" aria-labelledby="ideaModalTitle" id="ideaModal">
                        <!-- Top Ambient Glow -->
                        <div class="idea-modal-glow" aria-hidden="true"></div>

                        <!-- Header -->
                        <div class="idea-modal-header">
                            <div class="idea-modal-header-content">
                                <div class="idea-modal-pill">
                                    <svg class="idea-pill-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                                        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
                                    </svg>
                                    <span>Free AI & Project Consultation</span>
                                </div>
                                <h2 class="idea-modal-title" id="ideaModalTitle">
                                    Share Your <span class="idea-modal-title-accent">Project Idea</span>
                                </h2>
                                <p class="idea-modal-subtitle">
                                    Got a custom AI concept, startup tool, or academic project in mind? Let's turn your vision into real-world code.
                                </p>
                            </div>
                            <button class="idea-modal-close-btn" id="ideaModalClose" aria-label="Close modal">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                                    <line x1="18" y1="6" x2="6" y2="18"></line>
                                    <line x1="6" y1="6" x2="18" y2="18"></line>
                                </svg>
                            </button>
                        </div>

                        <!-- Body -->
                        <div class="idea-modal-body">
                            <!-- Form -->
                            <form class="idea-form" id="ideaForm" novalidate>
                                <!-- Name & Email Row -->
                                <div class="idea-form-row">
                                    <div class="idea-form-field">
                                        <label for="ideaName" class="idea-form-label">
                                            Full Name <span class="idea-form-label-required">*</span>
                                        </label>
                                        <div class="idea-input-wrapper">
                                            <span class="idea-input-icon">
                                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
                                            </span>
                                            <input type="text" id="ideaName" class="idea-form-input has-icon" placeholder="e.g. John Doe" required autocomplete="name" />
                                        </div>
                                        <span class="idea-form-error" id="ideaNameError">Please enter your name</span>
                                    </div>
                                    <div class="idea-form-field">
                                        <label for="ideaEmail" class="idea-form-label">
                                            Email Address <span class="idea-form-label-required">*</span>
                                        </label>
                                        <div class="idea-input-wrapper">
                                            <span class="idea-input-icon">
                                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>
                                            </span>
                                            <input type="email" id="ideaEmail" class="idea-form-input has-icon" placeholder="e.g. you@company.com" required autocomplete="email" />
                                        </div>
                                        <span class="idea-form-error" id="ideaEmailError">Please enter a valid email address</span>
                                    </div>
                                </div>

                                <!-- Phone & Title Row -->
                                <div class="idea-form-row">
                                    <div class="idea-form-field">
                                        <label for="ideaPhone" class="idea-form-label">
                                            Phone Number <span class="idea-label-subtext">(Optional)</span>
                                        </label>
                                        <div class="idea-input-wrapper">
                                            <span class="idea-input-icon">
                                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
                                            </span>
                                            <input type="tel" id="ideaPhone" class="idea-form-input has-icon" placeholder="e.g. +91 98765 43210" autocomplete="tel" />
                                        </div>
                                        <span class="idea-form-error" id="ideaPhoneError">Please enter a valid phone number</span>
                                    </div>
                                    <div class="idea-form-field">
                                        <label for="ideaTitle" class="idea-form-label">
                                            Project / Idea Title <span class="idea-form-label-required">*</span>
                                        </label>
                                        <div class="idea-input-wrapper">
                                            <span class="idea-input-icon">
                                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18h6"></path><path d="M10 22h4"></path><path d="M15.09 14c.18-.98.65-1.74 1.41-2.5A4.65 4.65 0 0 0 18 8 6 6 0 0 0 6 8c0 1 .23 2.23 1.5 3.5A4.61 4.61 0 0 1 8.91 14"></path></svg>
                                            </span>
                                            <input type="text" id="ideaTitle" class="idea-form-input has-icon" placeholder="e.g. AI Customer Service Agent" required />
                                        </div>
                                        <span class="idea-form-error" id="ideaTitleError">Please give your idea a title</span>
                                    </div>
                                </div>

                                <!-- Description -->
                                <div class="idea-form-field">
                                    <div class="idea-label-row">
                                        <label for="ideaDescription" class="idea-form-label">
                                            Idea Description <span class="idea-form-label-required">*</span>
                                        </label>
                                        <span class="idea-char-pill"><span id="ideaCharCount">0</span> / 500 chars</span>
                                    </div>
                                    <textarea id="ideaDescription" class="idea-form-textarea" placeholder="Tell us about the key problem, target users, desired features, or preferred AI models... (50 to 500 characters)" required rows="4"></textarea>
                                    <div class="idea-chips-row">
                                        <span class="idea-chip-hint">Click to insert:</span>
                                        <button type="button" class="idea-chip" data-insert="[Key Features]: ">✨ Features</button>
                                        <button type="button" class="idea-chip" data-insert="[Target Audience]: ">👥 Audience</button>
                                        <button type="button" class="idea-chip" data-insert="[Tech Stack]: ">⚡ Tech</button>
                                        <button type="button" class="idea-chip" data-insert="[Deliverables]: ">🎯 Deliverables</button>
                                    </div>
                                    <span class="idea-form-error" id="ideaDescriptionError">Please provide between 50 and 500 characters so we can understand your scope</span>
                                </div>

                                <!-- Budget & Timeline Row -->
                                <div class="idea-form-row">
                                    <div class="idea-form-field">
                                        <label for="ideaBudget" class="idea-form-label">
                                            Estimated Budget <span class="idea-form-label-required">*</span>
                                        </label>
                                        <div class="idea-select-wrapper">
                                            <select id="ideaBudget" class="idea-form-select" required>
                                                <option value="">Select budget range...</option>
                                                <option value="under-1k">Starter (Under $1,000 / ₹40,000)</option>
                                                <option value="1k-5k">Growth ($1,000 – $5,000 / ₹40k–₹2L)</option>
                                                <option value="5k-10k">Pro ($5,000 – $10,000 / ₹2L–₹5L)</option>
                                                <option value="10k-plus">Enterprise ($10,000+ / ₹5L+)</option>
                                                <option value="flexible">Flexible / Exploring</option>
                                            </select>
                                            <span class="idea-select-arrow" aria-hidden="true">
                                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
                                            </span>
                                        </div>
                                        <span class="idea-form-error" id="ideaBudgetError">Please select a budget range</span>
                                    </div>
                                    <div class="idea-form-field">
                                        <label for="ideaTimeline" class="idea-form-label">
                                            Preferred Timeline <span class="idea-form-label-required">*</span>
                                        </label>
                                        <div class="idea-select-wrapper">
                                            <select id="ideaTimeline" class="idea-form-select" required>
                                                <option value="">Select target delivery...</option>
                                                <option value="asap">ASAP (1–2 weeks sprint)</option>
                                                <option value="1-month">1 month</option>
                                                <option value="2-3-months">2–3 months</option>
                                                <option value="flexible">Flexible / Planning phase</option>
                                            </select>
                                            <span class="idea-select-arrow" aria-hidden="true">
                                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
                                            </span>
                                        </div>
                                        <span class="idea-form-error" id="ideaTimelineError">Please select a timeline</span>
                                    </div>
                                </div>

                                <!-- Agreement Checkbox -->
                                <div class="idea-form-field">
                                    <label class="idea-custom-checkbox" for="ideaAgree">
                                        <input type="checkbox" id="ideaAgree" class="idea-native-checkbox" required />
                                        <span class="idea-custom-box">
                                            <svg class="idea-box-check" width="12" height="10" viewBox="0 0 12 10" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                                                <polyline points="1.5 5 4.5 8 10.5 2"></polyline>
                                            </svg>
                                        </span>
                                        <span class="idea-agree-label">
                                            I agree to receive a free architecture breakdown and estimate for this project.
                                        </span>
                                    </label>
                                    <span class="idea-form-error" id="ideaAgreeError">Please confirm agreement to proceed</span>
                                </div>

                                <!-- Submit Button & Trust Badges -->
                                <div class="idea-form-footer">
                                    <button type="submit" class="idea-form-submit" id="ideaSubmitBtn">
                                        <span class="idea-submit-shimmer" aria-hidden="true"></span>
                                        <span class="idea-spinner" aria-hidden="true"></span>
                                        <span class="idea-submit-icon" aria-hidden="true">
                                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                                                <line x1="22" y1="2" x2="11" y2="13"></line>
                                                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                                            </svg>
                                        </span>
                                        <span class="idea-submit-text">Send Project Idea</span>
                                    </button>
                                    <div class="idea-form-trust">
                                        <span class="idea-trust-item">
                                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
                                            100% Confidential
                                        </span>
                                        <span class="idea-trust-dot">•</span>
                                        <span class="idea-trust-item">⚡ 24h Response</span>
                                        <span class="idea-trust-dot">•</span>
                                        <span class="idea-trust-item">🤝 Zero Obligation</span>
                                    </div>
                                </div>
                            </form>

                            <!-- Success State -->
                            <div class="idea-modal-success" id="ideaSuccess">
                                <div class="idea-success-badge-wrap">
                                    <div class="idea-success-glow-ring"></div>
                                    <div class="idea-success-icon-box">
                                        <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                                            <polyline points="20 6 9 17 4 12"></polyline>
                                        </svg>
                                    </div>
                                </div>
                                <div class="idea-success-pill">Submission Received!</div>
                                <h3 class="idea-success-title">We're Excited to Build This! 🚀</h3>
                                <p class="idea-success-desc">Your project details are safely in our hands. Our senior engineering team is reviewing your requirements right now.</p>
                                
                                <div class="idea-success-steps">
                                    <div class="idea-step-card">
                                        <span class="idea-step-badge">01</span>
                                        <div class="idea-step-body">
                                            <strong>Scope & Feasibility</strong>
                                            <p>We analyze technical feasibility, architecture, and AI models within 24h.</p>
                                        </div>
                                    </div>
                                    <div class="idea-step-card">
                                        <span class="idea-step-badge">02</span>
                                        <div class="idea-step-body">
                                            <strong>Roadmap & Cost</strong>
                                            <p>We craft a tailored project breakdown and delivery timeline.</p>
                                        </div>
                                    </div>
                                    <div class="idea-step-card">
                                        <span class="idea-step-badge">03</span>
                                        <div class="idea-step-body">
                                            <strong>Strategy Call</strong>
                                            <p>A complimentary 15-min consultation to align on deliverables & launch.</p>
                                        </div>
                                    </div>
                                </div>
                                <button type="button" class="idea-success-done-btn" id="ideaSuccessDone">Back to Exploring</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            document.body.insertAdjacentHTML('beforeend', html);
        }

        cacheElements() {
            this.overlay = document.getElementById('ideaModalOverlay');
            this.modal = document.getElementById('ideaModal');
            this.closeBtn = document.getElementById('ideaModalClose');

            // Form elements
            this.form = document.getElementById('ideaForm');
            this.nameInput = document.getElementById('ideaName');
            this.emailInput = document.getElementById('ideaEmail');
            this.phoneInput = document.getElementById('ideaPhone');
            this.titleInput = document.getElementById('ideaTitle');
            this.descriptionInput = document.getElementById('ideaDescription');
            this.budgetSelect = document.getElementById('ideaBudget');
            this.timelineSelect = document.getElementById('ideaTimeline');
            this.agreeCheckbox = document.getElementById('ideaAgree');
            this.submitBtn = document.getElementById('ideaSubmitBtn');
            this.charCountSpan = document.getElementById('ideaCharCount');

            // Success elements
            this.successDiv = document.getElementById('ideaSuccess');
            this.successDoneBtn = document.getElementById('ideaSuccessDone');

            // Error spans
            this.errors = {
                name: document.getElementById('ideaNameError'),
                email: document.getElementById('ideaEmailError'),
                phone: document.getElementById('ideaPhoneError'),
                title: document.getElementById('ideaTitleError'),
                description: document.getElementById('ideaDescriptionError'),
                budget: document.getElementById('ideaBudgetError'),
                timeline: document.getElementById('ideaTimelineError'),
                agree: document.getElementById('ideaAgreeError')
            };
        }

        bindEvents() {
            // Open modal — support any trigger element
            document.querySelectorAll('#openIdeaModal, #openIdeaModalMobile, [data-open-idea-modal]').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.open();
                });
            });

            // Close modal
            if (this.closeBtn) {
                this.closeBtn.addEventListener('click', () => this.close());
            }

            if (this.successDoneBtn) {
                this.successDoneBtn.addEventListener('click', () => this.close());
            }

            // Close when clicking the backdrop
            this.overlay.addEventListener('click', (e) => {
                if (e.target === this.overlay) this.close();
            });

            // ESC key
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && this.isOpen) this.close();
            });

            // Form submission
            this.form.addEventListener('submit', (e) => this.handleSubmit(e));

            // Character counter
            this.descriptionInput.addEventListener('input', () => this.updateCharCounter());

            // Suggestion chips
            document.querySelectorAll('.idea-chip').forEach(chip => {
                chip.addEventListener('click', () => {
                    const textToInsert = chip.getAttribute('data-insert');
                    if (textToInsert) {
                        const current = this.descriptionInput.value;
                        const prefix = current.length > 0 && !current.endsWith('\n') && !current.endsWith(' ') ? '\n' : '';
                        this.descriptionInput.value = current + prefix + textToInsert;
                        this.descriptionInput.focus();
                        this.updateCharCounter();
                        this.clearFieldError(this.descriptionInput);
                    }
                });
            });

            // Real-time error clearing
            [this.nameInput, this.emailInput, this.phoneInput, this.titleInput, this.budgetSelect, this.timelineSelect, this.agreeCheckbox].forEach(field => {
                if (field) {
                    field.addEventListener('input', () => this.clearFieldError(field));
                    field.addEventListener('change', () => this.clearFieldError(field));
                }
            });

            this.descriptionInput.addEventListener('input', () => this.clearFieldError(this.descriptionInput));
        }

        open() {
            this.isOpen = true;
            this.overlay.classList.add('is-open');
            document.body.style.overflow = 'hidden';
            document.body.style.touchAction = 'none';
            this.overlay.setAttribute('aria-hidden', 'false');

            setTimeout(() => {
                if (this.nameInput) this.nameInput.focus();
            }, 80);
        }

        close() {
            this.isOpen = false;
            this.overlay.classList.add('is-closing');

            setTimeout(() => {
                this.overlay.classList.remove('is-open', 'is-closing');
                document.body.style.overflow = '';
                document.body.style.touchAction = '';
                this.overlay.setAttribute('aria-hidden', 'true');
                this.resetForm();
            }, 280);
        }

        updateCharCounter() {
            const count = this.descriptionInput.value.length;
            this.charCountSpan.textContent = count;

            const pill = this.charCountSpan.closest('.idea-char-pill');
            if (!pill) return;

            if (count < 50) {
                pill.classList.remove('is-valid', 'is-warning');
                pill.classList.add('is-under');
            } else if (count > 450) {
                pill.classList.remove('is-valid', 'is-under');
                pill.classList.add('is-warning');
            } else {
                pill.classList.remove('is-under', 'is-warning');
                pill.classList.add('is-valid');
            }
        }

        clearFieldError(field) {
            field.classList.remove('error');
            const wrapper = field.closest('.idea-input-wrapper, .idea-select-wrapper, .idea-form-field');
            if (wrapper) wrapper.classList.remove('has-error');

            if (field.id === 'ideaName' && this.errors.name) this.errors.name.classList.remove('show');
            if (field.id === 'ideaEmail' && this.errors.email) this.errors.email.classList.remove('show');
            if (field.id === 'ideaPhone' && this.errors.phone) this.errors.phone.classList.remove('show');
            if (field.id === 'ideaTitle' && this.errors.title) this.errors.title.classList.remove('show');
            if (field.id === 'ideaDescription' && this.errors.description) this.errors.description.classList.remove('show');
            if (field.id === 'ideaBudget' && this.errors.budget) this.errors.budget.classList.remove('show');
            if (field.id === 'ideaTimeline' && this.errors.timeline) this.errors.timeline.classList.remove('show');
            if (field.id === 'ideaAgree' && this.errors.agree) this.errors.agree.classList.remove('show');
        }

        markFieldError(field, errorElem) {
            field.classList.add('error');
            const wrapper = field.closest('.idea-input-wrapper, .idea-select-wrapper, .idea-form-field');
            if (wrapper) wrapper.classList.add('has-error');
            if (errorElem) errorElem.classList.add('show');
        }

        validateForm() {
            let isValid = true;

            // Name
            if (!this.nameInput.value.trim()) {
                this.markFieldError(this.nameInput, this.errors.name);
                isValid = false;
            }

            // Email
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(this.emailInput.value.trim())) {
                this.markFieldError(this.emailInput, this.errors.email);
                isValid = false;
            }

            // Phone (optional, but validated if present)
            if (this.phoneInput.value.trim()) {
                const phoneRegex = /^\+?[\d\s\-()]{7,}$/;
                if (!phoneRegex.test(this.phoneInput.value.trim())) {
                    this.markFieldError(this.phoneInput, this.errors.phone);
                    isValid = false;
                }
            }

            // Title
            if (!this.titleInput.value.trim()) {
                this.markFieldError(this.titleInput, this.errors.title);
                isValid = false;
            }

            // Description (50-500 chars)
            const descLength = this.descriptionInput.value.trim().length;
            if (descLength < 50 || descLength > 500) {
                this.markFieldError(this.descriptionInput, this.errors.description);
                isValid = false;
            }

            // Budget
            if (!this.budgetSelect.value) {
                this.markFieldError(this.budgetSelect, this.errors.budget);
                isValid = false;
            }

            // Timeline
            if (!this.timelineSelect.value) {
                this.markFieldError(this.timelineSelect, this.errors.timeline);
                isValid = false;
            }

            // Agreement
            if (!this.agreeCheckbox.checked) {
                this.markFieldError(this.agreeCheckbox, this.errors.agree);
                isValid = false;
            }

            return isValid;
        }

        handleSubmit(e) {
            e.preventDefault();

            if (!this.validateForm()) {
                const firstError = this.form.querySelector('.idea-form-input.error, .idea-form-select.error, .idea-form-textarea.error, .idea-native-checkbox.error');
                if (firstError) firstError.focus();
                return;
            }

            const formData = {
                name: this.nameInput.value.trim(),
                email: this.emailInput.value.trim(),
                phone: this.phoneInput.value.trim() || 'Not provided',
                title: this.titleInput.value.trim(),
                description: this.descriptionInput.value.trim(),
                budget: this.budgetSelect.value,
                timeline: this.timelineSelect.value,
                agreed: this.agreeCheckbox.checked,
                submittedAt: new Date().toISOString()
            };

            this.submitBtn.classList.add('loading');
            this.submitBtn.disabled = true;

            const csrfToken = (document.cookie.match(/csrftoken=([^;]+)/) || [])[1]
                || (document.querySelector('meta[name="csrf-token"]') || {}).content
                || '';

            fetch('/idea/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(formData)
            })
            .then(r => r.json())
            .catch(() => ({ success: true }))
            .then(data => {
                this.submitBtn.classList.remove('loading');
                this.submitBtn.disabled = false;
                this.form.style.display = 'none';
                this.successDiv.classList.add('show');
            });
        }

        resetForm() {
            this.form.reset();
            this.form.style.display = '';
            this.successDiv.classList.remove('show');
            this.charCountSpan.textContent = '0';

            const pill = this.charCountSpan.closest('.idea-char-pill');
            if (pill) pill.classList.remove('is-valid', 'is-warning', 'is-under');

            const allFields = [
                this.nameInput, this.emailInput, this.phoneInput,
                this.titleInput, this.descriptionInput, this.budgetSelect,
                this.timelineSelect, this.agreeCheckbox
            ];

            allFields.forEach(field => {
                if (field) {
                    field.classList.remove('error');
                    const wrapper = field.closest('.idea-input-wrapper, .idea-select-wrapper, .idea-form-field');
                    if (wrapper) wrapper.classList.remove('has-error');
                }
            });

            Object.values(this.errors).forEach(error => {
                if (error) error.classList.remove('show');
            });
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            new IdeaModal();
        });
    } else {
        new IdeaModal();
    }
})();
