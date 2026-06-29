# Core Concepts

- **Worker:** The ONLY executable primitive in Atlas. Owns business logic and state.
- **Room:** An execution context representing a collaboration between Workers. Rooms are stewarded by Atlas.

<div class="atlas-svg-container new-registry-anim" style="position: relative; width: 100%; height: 350px; background: rgba(15,23,42,0.03); border-radius: 20px; border: 1px solid rgba(15,23,42,0.1); overflow: hidden; margin: 3rem 0; display: flex; align-items: center; justify-content: center;">
  <!-- Radar Grid Background -->
  <div style="position: absolute; left: 0; top: 0; width: 100%; height: 100%; background: radial-gradient(circle at center, rgba(16, 185, 129, 0.1) 0%, transparent 60%);"></div>
  <svg style="position: absolute; left: 0; top: 0; width: 100%; height: 100%;">
    <circle cx="50%" cy="50%" r="50" fill="none" stroke="rgba(16, 185, 129, 0.2)" stroke-width="1"/>
    <circle cx="50%" cy="50%" r="100" fill="none" stroke="rgba(16, 185, 129, 0.2)" stroke-width="1"/>
    <circle cx="50%" cy="50%" r="150" fill="none" stroke="rgba(16, 185, 129, 0.2)" stroke-width="1"/>
    <line x1="50%" y1="0" x2="50%" y2="100%" stroke="rgba(16, 185, 129, 0.2)" stroke-width="1"/>
    <line x1="0" y1="50%" x2="100%" y2="50%" stroke="rgba(16, 185, 129, 0.2)" stroke-width="1"/>
  </svg>
  
  <!-- Sweeping Radar Beam -->
  <div class="radar-beam" style="position: absolute; left: 50%; top: 50%; margin-left: -150px; margin-top: -150px; width: 300px; height: 300px; background: conic-gradient(from 0deg, rgba(16, 185, 129, 0.4) 0deg, transparent 40deg); border-radius: 50%; transform-origin: center; opacity: 0.8; mix-blend-mode: screen;"></div>
  
  <!-- The Global Registry Core -->
  <div style="position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); width: 40px; height: 40px; background: #10b981; border-radius: 50%; box-shadow: 0 0 20px #10b981; display: flex; align-items: center; justify-content: center; z-index: 5;">
    <span style="color: white; font-weight: bold; font-family: monospace; font-size: 0.7rem;">REG</span>
  </div>
  
  <!-- Hidden Worker Blips -->
  <div class="radar-blip blip-1" style="position: absolute; left: 30%; top: 30%; width: 12px; height: 12px; background: #3b82f6; border-radius: 50%; opacity: 0; box-shadow: 0 0 10px #3b82f6;"></div>
  <div class="radar-blip blip-2" style="position: absolute; left: 70%; top: 20%; width: 12px; height: 12px; background: #3b82f6; border-radius: 50%; opacity: 0; box-shadow: 0 0 10px #3b82f6;"></div>
  <div class="radar-blip blip-3" style="position: absolute; left: 60%; top: 80%; width: 12px; height: 12px; background: #3b82f6; border-radius: 50%; opacity: 0; box-shadow: 0 0 10px #3b82f6;"></div>
  
  <!-- Connection Lines -->
  <svg style="position: absolute; left: 0; top: 0; width: 100%; height: 100%; pointer-events: none;">
    <line class="blip-line line-1" x1="50%" y1="50%" x2="30%" y2="30%" stroke="#10b981" stroke-width="2" stroke-dasharray="5,5" opacity="0"/>
    <line class="blip-line line-2" x1="50%" y1="50%" x2="70%" y2="20%" stroke="#10b981" stroke-width="2" stroke-dasharray="5,5" opacity="0"/>
    <line class="blip-line line-3" x1="50%" y1="50%" x2="60%" y2="80%" stroke="#10b981" stroke-width="2" stroke-dasharray="5,5" opacity="0"/>
  </svg>
</div>

- **Registry:** Stores runtime facts. Split into the **Global Registry** (macro-state) and **Room Registry** (execution cache). When a Worker boots up, Atlas automatically discovers it and adds it to the Registry.

- **Session:** The communication primitive connecting Workers. Exists inside Rooms.
- **Binding:** A negotiated connection established by Atlas between a requesting Worker and a providing Worker.
- **Invocation:** The actual execution request sent over a Session and processed by a Worker.

<div class="atlas-svg-container new-session-anim" style="position: relative; width: 100%; height: 350px; background: rgba(15,23,42,0.03); border-radius: 20px; border: 1px solid rgba(15,23,42,0.1); overflow: hidden; margin: 3rem 0; display: flex; align-items: center; justify-content: center; perspective: 1000px;">
  
  <!-- Core Laser Emitter -->
  <div class="wormhole-core" style="position: absolute; top: -20px; left: 50%; transform: translateX(-50%); width: 60px; height: 30px; background: var(--atlas-red); border-bottom-left-radius: 30px; border-bottom-right-radius: 30px; box-shadow: 0 10px 30px var(--atlas-red);">
    <span style="position: absolute; top: 5px; left: 10px; color: white; font-weight: bold; font-family: monospace; font-size: 0.7rem;">CORE</span>
  </div>
  
  <div class="core-laser" style="position: absolute; top: 10px; left: 50%; width: 2px; height: 160px; background: var(--atlas-red); transform: translateX(-50%); opacity: 0; box-shadow: 0 0 10px var(--atlas-red);"></div>

  <!-- 3D Worker Cubes -->
  <div class="cube-worker req-cube" style="position: absolute; left: 15%; top: 50%; width: 80px; height: 80px; background: rgba(59, 130, 246, 0.9); border: 2px solid white; transform: translateY(-50%) rotateY(30deg) rotateX(15deg); display: flex; align-items: center; justify-content: center; font-weight: bold; color: white; box-shadow: -10px 10px 20px rgba(0,0,0,0.1);">UI</div>
  
  <div class="cube-worker prov-cube" style="position: absolute; right: 15%; top: 50%; width: 80px; height: 80px; background: rgba(16, 185, 129, 0.9); border: 2px solid white; transform: translateY(-50%) rotateY(-30deg) rotateX(15deg); display: flex; align-items: center; justify-content: center; font-weight: bold; color: white; box-shadow: 10px 10px 20px rgba(0,0,0,0.1);">Storage</div>
  
  <!-- The Quantum Wormhole -->
  <div class="wormhole-tunnel" style="position: absolute; left: 50%; top: 50%; width: 300px; height: 40px; transform: translate(-50%, -50%) scaleX(0); background: linear-gradient(90deg, transparent, rgba(59,130,246,0.3), rgba(239,68,68,0.5), rgba(16,185,129,0.3), transparent); border-radius: 50%; filter: blur(4px);"></div>
  
  <!-- Packets shooting through -->
  <div class="quantum-packet packet-1" style="position: absolute; left: 30%; top: 50%; width: 15px; height: 15px; background: white; border-radius: 50%; transform: translateY(-50%); opacity: 0; box-shadow: 0 0 15px white;"></div>
</div>

- **Communication:** Workers communicate by sending Headers. Atlas handles the Transport and Translation layers to guarantee language neutrality. Notice how data flows peer-to-peer between Workers after Atlas establishes the binding!

- **Model:** The declarative, tool-independent blueprint that a Worker implements.

<div class="atlas-svg-container new-model-anim" style="position: relative; width: 100%; height: 350px; background: rgba(15,23,42,0.03); border-radius: 20px; border: 1px solid rgba(15,23,42,0.1); overflow: hidden; margin: 3rem 0; display: flex; align-items: center; justify-content: center;">
  
  <!-- Protected Worker -->
  <div style="position: absolute; right: 10%; top: 50%; transform: translateY(-50%); width: 100px; height: 100px; background: white; border: 4px solid var(--atlas-navy); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-family: monospace; z-index: 5;">Worker</div>
  
  <!-- Laser Filtration Grid (Model Shield) -->
  <div class="filtration-grid" style="position: absolute; right: 35%; top: 10%; bottom: 10%; width: 20px; display: flex; flex-direction: column; justify-content: space-between; z-index: 4;">
    <div style="width: 100%; height: 2px; background: #3b82f6; box-shadow: 0 0 10px #3b82f6;"></div>
    <div style="width: 100%; height: 2px; background: #3b82f6; box-shadow: 0 0 10px #3b82f6;"></div>
    <div style="width: 100%; height: 2px; background: #3b82f6; box-shadow: 0 0 10px #3b82f6;"></div>
    <div style="width: 100%; height: 2px; background: #3b82f6; box-shadow: 0 0 10px #3b82f6;"></div>
    <div style="width: 100%; height: 2px; background: #3b82f6; box-shadow: 0 0 10px #3b82f6;"></div>
    <div style="width: 100%; height: 2px; background: #3b82f6; box-shadow: 0 0 10px #3b82f6;"></div>
    <div style="width: 100%; height: 2px; background: #3b82f6; box-shadow: 0 0 10px #3b82f6;"></div>
    <div style="position: absolute; left: 50%; top: 0; transform: translateX(-50%); width: 2px; height: 100%; background: #3b82f6; box-shadow: 0 0 10px #3b82f6;"></div>
  </div>
  <div style="position: absolute; right: 35%; top: 5px; font-family: monospace; font-size: 0.8rem; font-weight: bold; color: #3b82f6; transform: translateX(50%);">Model Grid</div>
  
  <!-- Incoming Data -->
  <div class="bad-blob" style="position: absolute; left: 10%; top: 30%; width: 40px; height: 40px; background: #ef4444; border-radius: 30% 70% 70% 30% / 30% 30% 70% 70%; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white;">{}</div>
  
  <div class="good-blob" style="position: absolute; left: 10%; top: 60%; width: 40px; height: 40px; background: #10b981; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white;">{}</div>
  
  <!-- Explosion Particles -->
  <div class="vaporize-field" style="position: absolute; left: 55%; top: 15%; width: 100px; height: 100px; pointer-events: none; z-index: 10;"></div>
</div>

- **Role:** A metadata tag (e.g., `database`, `manager`, `ai`) that describes a Worker to the Studio Suite.
