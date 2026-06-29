    // ----------------------------------------------------
    // 0. ATLAS CONSTELLATION (Home Page Hero)
    // A lightweight orbital animation showing Workers
    // binding to a central Runtime core.
    // ----------------------------------------------------
    function initAnimeCityscape() {
        if (typeof anime === 'undefined') return;
        const container = document.getElementById('anime-cityscape');
        if (!container) return;

        // Build SVG constellation
        const svgNS = "http://www.w3.org/2000/svg";
        const cx = 400, cy = 300; // center
        const svg = document.createElementNS(svgNS, "svg");
        svg.setAttribute("viewBox", "0 0 800 600");
        svg.setAttribute("preserveAspectRatio", "xMidYMid meet");
        svg.style.cssText = "width:100%;height:100%;position:absolute;top:0;left:0;";

        // Workers with Atlas-meaningful names, colors, and orbital radii
        const workers = [
            { label: "UI",      color: "#3b82f6", radius: 160, speed: 25000, startAngle: 0 },
            { label: "Storage", color: "#10b981", radius: 200, speed: 32000, startAngle: 60 },
            { label: "AI",      color: "#a855f7", radius: 140, speed: 20000, startAngle: 120 },
            { label: "Events",  color: "#f59e0b", radius: 220, speed: 38000, startAngle: 180 },
            { label: "DB",      color: "#ef4444", radius: 170, speed: 28000, startAngle: 240 },
            { label: "Logger",  color: "#06b6d4", radius: 190, speed: 35000, startAngle: 300 },
        ];

        // Orbital ring guides (subtle)
        workers.forEach(w => {
            const ring = document.createElementNS(svgNS, "circle");
            ring.setAttribute("cx", cx);
            ring.setAttribute("cy", cy);
            ring.setAttribute("r", w.radius);
            ring.setAttribute("fill", "none");
            ring.setAttribute("stroke", w.color);
            ring.setAttribute("stroke-opacity", "0.08");
            ring.setAttribute("stroke-width", "1");
            ring.setAttribute("stroke-dasharray", "4 8");
            svg.appendChild(ring);
        });

        // Binding lines (from center to each worker)
        const lines = workers.map(w => {
            const line = document.createElementNS(svgNS, "line");
            line.setAttribute("x1", cx);
            line.setAttribute("y1", cy);
            line.setAttribute("stroke", w.color);
            line.setAttribute("stroke-width", "1.5");
            line.setAttribute("stroke-opacity", "0.3");
            line.setAttribute("stroke-dasharray", "6 4");
            line.classList.add("atlas-binding-line");
            svg.appendChild(line);
            return line;
        });

        // Central Runtime core glow
        const coreGlow = document.createElementNS(svgNS, "circle");
        coreGlow.setAttribute("cx", cx);
        coreGlow.setAttribute("cy", cy);
        coreGlow.setAttribute("r", "45");
        coreGlow.setAttribute("fill", "url(#coreGrad)");
        coreGlow.setAttribute("filter", "url(#glow)");

        // SVG defs for gradient + glow
        const defs = document.createElementNS(svgNS, "defs");
        defs.innerHTML = `
            <radialGradient id="coreGrad">
                <stop offset="0%" stop-color="rgba(59,130,246,0.4)"/>
                <stop offset="100%" stop-color="rgba(59,130,246,0)"/>
            </radialGradient>
            <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur stdDeviation="8" result="blur"/>
                <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
        `;
        svg.appendChild(defs);
        svg.appendChild(coreGlow);

        // Core label
        const coreLabel = document.createElementNS(svgNS, "text");
        coreLabel.setAttribute("x", cx);
        coreLabel.setAttribute("y", cy);
        coreLabel.setAttribute("text-anchor", "middle");
        coreLabel.setAttribute("dominant-baseline", "middle");
        coreLabel.setAttribute("fill", "#38bdf8");
        coreLabel.setAttribute("font-family", "'JetBrains Mono', monospace");
        coreLabel.setAttribute("font-size", "13");
        coreLabel.setAttribute("font-weight", "700");
        coreLabel.setAttribute("opacity", "0.9");
        coreLabel.textContent = "Runtime";
        svg.appendChild(coreLabel);

        // Core inner ring
        const coreRing = document.createElementNS(svgNS, "circle");
        coreRing.setAttribute("cx", cx);
        coreRing.setAttribute("cy", cy);
        coreRing.setAttribute("r", "30");
        coreRing.setAttribute("fill", "none");
        coreRing.setAttribute("stroke", "#3b82f6");
        coreRing.setAttribute("stroke-width", "1.5");
        coreRing.setAttribute("stroke-opacity", "0.5");
        coreRing.classList.add("atlas-core-ring");
        svg.appendChild(coreRing);

        // Worker nodes (groups with circle + text)
        const nodeGroups = workers.map((w, i) => {
            const g = document.createElementNS(svgNS, "g");
            g.classList.add("atlas-worker-node");

            const dot = document.createElementNS(svgNS, "circle");
            dot.setAttribute("r", "18");
            dot.setAttribute("fill", w.color);
            dot.setAttribute("fill-opacity", "0.15");
            dot.setAttribute("stroke", w.color);
            dot.setAttribute("stroke-width", "2");

            const dotInner = document.createElementNS(svgNS, "circle");
            dotInner.setAttribute("r", "5");
            dotInner.setAttribute("fill", w.color);

            const text = document.createElementNS(svgNS, "text");
            text.setAttribute("y", "32");
            text.setAttribute("text-anchor", "middle");
            text.setAttribute("fill", w.color);
            text.setAttribute("font-family", "'JetBrains Mono', monospace");
            text.setAttribute("font-size", "10");
            text.setAttribute("font-weight", "600");
            text.setAttribute("opacity", "0.8");
            text.textContent = w.label;

            g.appendChild(dot);
            g.appendChild(dotInner);
            g.appendChild(text);
            svg.appendChild(g);
            return g;
        });

        container.appendChild(svg);

        // Animate orbits with anime.js
        workers.forEach((w, i) => {
            const angle = { value: w.startAngle };

            anime({
                targets: angle,
                value: w.startAngle + 360,
                duration: w.speed,
                loop: true,
                easing: 'linear',
                update: () => {
                    const rad = (angle.value * Math.PI) / 180;
                    const x = cx + Math.cos(rad) * w.radius;
                    const y = cy + Math.sin(rad) * w.radius * 0.45; // elliptical orbit
                    nodeGroups[i].setAttribute("transform", `translate(${x}, ${y})`);
                    lines[i].setAttribute("x2", x);
                    lines[i].setAttribute("y2", y);
                }
            });
        });

        // Pulse the binding lines
        anime({
            targets: '.atlas-binding-line',
            strokeOpacity: [0.1, 0.5, 0.1],
            strokeDashoffset: [0, 20],
            duration: 3000,
            delay: anime.stagger(400),
            loop: true,
            easing: 'easeInOutSine'
        });

        // Pulse the core ring
        anime({
            targets: '.atlas-core-ring',
            r: [30, 35, 30],
            strokeOpacity: [0.3, 0.8, 0.3],
            duration: 4000,
            loop: true,
            easing: 'easeInOutSine'
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

        // 1. Worker Lifecycle (Vertical Energy Tower)
        const lfContainer = document.querySelector('.new-lifecycle-container');
        if (lfContainer) {
            const tl = gsap.timeline({ repeat: -1, repeatDelay: 2 });
            
            // Initial state — all rings dim, bar empty, pulse hidden
            gsap.set('.state-ring', { opacity: 0.4 });
            gsap.set('.energy-bar', { height: 0 });
            gsap.set('.energy-pulse', { opacity: 0, top: 20 });
            
            // Pulse appears at BOOT
            tl.to('.energy-pulse', { opacity: 1, duration: 0.3 })
              // BOOT lights up
              .to('.ring-boot', { opacity: 1, borderColor: 'rgba(239, 68, 68, 0.8)', boxShadow: '0 0 25px rgba(239,68,68,0.5)', duration: 0.4 }, '<')
              .to('.energy-bar', { height: '25%', duration: 0.5 }, '<')
              
              // Pulse travels to RESOLVE
              .to('.energy-pulse', { top: 95, boxShadow: '0 0 20px #fff, 0 0 40px #3b82f6', duration: 0.6, ease: 'power2.inOut' })
              .to('.ring-resolve', { opacity: 1, borderColor: 'rgba(59, 130, 246, 0.8)', boxShadow: '0 0 25px rgba(59,130,246,0.5)', duration: 0.4 }, '-=0.3')
              .to('.energy-bar', { height: '50%', duration: 0.5 }, '-=0.4')
              
              // Pulse travels to READY
              .to('.energy-pulse', { top: 170, boxShadow: '0 0 20px #fff, 0 0 40px #10b981', duration: 0.6, ease: 'power2.inOut' })
              .to('.ring-ready', { opacity: 1, borderColor: 'rgba(16, 185, 129, 0.8)', boxShadow: '0 0 25px rgba(16,185,129,0.5)', duration: 0.4 }, '-=0.3')
              .to('.energy-bar', { height: '75%', duration: 0.5 }, '-=0.4')
              
              // Pulse travels to TERM
              .to('.energy-pulse', { top: 245, boxShadow: '0 0 20px #fff, 0 0 40px #ef4444', duration: 0.6, ease: 'power2.inOut' })
              .to('.ring-term', { opacity: 1, borderColor: 'rgba(239, 68, 68, 0.8)', boxShadow: '0 0 25px rgba(239,68,68,0.5)', duration: 0.4 }, '-=0.3')
              .to('.energy-bar', { height: '100%', duration: 0.5 }, '-=0.4')
              
              // Everything fades out
              .to('.energy-pulse', { opacity: 0, duration: 0.3 }, '+=1')
              .to('.energy-bar', { opacity: 0, duration: 0.5 }, '<')
              .to('.state-ring', { opacity: 0.4, borderColor: 'rgba(100,100,100,0.3)', boxShadow: 'none', duration: 0.5 }, '<')
              .set('.energy-bar', { height: 0, opacity: 1 });
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

        // Phase 2: Core Concepts - Radar Sweep
        const registryAnim = document.querySelector('.new-registry-anim');
        if (registryAnim) {
            const tl = gsap.timeline({ repeat: -1 });
            gsap.set('.radar-beam', { rotation: 0 });
            gsap.set('.radar-blip', { scale: 0, opacity: 0 });
            gsap.set('.blip-line', { strokeDashoffset: 50, strokeDasharray: "50 50", opacity: 0 });
            
            tl.to('.radar-beam', { rotation: 360, duration: 4, ease: "none" })
              // At specific angles, pop the blips
              .to('.blip-1', { opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)" }, "-=3.2")
              .to('.line-1', { opacity: 1, strokeDashoffset: 0, duration: 0.3 }, "-=3.1")
              
              .to('.blip-2', { opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)" }, "-=2.4")
              .to('.line-2', { opacity: 1, strokeDashoffset: 0, duration: 0.3 }, "-=2.3")
              
              .to('.blip-3', { opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)" }, "-=1.0")
              .to('.line-3', { opacity: 1, strokeDashoffset: 0, duration: 0.3 }, "-=0.9")
              
              .to('.radar-blip, .blip-line', { opacity: 0, duration: 0.5 }, "-=0.2");
        }

        // Phase 2: Core Concepts - Quantum Wormhole
        const sessionAnim = document.querySelector('.new-session-anim');
        if (sessionAnim) {
            const tl = gsap.timeline({ repeat: -1, repeatDelay: 1 });
            gsap.set('.core-laser', { scaleY: 0, transformOrigin: 'top center' });
            gsap.set('.wormhole-tunnel', { scaleX: 0, opacity: 0 });
            gsap.set('.packet-1', { left: '15%', scale: 0, opacity: 0 });
            
            // Hover cubes
            gsap.to('.req-cube', { y: '+=10', duration: 2, repeat: -1, yoyo: true, ease: "sine.inOut" });
            gsap.to('.prov-cube', { y: '-=10', duration: 2, repeat: -1, yoyo: true, ease: "sine.inOut", delay: 0.5 });
            
            tl.to('.core-laser', { opacity: 1, scaleY: 1, duration: 0.4, ease: "power4.out" })
              .to('.wormhole-tunnel', { scaleX: 1, opacity: 1, duration: 0.6, ease: "elastic.out(1, 0.5)" })
              .to('.core-laser', { opacity: 0, duration: 0.2 }, "-=0.4")
              
              .to('.packet-1', { opacity: 1, scale: 1, duration: 0.2 })
              .to('.packet-1', { left: '30%', duration: 0.3, ease: "power2.in" })
              // Sucked in
              .to('.packet-1', { scale: 0, opacity: 0, left: '50%', duration: 0.2 })
              // Shot out
              .to('.packet-1', { left: '70%', duration: 0 })
              .to('.packet-1', { scale: 1, opacity: 1, duration: 0.2 })
              .to('.packet-1', { left: '85%', duration: 0.3, ease: "power2.out" })
              .to('.packet-1', { opacity: 0, scale: 0, duration: 0.2 })
              
              .to('.wormhole-tunnel', { scaleX: 0, opacity: 0, duration: 0.4 }, "+=0.5");
        }

        // Phase 2: Core Concepts - Filtration Grid
        const modelAnim = document.querySelector('.new-model-anim');
        if (modelAnim) {
            const tl = gsap.timeline({ repeat: -1, repeatDelay: 1 });
            gsap.set('.bad-blob, .good-blob', { left: '10%', scale: 1, opacity: 1 });
            
            // Generate explosion dots
            const vaporField = document.querySelector('.vaporize-field');
            if (vaporField && vaporField.children.length === 0) {
                for (let i = 0; i < 15; i++) {
                    const dot = document.createElement('div');
                    dot.className = 'vapor-dot';
                    dot.style.position = 'absolute';
                    dot.style.width = '4px'; dot.style.height = '4px';
                    dot.style.background = '#ef4444';
                    dot.style.borderRadius = '50%';
                    dot.style.left = '50%'; dot.style.top = '50%';
                    dot.style.opacity = '0';
                    vaporField.appendChild(dot);
                }
            }
            
            tl.to('.bad-blob', { left: '55%', duration: 1, ease: "power2.in" })
              .to('.bad-blob', { scale: 0, opacity: 0, duration: 0.1 })
              .to('.vapor-dot', { 
                  opacity: 1, 
                  x: () => (Math.random() - 0.5) * 100, 
                  y: () => (Math.random() - 0.5) * 100, 
                  duration: 0.4, 
                  ease: "power3.out" 
              }, "-=0.1")
              .to('.vapor-dot', { opacity: 0, duration: 0.2 }, "+=0.2")
              
              .to('.good-blob', { left: '80%', duration: 1.5, ease: "power1.inOut" }, "-=0.5")
              .to('.good-blob', { scale: 0, opacity: 0, duration: 0.2 });
        }

        // Phase 2: The Manager - Holographic Projector
        const managerAnim = document.querySelector('.new-manager-anim');
        if (managerAnim) {
            const tl = gsap.timeline({ repeat: -1, repeatDelay: 2 });
            gsap.set('.holo-beam', { strokeDashoffset: 20, strokeDasharray: "20 20", opacity: 0 });
            
            // Fix: GSAP overwrites inline transforms, so we must set the 3D rotation explicitly here
            gsap.set('.holo-worker', { rotationX: 60, rotationZ: 45, y: -50, scale: 0.5, opacity: 0 });
            gsap.set('.hologram-blueprint', { xPercent: -50, rotationX: 60, rotationZ: -20 });
            
            gsap.to('.hologram-blueprint', { y: '+=10', duration: 2, repeat: -1, yoyo: true, ease: "sine.inOut" });
            
            tl.to('.holo-beam', { opacity: 1, duration: 0.3 })
              .to('.holo-beam', { strokeDashoffset: 0, duration: 1, ease: "none" }, "<")
              // Animate y and scale, preserving rotation
              .to('.holo-worker', { rotationX: 60, rotationZ: 45, y: 0, scale: 1, opacity: 1, duration: 0.8, stagger: 0.2, ease: "elastic.out(1, 0.5)" }, "-=0.8")
              .to('.holo-beam', { opacity: 0, duration: 0.3 })
              .to('.holo-worker', { y: 20, opacity: 0, duration: 0.5, stagger: 0.1 }, "+=2");
        }
    }

    // Initialize all libraries
    function bootAll() {
        initAnimeCityscape();
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

    // =========================================================================
    // MERMAID GRAPH ANIMATOR
    // MkDocs Material handles rendering natively. We just observe the DOM
    // for rendered SVGs and apply GSAP animations to them.
    // =========================================================================
    
    function animateMermaidGraph(svg) {
        if (svg.dataset.animated === "true") return;
        svg.dataset.animated = "true";
        if (typeof gsap === 'undefined') return;

        const edges = svg.querySelectorAll('.edgePath path');
        edges.forEach(edge => {
            const length = edge.getTotalLength ? edge.getTotalLength() : 1000;
            edge.style.strokeDasharray = length;
            edge.style.strokeDashoffset = length;
        });

        const nodes = svg.querySelectorAll('.node');
        gsap.set(nodes, { opacity: 0, scale: 0.8, transformOrigin: "center center" });
        
        const labels = svg.querySelectorAll('.edgeLabel');
        gsap.set(labels, { opacity: 0, y: 10 });

        ScrollTrigger.create({
            trigger: svg,
            start: "top 85%",
            animation: gsap.timeline()
                .to(nodes, { opacity: 1, scale: 1, duration: 0.5, stagger: 0.1, ease: "back.out(1.5)" })
                .to(edges, { strokeDashoffset: 0, duration: 0.8, ease: "power2.inOut", stagger: 0.1 }, "-=0.2")
                .to(labels, { opacity: 1, y: 0, duration: 0.4, stagger: 0.1 }, "-=0.4")
        });
    }

    // Watch for Material's mermaid SVGs to appear in the DOM
    const mermaidObserver = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            mutation.addedNodes.forEach((node) => {
                if (node.nodeType !== 1) return;
                // Material renders mermaid inside shadow DOM or directly
                const svgs = node.querySelectorAll ? node.querySelectorAll('svg') : [];
                svgs.forEach(svg => {
                    if (svg.id && svg.id.startsWith('mermaid')) animateMermaidGraph(svg);
                });
                if (node.tagName === 'SVG' && node.id && node.id.startsWith('mermaid')) {
                    animateMermaidGraph(node);
                }
            });
        });
    });
    mermaidObserver.observe(document.body, { childList: true, subtree: true });

    // Also catch any already-rendered mermaid graphs
    setTimeout(() => {
        document.querySelectorAll('.mermaid svg, pre.mermaid svg').forEach(animateMermaidGraph);
    }, 1000);

});
