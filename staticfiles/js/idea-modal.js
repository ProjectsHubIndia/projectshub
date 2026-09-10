/* ════════════════════════════════════════════════════════════
   Share Your Idea Modal — Interaction & Validation Logic
   Features: Form validation, character counter, accessibility
   ════════════════════════════════════════════════════════════ */

(function () {
    'use strict';

    class IdeaModal {
        constructor() {
            this.isOpen = false;
            this.init();
        }

        init() {
            // Inject modal HTML if not already present
            this.createModalHTML();
            this.cacheElements();
            this.bindEvents();
        }

        createModalHTML() {
            // Check if modal already exists
            if (document.getElementById('ideaModalOverlay')) {
                return;
            }

            const html = `
                <div class="idea-modal-overlay" id="ideaModalOverlay" role="presentation">
                    <div class="idea-modal" role="dialog" aria-modal="true" aria-labelledby="ideaModalTitle" id="ideaModal">
                        <!-- Header -->
                        <div class="idea-modal-header">
                            <h2 class="idea-modal-title" id="ideaModalTitle">
                                Share Your <span class="idea-modal-title-accent">Idea</span>
                            </h2>
                            <button class="idea-modal-close-btn" id="ideaModalClose" aria-label="Close modal">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
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
                                        <input type="text" id="ideaName" class="idea-form-input" placeholder="John Doe" required />
                                        <span class="idea-form-error" id="ideaNameError">Name is required</span>
                                    </div>
                                    <div class="idea-form-field">
                                        <label for="ideaEmail" class="idea-form-label">
                                            Email Address <span class="idea-form-label-required">*</span>
                                        </label>
                                        <input type="email" id="ideaEmail" class="idea-form-input" placeholder="you@example.com" required />
                                        <span class="idea-form-error" id="ideaEmailError">Valid email is required</span>
                                    </div>
                                </div>

                                <!-- Phone & Title Row -->
                                <div class="idea-form-row">
                                    <div class="idea-form-field">
                                        <label for="ideaPhone" class="idea-form-label">Phone Number</label>
                                        <input type="tel" id="ideaPhone" class="idea-form-input" placeholder="+1 (555) 000-0000" />
                                        <span class="idea-form-error" id="ideaPhoneError">Invalid phone format</span>
                                    </div>
                                    <div class="idea-form-field">
                                        <label for="ideaTitle" class="idea-form-label">
                                            Project/Idea Title <span class="idea-form-label-required">*</span>
                                        </label>
                                        <input type="text" id="ideaTitle" class="idea-form-input" placeholder="Your project name" required />
                                        <span class="idea-form-error" id="ideaTitleError">Title is required</span>
                                    </div>
                                </div>

                                <!-- Description -->
                                <div class="idea-form-field">
                                    <label for="ideaDescription" class="idea-form-label">
                                        Idea Description <span class="idea-form-label-required">*</span>
                                    </label>
                                    <textarea id="ideaDescription" class="idea-form-textarea" placeholder="Tell us about your idea... (50-500 characters)" required></textarea>
                                    <div class="idea-form-helper">
                                        <span class="idea-form-error" id="ideaDescriptionError">Description must be 50-500 characters</span>
                                        <span class="idea-form-char-count"><span id="ideaCharCount">0</span>/500</span>
                                    </div>
                                </div>

                                <!-- Budget & Timeline Row -->
                                <div class="idea-form-row">
                                    <div class="idea-form-field">
                                        <label for="ideaBudget" class="idea-form-label">
                                            Budget Range <span class="idea-form-label-required">*</span>
                                        </label>
                                        <select id="ideaBudget" class="idea-form-select" required>
                                            <option value="">Select a range</option>
                                            <option value="under-1k">Under $1K</option>
                                            <option value="1k-5k">$1K – $5K</option>
                                            <option value="5k-10k">$5K – $10K</option>
                                            <option value="10k-plus">$10K+</option>
                                            <option value="not-sure">Not sure yet</option>
                                        </select>
                                        <span class="idea-form-error" id="ideaBudgetError">Budget range is required</span>
                                    </div>
                                    <div class="idea-form-field">
                                        <label for="ideaTimeline" class="idea-form-label">
                                            Preferred Timeline <span class="idea-form-label-required">*</span>
                                        </label>
                                        <select id="ideaTimeline" class="idea-form-select" required>
                                            <option value="">Select timeline</option>
                                            <option value="asap">ASAP</option>
                                            <option value="1-2-weeks">1–2 weeks</option>
                                            <option value="1-month">1 month</option>
                                            <option value="2-3-months">2–3 months</option>
                                            <option value="flexible">Flexible</option>
                                        </select>
                                        <span class="idea-form-error" id="ideaTimelineError">Timeline is required</span>
                                    </div>
                                </div>

                                <!-- Agreement Checkbox -->
                                <div class="idea-form-field">
                                    <div class="idea-form-checkbox-wrap">
                                        <input type="checkbox" id="ideaAgree" class="idea-form-checkbox" required />
                                        <label for="ideaAgree" class="idea-form-checkbox-label">
                                            I agree to be contacted about this idea
                                        </label>
                                    </div>
                                    <span class="idea-form-error" id="ideaAgreeError">You must agree to be contacted</span>
                                </div>

                                <!-- Submit Button -->
                                <button type="submit" class="idea-form-submit" id="ideaSubmitBtn">
                                    <span class="idea-spinner"></span>
                                    <span class="idea-submit-text">Send My Idea</span>
                                </button>
                            </form>

                            <!-- Success State -->
                            <div class="idea-modal-success" id="ideaSuccess">
                                <div class="idea-success-icon">
                                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                                        <polyline points="20 6 9 17 4 12"></polyline>
                                    </svg>
                                </div>
                                <h3 class="idea-success-title">Thanks!</h3>
                                <p class="idea-success-message">We'll reach out soon to discuss your amazing idea.</p>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            document.body.insertAdjacentHTML('beforeend', html);
        }

        cacheElements() {
            // Modal elements
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
            // Open modal — support any element with data-open-idea-modal or known IDs
            document.querySelectorAll('#openIdeaModal, #openIdeaModalMobile, [data-open-idea-modal]').forEach(btn => {
                btn.addEventListener('click', () => this.open());
            });

            // Close modal
            this.closeBtn.addEventListener('click', () => this.close());

            // Close only when clicking the translucent overlay backdrop, not the modal card itself
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

            // Real-time field clearing on input
            [this.nameInput, this.emailInput, this.titleInput, this.budgetSelect, this.timelineSelect, this.agreeCheckbox].forEach(field => {
                if (field) {
                    field.addEventListener('input', () => this.clearFieldError(field));
                    // Also clear on change for select elements
                    field.addEventListener('change', () => this.clearFieldError(field));
                }
            });

            this.descriptionInput.addEventListener('input', () => this.clearFieldError(this.descriptionInput));
        }

        open() {
            this.isOpen = true;
            this.overlay.classList.add('is-open');
            // Lock background scroll on all browsers including iOS
            document.body.style.overflow = 'hidden';
            document.body.style.touchAction = 'none';
            this.overlay.setAttribute('aria-hidden', 'false');

            // Move focus into the modal for screen readers
            setTimeout(() => {
                if (this.nameInput) this.nameInput.focus();
            }, 80);
        }

        close() {
            this.isOpen = false;
            this.overlay.classList.add('is-closing');

            setTimeout(() => {
                this.overlay.classList.remove('is-open', 'is-closing');
                // Restore scroll
                document.body.style.overflow = '';
                document.body.style.touchAction = '';
                this.overlay.setAttribute('aria-hidden', 'true');
                this.resetForm();
            }, 300);
        }

        updateCharCounter() {
            const count = this.descriptionInput.value.length;
            this.charCountSpan.textContent = count;

            // Update color based on count
            if (count < 50) {
                this.charCountSpan.classList.add('error');
                this.charCountSpan.classList.remove('warning');
            } else if (count > 450) {
                this.charCountSpan.classList.add('warning');
                this.charCountSpan.classList.remove('error');
            } else {
                this.charCountSpan.classList.remove('error', 'warning');
            }
        }

        clearFieldError(field) {
            field.classList.remove('error');
            if (field.id === 'ideaName' && this.errors.name) this.errors.name.classList.remove('show');
            if (field.id === 'ideaEmail' && this.errors.email) this.errors.email.classList.remove('show');
            if (field.id === 'ideaPhone' && this.errors.phone) this.errors.phone.classList.remove('show');
            if (field.id === 'ideaTitle' && this.errors.title) this.errors.title.classList.remove('show');
            if (field.id === 'ideaDescription' && this.errors.description) this.errors.description.classList.remove('show');
            if (field.id === 'ideaBudget' && this.errors.budget) this.errors.budget.classList.remove('show');
            if (field.id === 'ideaTimeline' && this.errors.timeline) this.errors.timeline.classList.remove('show');
            if (field.id === 'ideaAgree' && this.errors.agree) this.errors.agree.classList.remove('show');
        }

        validateForm() {
            let isValid = true;

            // Name validation
            if (!this.nameInput.value.trim()) {
                this.nameInput.classList.add('error');
                this.errors.name.classList.add('show');
                isValid = false;
            }

            // Email validation
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(this.emailInput.value)) {
                this.emailInput.classList.add('error');
                this.errors.email.classList.add('show');
                isValid = false;
            }

            // Phone validation (optional, but if filled, must be valid)
            if (this.phoneInput.value.trim()) {
                const phoneRegex = /^\+?[\d\s\-()]{10,}$/;
                if (!phoneRegex.test(this.phoneInput.value)) {
                    this.phoneInput.classList.add('error');
                    this.errors.phone.classList.add('show');
                    isValid = false;
                }
            }

            // Title validation
            if (!this.titleInput.value.trim()) {
                this.titleInput.classList.add('error');
                this.errors.title.classList.add('show');
                isValid = false;
            }

            // Description validation (50-500 chars)
            const descLength = this.descriptionInput.value.trim().length;
            if (descLength < 50 || descLength > 500) {
                this.descriptionInput.classList.add('error');
                this.errors.description.classList.add('show');
                isValid = false;
            }

            // Budget validation
            if (!this.budgetSelect.value) {
                this.budgetSelect.classList.add('error');
                this.errors.budget.classList.add('show');
                isValid = false;
            }

            // Timeline validation
            if (!this.timelineSelect.value) {
                this.timelineSelect.classList.add('error');
                this.errors.timeline.classList.add('show');
                isValid = false;
            }

            // Agreement checkbox
            if (!this.agreeCheckbox.checked) {
                this.agreeCheckbox.classList.add('error');
                this.errors.agree.classList.add('show');
                isValid = false;
            }

            return isValid;
        }

        handleSubmit(e) {
            e.preventDefault();

            // Validate
            if (!this.validateForm()) {
                console.log('Form validation failed');
                return;
            }

            // Get form data
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

            // Show loading state
            this.submitBtn.classList.add('loading');
            this.submitBtn.disabled = true;

            // Submit to backend
            const csrfToken = (document.cookie.match(/csrftoken=([^;]+)/) || [])[1]
                || (document.querySelector('meta[name="csrf-token"]') || {}).content
                || '';
            fetch('/idea/', {
                method: 'POST',
                headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrfToken},
                body: JSON.stringify(formData)
            }).then(r => r.json()).catch(() => ({success: true})).then(data => {
                this.submitBtn.classList.remove('loading');
                this.submitBtn.disabled = false;
                this.form.style.display = 'none';
                this.successDiv.classList.add('show');
                setTimeout(() => { this.close(); }, 3000);
            });
        }

        resetForm() {
            this.form.reset();
            this.form.style.display = '';
            this.successDiv.classList.remove('show');
            this.charCountSpan.textContent = '0';

            // Clear all error states
            const allFields = [
                this.nameInput, this.emailInput, this.phoneInput,
                this.titleInput, this.descriptionInput, this.budgetSelect,
                this.timelineSelect, this.agreeCheckbox
            ];

            allFields.forEach(field => {
                if (field) field.classList.remove('error');
            });

            Object.values(this.errors).forEach(error => {
                error.classList.remove('show');
            });
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            new IdeaModal();
        });
    } else {
        new IdeaModal();
    }
})();
