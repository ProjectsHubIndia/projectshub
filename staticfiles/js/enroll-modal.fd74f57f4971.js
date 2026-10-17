/* ═══════════════════════════════════════════
   ENROLLMENT MODAL
   ═══════════════════════════════════════════ */

(function () {
    const modal = document.getElementById('enrollModal');
    const closeBtn = document.getElementById('enrollClose');
    const backdrop = document.getElementById('enrollBackdrop');
    const form = document.getElementById('enrollForm');
    const successState = document.getElementById('enrollSuccess');
    const successCloseBtn = document.getElementById('enrollSuccessClose');
    const submitBtn = document.getElementById('enrollSubmit');
    const charCount = document.getElementById('charCount');
    const messageField = document.getElementById('enrollMessage');

    if (!modal) return; // safety guard if modal not on page

    let lastFocusedElement = null;

    // Open modal
    function openModal() {
        lastFocusedElement = document.activeElement;
        modal.classList.add('is-active');
        document.body.style.overflow = 'hidden';
        setTimeout(() => {
            document.getElementById('enrollName').focus();
        }, 100);
    }

    // Close modal
    function closeModal() {
        modal.classList.remove('is-active');
        document.body.style.overflow = '';
        if (lastFocusedElement) lastFocusedElement.focus();
        setTimeout(() => resetForm(), 350);
    }

    // Reset form
    function resetForm() {
        form.reset();
        form.classList.remove('is-hidden');
        successState.classList.remove('is-visible');
        submitBtn.classList.remove('is-loading');
        submitBtn.disabled = false;
        charCount.textContent = '0 / 300';
        document.querySelectorAll('.enroll-field').forEach(f => f.classList.remove('has-error'));
    }

    // Validate email
    function isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    // Validate form
    function validateForm() {
        let isValid = true;

        const name = document.getElementById('enrollName');
        const nameField = name.closest('.enroll-field');
        if (!name.value.trim() || name.value.trim().length < 2) {
            nameField.classList.add('has-error'); isValid = false;
        } else {
            nameField.classList.remove('has-error');
        }

        const email = document.getElementById('enrollEmail');
        const emailField = email.closest('.enroll-field');
        if (!email.value.trim() || !isValidEmail(email.value.trim())) {
            emailField.classList.add('has-error'); isValid = false;
        } else {
            emailField.classList.remove('has-error');
        }
       
        const exp = document.getElementById('enrollExperience');
        const expField = exp.closest('.enroll-field');
        if (!exp.value) {
            expField.classList.add('has-error'); isValid = false;
        } else {
            expField.classList.remove('has-error');
        }
        const phone = document.getElementById('enrollPhone');
        const phoneField = phone.closest('.enroll-field');
        if (!phone.value.trim() || phone.value.trim().length < 8) {
            phoneField.classList.add('has-error'); isValid = false;
        } else {
            phoneField.classList.remove('has-error');
        }
 

        return isValid;
    }

    // Character counter
    if (messageField) {
        messageField.addEventListener('input', () => {
            const len = messageField.value.length;
            charCount.textContent = `${len} / 300`;
            charCount.style.color = len >= 300 ? '#ef4444' : '';
        });
    }

    // Clear error on input/change
    form.querySelectorAll('.enroll-field__input, .enroll-checkbox input').forEach(input => {
        input.addEventListener('input', () => input.closest('.enroll-field').classList.remove('has-error'));
        input.addEventListener('change', () => input.closest('.enroll-field').classList.remove('has-error'));
    });



//submit

// Get CSRF token from cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        document.cookie.split(';').forEach(cookie => {
            const c = cookie.trim();
            if (c.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(c.substring(name.length + 1));
            }
        });
    }
    // Fallback: read from <meta name="csrf-token"> if cookie not set
    if (!cookieValue && name === 'csrftoken') {
        const meta = document.querySelector('meta[name="csrf-token"]');
        if (meta) cookieValue = meta.getAttribute('content');
    }
    return cookieValue;
}

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    submitBtn.classList.add('is-loading');
    submitBtn.disabled = true;

    const workshopHiddenInput = document.getElementById('enrollWorkshopId');
    const workshopBtn = document.querySelector('.open-enroll-modal[data-workshop-id]');
    const workshopId = activeWorkshopId || (workshopHiddenInput ? workshopHiddenInput.value : null) || (workshopBtn ? workshopBtn.dataset.workshopId : null);

    const formData = {
        fullName: document.getElementById('enrollName').value.trim(),
        email: document.getElementById('enrollEmail').value.trim(),
        phone: document.getElementById('enrollPhone').value.trim(),
        experience: document.getElementById('enrollExperience').value,
        referral: '',
        message: document.getElementById('enrollMessage').value.trim(),
        agreed: true,
        workshopId: workshopId
    };

    try {
        const response = await fetch('/enroll/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(formData)
        });

        const result = await response.json();

        if (result.success) {
            document.getElementById('successName').textContent = formData.fullName.split(' ')[0];
            document.getElementById('successEmail').textContent = formData.email;
            form.classList.add('is-hidden');
            successState.classList.add('is-visible');
            setTimeout(() => {
                if (modal.classList.contains('is-active')) closeModal();
            }, 5000);
        } else {
            alert(result.message || 'Something went wrong. Please try again.');
            submitBtn.classList.remove('is-loading');
            submitBtn.disabled = false;
        }

    } catch (err) {
        console.error('Enrollment error:', err);
        alert('Network error. Please check your connection and try again.');
        submitBtn.classList.remove('is-loading');
        submitBtn.disabled = false;
    }
});
    let activeWorkshopId = null;

    // ✅ Bind all current buttons & delegate clicks for maximum reliability
    document.querySelectorAll('.open-enroll-modal, #openEnrollModal, #openEnrollModalMobile')
        .forEach(btn => btn.addEventListener('click', function(e) {
            activeWorkshopId = this.dataset?.workshopId || null;
            openModal();
        }));

    document.addEventListener('click', function (e) {
        const trigger = e.target.closest('.open-enroll-modal, #openEnrollModal, #openEnrollModalMobile');
        if (trigger) {
            e.preventDefault();
            activeWorkshopId = trigger.dataset?.workshopId || null;
            openModal();
        }
    });

    closeBtn?.addEventListener('click', closeModal);
    backdrop?.addEventListener('click', closeModal);
    successCloseBtn?.addEventListener('click', closeModal);

    // Keyboard ESC
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('is-active')) closeModal();
    });

    // Focus trap
    modal.addEventListener('keydown', (e) => {
        if (e.key !== 'Tab') return;
        const focusables = modal.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        const first = focusables[0];
        const last = focusables[focusables.length - 1];
        if (e.shiftKey && document.activeElement === first) {
            e.preventDefault(); last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
            e.preventDefault(); first.focus();
        }
    });

})();