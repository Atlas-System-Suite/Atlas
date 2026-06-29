document.addEventListener("DOMContentLoaded", () => {
    // ----------------------------------------------------
    // 0. TSPARTICLES (Home Page Hero: Workers & Models)
    // ----------------------------------------------------
    function initParticles() {
        if (typeof tsParticles === 'undefined') return;
        if (!document.getElementById('home-particles')) return; 

        tsParticles.load("home-particles", {
            fpsLimit: 60,
            interactivity: {
                events: { onHover: { enable: true, mode: "grab" } },
                modes: { grab: { distance: 150, links: { opacity: 0.8, color: "#ef4444" } } },
            },
            particles: {
                color: { value: ["#3b82f6", "#10b981", "#ef4444"] },
                links: { color: "#94a3b8", distance: 120, enable: true, opacity: 0.3, width: 1.5 },
                move: { enable: true, speed: 1.2, direction: "none", random: true, straight: false, outModes: "bounce" },
                number: { value: 50, density: { enable: true, area: 800 } },
                opacity: { value: 0.8 },
                shape: { type: "circle" },
                size: { value: { min: 2, max: 5 } },
            },
            detectRetina: true,
        });
    }

    // ----------------------------------------------------
    // 1. TYPED.JS (Hacker Terminal Effect)
    // ----------------------------------------------------
    function initTyped() {
        if (typeof Typed === 'undefined') return;
        const headers = document.querySelectorAll('.atlas-chapter-title');
        headers.forEach((header) => {
            const originalText = header.innerText;
            header.innerText = ''; 
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        new Typed(header, {
                            strings: [originalText], typeSpeed: 40, showCursor: true, cursorChar: '█',
                            onComplete: (self) => { setTimeout(() => { self.cursor.style.display = 'none'; }, 1000); }
                        });
                        observer.unobserve(header);
                    }
                });
            });
            observer.observe(header);
        });
    }

    // ----------------------------------------------------
    // 2. ANIME.JS (Universal Translator Funnel)
    // ----------------------------------------------------
    function initAnime() {
        if (typeof anime === 'undefined') return;
        const funnelContainer = document.querySelector('.funnel-container');
        if (funnelContainer) {
            const tl = anime.timeline({ loop: true });
            
            // Suck chaotic nodes into the funnel
            tl.add({
                targets: '.chaotic-node',
                translateX: () => anime.random(100, 150),
                translateY: () => anime.random(10, -10),
                scale: 0,
                rotate: '1turn',
                opacity: 0,
                duration: 1000,
                delay: anime.stagger(200),
                easing: 'easeInBack'
            })
            // Flash binary stream
            .add({
                targets: '.binary-stream',
                opacity: [0, 1, 0, 1, 0],
                duration: 800,
                easing: 'linear'
            })
            // Pop out ordered nodes
            .add({
                targets: '.ordered-node',
                translateX: [0, 50],
                opacity: [0, 1],
                duration: 800,
                delay: anime.stagger(200),
                easing: 'easeOutElastic(1, .5)'
            })
            // Reset
            .add({
                targets: ['.chaotic-node', '.ordered-node'],
                opacity: [1, 0],
                duration: 500,
                easing: 'linear'
            });
        }
    }

    // ----------------------------------------------------
    // 3. GSAP (The Grand Reimagined Physics)
    // ----------------------------------------------------
    function initGSAP() {
        if (typeof gsap === 'undefined') return;

        // Header ScrollTrigger
        if (typeof ScrollTrigger !== 'undefined') {
            gsap.registerPlugin(ScrollTrigger);
            const header = document.querySelector('.md-header');
            if (header) {
                gsap.to(header, {
                    scrollTrigger: { trigger: document.body, start: "top top", end: "+=800", scrub: 3 },
                    y: -80, opacity: 0, filter: "blur(15px)", ease: "power2.inOut"
                });
            }
        }

        // 1. Worker Lifecycle (State Machine Cylinder)
        const lfContainer = document.querySelector('.new-lifecycle-container');
        if (lfContainer) {
            const tl = gsap.timeline({ repeat: -1, repeatDelay: 1.5 });
            gsap.set('.state-plane', { opacity: 0.3 });
            gsap.set('.cylinder-core', { opacity: 0, scaleY: 0, transformOrigin: "top center" });
            
            tl.to('.cylinder-core', { opacity: 1, scaleY: 0.25, duration: 0.5, ease: "power3.in" })
              .to('.plane-boot', { opacity: 1, backgroundColor: "rgba(239, 68, 68, 0.4)", boxShadow: "0 0 30px rgba(239,68,68,0.5)", duration: 0.3 })
              .to('.cylinder-core', { scaleY: 0.5, duration: 0.5, ease: "power3.inOut" }, "+=0.5")
              .to('.plane-resolve', { opacity: 1, backgroundColor: "rgba(59, 130, 246, 0.4)", boxShadow: "0 0 30px rgba(59,130,246,0.5)", duration: 0.3 })
              .to('.cylinder-core', { scaleY: 0.75, duration: 0.5, ease: "power3.inOut" }, "+=0.5")
              .to('.plane-ready', { opacity: 1, backgroundColor: "rgba(16, 185, 129, 0.4)", boxShadow: "0 0 30px rgba(16,185,129,0.5)", duration: 0.3 })
              .to('.cylinder-core', { scaleY: 1, duration: 0.5, ease: "power3.inOut" }, "+=0.5")
              .to('.plane-term', { opacity: 1, backgroundColor: "rgba(239, 68, 68, 0.4)", boxShadow: "0 0 30px rgba(239,68,68,0.5)", duration: 0.3 })
              .to('.cylinder-core', { opacity: 0, duration: 0.5 }, "+=1")
              .to('.state-plane', { opacity: 0.3, backgroundColor: "rgba(15,23,42,0.8)", boxShadow: "none", duration: 0.5 }, "<");
        }

        // 2. Boot Sequence (Matrix Grid Sweep)
        const bootContainer = document.querySelector('.gsap-boot-anim');
        if (bootContainer) {
            const tl = gsap.timeline({ repeat: -1, repeatDelay: 2 });
            gsap.set('.sonar-ring', { scale: 0, opacity: 1 });
            gsap.set('.matrix-node', { opacity: 0, z: -100 });
            
            tl.to('.matrix-core', { scale: 1.2, duration: 0.5, yoyo: true, repeat: 1, ease: "back.out(2)" })
              .to('.sonar-ring', { scale: 1, opacity: 0, duration: 1.5, ease: "power3.out" }, "-=0.2")
              .to('.matrix-node', { opacity: 1, z: 0, duration: 0.8, stagger: 0.2, ease: "elastic.out(1, 0.5)", backgroundColor: "#3b82f6", boxShadow: "0 0 20px #3b82f6" }, "-=1.2")
              .to('.matrix-node', { opacity: 0, z: -100, duration: 0.5, stagger: 0.1, ease: "power2.in" }, "+=1.5");
        }

        // 3. Room Sandboxing (Containment Sphere)
        const roomContainer = document.querySelector('.gsap-room-anim');
        if (roomContainer) {
            const tl = gsap.timeline({ repeat: -1 });
            gsap.to('.containment-sphere', { rotation: 360, duration: 10, repeat: -1, ease: "none" });
            
            // Violent worker bouncing inside the sphere
            tl.to('.violent-worker', { x: -60, y: -40, duration: 0.4, ease: "power1.inOut" })
              .to('.containment-flash', { opacity: 1, duration: 0.1, yoyo: true, repeat: 1 }, "-=0.1")
              .to('.violent-worker', { x: 80, y: 20, duration: 0.5, ease: "power1.inOut" })
              .to('.containment-flash', { opacity: 1, duration: 0.1, yoyo: true, repeat: 1 }, "-=0.1")
              .to('.violent-worker', { x: -20, y: 70, duration: 0.4, ease: "power1.inOut" })
              .to('.containment-flash', { opacity: 1, duration: 0.1, yoyo: true, repeat: 1 }, "-=0.1")
              .to('.violent-worker', { x: 0, y: 0, duration: 0.5, ease: "elastic.out(1, 0.4)" });
        }

        // 4. Binding Handshake (Neural Bridge)
        const bindingContainer = document.querySelector('.gsap-binding-anim');
        if (bindingContainer) {
            const tl = gsap.timeline({ repeat: -1, repeatDelay: 1.5 });
            gsap.set(['.laser-up', '.laser-down'], { strokeDashoffset: 100, strokeDasharray: "100 100", opacity: 0 });
            gsap.set('.neural-cable', { opacity: 0 });
            gsap.set('.neural-pulse-wave', { strokeDashoffset: 400, opacity: 0 });
            
            tl.to('.node-a', { scale: 1.1, duration: 0.3, ease: "back.out(2)" })
              .to('.laser-up', { opacity: 1, strokeDashoffset: 0, duration: 0.5, ease: "power2.inOut" })
              .to('.neural-registry', { scale: 1.1, borderColor: "#ef4444", duration: 0.3, yoyo: true, repeat: 1 })
              .to('.laser-down', { opacity: 1, strokeDashoffset: 0, duration: 0.5, ease: "power2.inOut" })
              .to('.node-b', { scale: 1.1, duration: 0.3, ease: "back.out(2)" })
              .to(['.laser-up', '.laser-down'], { opacity: 0, duration: 0.3 })
              .to('.neural-cable', { opacity: 1, duration: 0.5 })
              .to('.neural-pulse-wave', { opacity: 1, duration: 0.1 })
              .to('.neural-pulse-wave', { strokeDashoffset: 0, duration: 1.5, ease: "power1.inOut" })
              .to('.neural-pulse-wave', { opacity: 0, duration: 0.3 })
              .to('.neural-cable', { opacity: 0, duration: 0.5 }, "+=0.5")
              .to(['.node-a', '.node-b'], { scale: 1, duration: 0.3 });
        }

        // 5. SDK Serialization (Assembly Line)
        const sdkContainer = document.querySelector('.gsap-sdk-anim');
        if (sdkContainer) {
            // Generate dots
            const field = document.querySelector('.binary-scatter-field');
            for(let i=0; i<30; i++) {
                let dot = document.createElement('div');
                dot.className = 'binary-dot';
                dot.style.position = 'absolute';
                dot.style.width = '6px';
                dot.style.height = '6px';
                dot.style.background = '#3b82f6';
                dot.style.borderRadius = '50%';
                dot.style.opacity = '0';
                field.appendChild(dot);
            }
            
            const tl = gsap.timeline({ repeat: -1, repeatDelay: 2 });
            gsap.set('.assembly-python', { opacity: 1, scale: 1 });
            gsap.set('.assembly-rust', { opacity: 0, scale: 0.5 });
            gsap.set('.binary-dot', { left: '20%', top: '50%', opacity: 0 });
            gsap.set('.assembly-laser', { opacity: 0, height: 0 });
            
            tl.to('.assembly-laser', { opacity: 1, height: 100, duration: 0.3, ease: "power4.out" })
              .to('.assembly-python', { x: -5, duration: 0.1, yoyo: true, repeat: 3 }, "<")
              .to('.assembly-python', { opacity: 0, scale: 0, duration: 0.3 })
              .to('.assembly-laser', { opacity: 0, duration: 0.2 }, "<")
              .to('.binary-dot', { 
                  opacity: 1, 
                  left: () => 30 + Math.random() * 40 + '%',
                  top: () => 20 + Math.random() * 60 + '%',
                  duration: 0.6,
                  stagger: 0.01,
                  ease: "power2.out"
              })
              .to('.binary-dot', { 
                  left: '80%', 
                  top: '50%', 
                  background: '#10b981',
                  duration: 0.8, 
                  stagger: 0.01,
                  ease: "power3.in"
              }, "+=0.5")
              .to('.assembly-rust', { opacity: 1, scale: 1, duration: 0.5, ease: "elastic.out(1, 0.4)" })
              .to('.binary-dot', { opacity: 0, duration: 0.1 }, "<")
              .to('.assembly-rust', { opacity: 0, scale: 0.5, duration: 0.5, delay: 1.5 });
        }
    }

    // Initialize all libraries
    function bootAll() {
        initParticles();
        initTyped();
        initAnime();
        initGSAP();
    }

    bootAll();

    if (typeof document$ !== "undefined") {
        document$.subscribe(function() {
            if (typeof gsap !== 'undefined') gsap.globalTimeline.clear();
            initTyped();
            initAnime();
            initGSAP();
        });
    }
});
