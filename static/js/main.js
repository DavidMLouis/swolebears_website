// static/js/main.js

document.addEventListener('DOMContentLoaded', () => {

    // 1. UTM Param capturing
    const urlParams = new URLSearchParams(window.location.search);
    const utms = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'source'];
    
    // Store in sessionStorage if present in URL
    utms.forEach(param => {
        if (urlParams.has(param)) {
            sessionStorage.setItem(param, urlParams.get(param));
        }
    });

    // 2. Form Submission Handling
    const forms = document.querySelectorAll('.waitlist-form');
    
    forms.forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.innerHTML;
            const msgContainer = form.querySelector('.form-message');
            const formInputs = form.querySelectorAll('input:not([type="hidden"])');
            
            // Set loading state
            submitBtn.innerHTML = `
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg> Joining...`;
            submitBtn.disabled = true;
            if(msgContainer) {
                msgContainer.innerHTML = '';
                msgContainer.className = 'form-message hidden mt-3 text-sm';
            }

            // Gather Data
            const formData = new FormData(form);
            const jsonData = Object.fromEntries(formData.entries());
            
            // Inject UTMs and Landing Page Meta
            utms.forEach(param => {
                if (sessionStorage.getItem(param)) {
                    jsonData[param] = sessionStorage.getItem(param);
                }
            });
            jsonData['landing_page'] = window.location.href;

            // Include CSRF Token
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

            try {
                const response = await fetch('/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify(jsonData)
                });

                const data = await response.json();

                if (msgContainer) {
                    msgContainer.classList.remove('hidden');
                    if (data.success) {
                        msgContainer.classList.add('text-green-400');
                        msgContainer.textContent = data.message;
                        formInputs.forEach(input => input.disabled = true);
                        submitBtn.innerHTML = `✔ waitlisted!`;
                        submitBtn.classList.replace('bg-brand-red', 'bg-green-600');
                        submitBtn.classList.remove('hover:bg-red-700');
                        
                        // Optionally trigger a success event for Analytics / Pixel
                        if (typeof gtag !== 'undefined') {
                            // placeholder event tracking
                            // gtag('event', 'generate_lead', { currency: 'USD', value: 0 });
                        }
                    } else {
                        msgContainer.classList.add('text-red-400');
                        msgContainer.textContent = data.error || 'Something went wrong. Please try again.';
                        submitBtn.innerHTML = originalBtnText;
                        submitBtn.disabled = false;
                    }
                }

            } catch (err) {
                console.error('Form submission error:', err);
                if (msgContainer) {
                    msgContainer.classList.remove('hidden');
                    msgContainer.classList.add('text-red-400');
                    msgContainer.textContent = 'A network error occurred. Please try again.';
                }
                submitBtn.innerHTML = originalBtnText;
                submitBtn.disabled = false;
            }
        });
    });

    // 3. Sticky Mobile CTA Interaction
    const stickyCta = document.getElementById('sticky-cta');
    const heroForm = document.getElementById('hero-form');
    
    if (stickyCta && heroForm) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                // Determine screen width context
                if (window.innerWidth < 768) {
                    if (!entry.isIntersecting) {
                        // Form is out of view, show sticky bar
                        stickyCta.classList.remove('translate-y-full');
                        stickyCta.classList.add('translate-y-0');
                    } else {
                        // Form is in view, hide sticky bar
                        stickyCta.classList.add('translate-y-full');
                        stickyCta.classList.remove('translate-y-0');
                    }
                }
            });
        }, { threshold: 0.1 });

        observer.observe(heroForm);
    }
    
    // Smooth scrolling for sticky CTA anchor
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if(target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // 4. FAQ Accordion Logic
    const faqDetails = document.querySelectorAll('.faq-item details');
    faqDetails.forEach((targetDetail) => {
        targetDetail.addEventListener('click', () => {
            // Close all the details that are not targetDetail.
            faqDetails.forEach((detail) => {
                if (detail !== targetDetail) {
                    detail.removeAttribute('open');
                }
            });
        });
    });
});
