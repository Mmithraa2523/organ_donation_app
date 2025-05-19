document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Flash message auto-close
    setTimeout(function() {
        let alerts = document.querySelectorAll('.alert:not(.alert-persistent)');
        alerts.forEach(function(alert) {
            let bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Form validation styles
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
    
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') {
                // Skip for links with just "#"
                return;
            }
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Auto-scroll to section if specified in URL
    const scrollTo = document.body.dataset.scrollTo;
    if (scrollTo) {
        const element = document.getElementById(scrollTo);
        if (element) {
            setTimeout(() => {
                element.scrollIntoView({
                    behavior: 'smooth'
                });
            }, 500);
        }
    }
    
    // Handle countdowns for OTP expiry
    const otpTimers = document.querySelectorAll('.otp-timer');
    
    otpTimers.forEach(timer => {
        const expiryTime = parseInt(timer.dataset.expiry);
        updateTimer(timer, expiryTime);
        
        const interval = setInterval(() => {
            if (updateTimer(timer, expiryTime) <= 0) {
                clearInterval(interval);
            }
        }, 1000);
    });
    
    // Function to update OTP timer
    function updateTimer(timerElement, expiryTime) {
        const now = Math.floor(Date.now() / 1000);
        const remainingTime = expiryTime - now;
        
        if (remainingTime <= 0) {
            timerElement.innerHTML = 'OTP expired';
            timerElement.classList.add('text-danger');
            
            // Disable submit button
            const form = timerElement.closest('form');
            if (form) {
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.disabled = true;
                }
            }
            
            return 0;
        }
        
        const minutes = Math.floor(remainingTime / 60);
        const seconds = remainingTime % 60;
        
        timerElement.innerHTML = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        
        return remainingTime;
    }
    
    // AJAX for resending OTP
    const resendOtpBtn = document.getElementById('resend-otp');
    if (resendOtpBtn) {
        resendOtpBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = resendOtpBtn.dataset.url;
            document.body.appendChild(form);
            form.submit();
        });
    }
    
    // Disable all transitions on the page
    const styleElement = document.createElement('style');
    styleElement.textContent = `
        *, *::before, *::after {
            transition: none !important;
            transform: none !important;
            animation: none !important;
        }
        
        .modal-backdrop {
            opacity: 0.5 !important;
        }
        
        .modal.fade .modal-dialog {
            transform: none !important;
        }
        
        .modal {
            background-color: rgba(0, 0, 0, 0.5) !important;
        }
    `;
    document.head.appendChild(styleElement);
    
    // Store the active modal instance
    let activeModal = null;
    
    // Function to handle verify button click
    function handleVerifyButtonClick(e) {
        // Prevent the default action to avoid any page refreshes or jumps
        e.preventDefault();
        e.stopPropagation();
        
        console.log("Button clicked");
        const btn = this;
        
        // Get the target modal
        const targetModalId = btn.getAttribute('data-bs-target');
        console.log("Target modal ID:", targetModalId);
        
        if (targetModalId) {
            const modalElement = document.querySelector(targetModalId);
            console.log("Modal element found:", modalElement ? true : false);
            
            if (modalElement) {
                try {
                    // Force the modal to open using Bootstrap
                    const modal = new bootstrap.Modal(modalElement, {
                        backdrop: 'static',  // Prevent closing when clicking outside
                        keyboard: false      // Prevent closing with keyboard
                    });
                    
                    // Store the modal instance globally
                    activeModal = modal;
                    
                    console.log("Modal instance created");
                    modal.show();
                    console.log("Modal show() called");
                    
                    // Keep the modal open for at least 30 seconds
                    const closeButtons = modalElement.querySelectorAll('[data-bs-dismiss="modal"]');
                    closeButtons.forEach(btn => {
                        btn.style.display = 'none'; // Hide the close button initially
                        
                        setTimeout(() => {
                            btn.style.display = ''; // Show the close button after 30 seconds
                        }, 30000);
                    });
                    
                    // Disable backdrop click to close for 30 seconds
                    setTimeout(() => {
                        // Allow closing after 30 seconds
                        console.log("Modal now closeable");
                    }, 30000);
                    
                } catch (error) {
                    console.error("Error showing modal:", error);
                }
            } else {
                console.error("Modal element not found with selector:", targetModalId);
            }
        } else {
            console.error("No target modal ID found on button");
        }
    }
    
    // Fix for verify collection buttons with debugging
    const verifyCollectionBtns = document.querySelectorAll('.verify-collection-btn');
    console.log("Found verify collection buttons:", verifyCollectionBtns.length);
    
    verifyCollectionBtns.forEach(btn => {
        console.log("Button:", btn.outerHTML);
        console.log("Target modal:", btn.getAttribute('data-bs-target'));
        
        // Remove the default bootstrap data-bs-toggle behavior
        btn.removeAttribute('data-bs-toggle');
        
        // Add our custom click handler
        btn.addEventListener('click', handleVerifyButtonClick);
    });
});
