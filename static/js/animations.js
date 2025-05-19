// Animations using JS and CSS animations
document.addEventListener('DOMContentLoaded', function() {
    // Animate elements when they come into view
    const animateOnScroll = function() {
        const elements = document.querySelectorAll('.animate-on-scroll');
        
        elements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            const elementHeight = element.offsetHeight;
            const windowHeight = window.innerHeight;
            
            if (elementTop < windowHeight - elementHeight / 2) {
                const animationType = element.dataset.animation || 'fade-in';
                element.classList.add(animationType);
                element.classList.remove('animate-on-scroll');
            }
        });
    };
    
    // Run once on page load
    animateOnScroll();
    
    // Run on scroll
    window.addEventListener('scroll', animateOnScroll);
    
    // Hero section pulse animation
    const heroBtn = document.querySelector('.hero-btn');
    if (heroBtn) {
        setInterval(() => {
            heroBtn.classList.add('pulse');
            
            setTimeout(() => {
                heroBtn.classList.remove('pulse');
            }, 1000);
        }, 3000);
    }
    
    // Animated counter for statistics
    const counters = document.querySelectorAll('.counter');
    
    counters.forEach(counter => {
        const target = parseInt(counter.getAttribute('data-target'));
        const duration = 2000; // Animation duration in ms
        const step = target / (duration / 16); // 60fps approx
        let current = 0;
        
        const updateCounter = () => {
            current += step;
            const progress = Math.min(current, target);
            counter.textContent = Math.round(progress);
            
            if (progress < target) {
                requestAnimationFrame(updateCounter);
            } else {
                counter.textContent = target;
            }
        };
        
        const observer = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    updateCounter();
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });
        
        observer.observe(counter);
    });
    
    // Animate SVG paths
    const svgPaths = document.querySelectorAll('.animate-path path');
    
    svgPaths.forEach(path => {
        const length = path.getTotalLength();
        
        // Set up the starting position
        path.style.strokeDasharray = length;
        path.style.strokeDashoffset = length;
        
        // Create the animation
        path.animate(
            [
                { strokeDashoffset: length },
                { strokeDashoffset: 0 }
            ],
            {
                duration: 2000,
                fill: 'forwards',
                easing: 'ease-in-out'
            }
        );
    });
    
    // Add wave animation to hero section
    const hero = document.querySelector('.hero');
    if (hero) {
        const wave = document.createElement('div');
        wave.classList.add('wave-animation');
        hero.appendChild(wave);
        
        for (let i = 0; i < 3; i++) {
            const waveInner = document.createElement('div');
            waveInner.classList.add('wave', `wave-${i+1}`);
            wave.appendChild(waveInner);
        }
    }
    
    // Animate heart beat for health-related elements
    const heartIcons = document.querySelectorAll('.heart-icon');
    
    heartIcons.forEach(icon => {
        setInterval(() => {
            icon.classList.add('heart-beat');
            
            setTimeout(() => {
                icon.classList.remove('heart-beat');
            }, 1000);
        }, 2500);
    });
    
    // Add floating animation to cards
    const floatingCards = document.querySelectorAll('.floating-card');
    
    floatingCards.forEach((card, index) => {
        const direction = index % 2 === 0 ? 1 : -1;
        const delay = index * 0.2;
        
        card.style.animation = `floating ${3 + index * 0.5}s ease-in-out infinite alternate`;
        card.style.animationDelay = `${delay}s`;
    });
    
    // Add typing animation for hero text
    const typingText = document.querySelector('.typing-text');
    if (typingText) {
        const text = typingText.textContent;
        typingText.textContent = '';
        
        let i = 0;
        const typeWriter = () => {
            if (i < text.length) {
                typingText.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, 100);
            }
        };
        
        typeWriter();
    }
});

// CSS Animations
document.head.insertAdjacentHTML('beforeend', `
<style>
@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}

.pulse {
    animation: pulse 1s ease-in-out;
}

@keyframes heart-beat {
    0% { transform: scale(1); }
    15% { transform: scale(1.3); }
    30% { transform: scale(1); }
    45% { transform: scale(1.3); }
    60% { transform: scale(1); }
    100% { transform: scale(1); }
}

.heart-beat {
    animation: heart-beat 1.5s ease-in-out;
    color: #e74c3c;
}

@keyframes floating {
    0% { transform: translateY(0px); }
    100% { transform: translateY(-15px); }
}

.wave-animation {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 100px;
    overflow: hidden;
}

.wave {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 200%;
    height: 100%;
    background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1440 320'%3E%3Cpath fill='%233498db' fill-opacity='0.5' d='M0,192L60,176C120,160,240,128,360,122.7C480,117,600,139,720,149.3C840,160,960,160,1080,138.7C1200,117,1320,75,1380,53.3L1440,32L1440,320L1380,320C1320,320,1200,320,1080,320C960,320,840,320,720,320C600,320,480,320,360,320C240,320,120,320,60,320L0,320Z'%3E%3C/path%3E%3C/svg%3E") repeat-x;
    background-position: 0 bottom;
    background-size: 50% 100px;
}

.wave-1 {
    animation: wave 30s linear infinite;
    opacity: 0.3;
    animation-delay: 0s;
    bottom: 0;
}

.wave-2 {
    animation: wave 20s linear infinite;
    opacity: 0.5;
    animation-delay: -5s;
    bottom: 10px;
}

.wave-3 {
    animation: wave 15s linear infinite;
    opacity: 0.7;
    animation-delay: -2s;
    bottom: 20px;
}

@keyframes wave {
    0% { transform: translateX(0); }
    100% { transform: translateX(-50%); }
}
</style>
`);
