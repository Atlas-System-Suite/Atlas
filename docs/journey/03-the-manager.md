<div class="atlas-chapter-header">
  <span class="atlas-chapter-num">Chapter 3</span>
  <h1 class="atlas-chapter-title">Orchestration & Determinism</h1>
  <p class="atlas-chapter-desc">A Worker is an isolated unit of potential. A Manager is the orchestrator that collapses that potential into a deterministic reality.</p>
</div>

<div class="atlas-narrative" markdown="1">

A **Manager** is the conductor of the orchestra. It contains zero business logic. Its only job is to bind Workers together into a topology.

<div class="atlas-svg-container new-manager-anim" style="position: relative; width: 100%; height: 350px; background: rgba(15,23,42,0.03); border-radius: 20px; border: 1px solid rgba(15,23,42,0.1); overflow: hidden; margin: 3rem 0;">
  <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; perspective: 1200px;">
  <!-- Floating Blueprint -->
  <div class="hologram-blueprint" style="position: absolute; top: 10%; left: 50%; width: 120px; height: 160px; background: rgba(255, 255, 255, 0.9); border: 2px solid var(--atlas-navy); border-radius: 8px; transform: translateX(-50%) rotateX(60deg) rotateZ(-20deg); transform-style: preserve-3d; box-shadow: 0 20px 40px rgba(0,0,0,0.2); display: flex; flex-direction: column; padding: 10px; font-family: monospace; font-size: 0.6rem; font-weight: bold; color: var(--atlas-navy); z-index: 10;">
    <div style="font-size: 0.8rem; border-bottom: 1px solid var(--atlas-navy); margin-bottom: 5px; padding-bottom: 2px;">atlas.yaml</div>
    <div>- UI (0,0)</div>
    <div>- DB (1,0)</div>
    <div>- NET (0,1)</div>
  </div>

  <!-- Projection Beams -->
  <svg viewBox="0 0 1000 350" preserveAspectRatio="none" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 5;">
    <path class="holo-beam beam-1" d="M 500 120 L 275 235" fill="none" stroke="#3b82f6" stroke-width="3" stroke-dasharray="10 5" opacity="0"/>
    <path class="holo-beam beam-2" d="M 500 120 L 475 235" fill="none" stroke="#10b981" stroke-width="3" stroke-dasharray="10 5" opacity="0"/>
    <path class="holo-beam beam-3" d="M 500 120 L 675 235" fill="none" stroke="#ef4444" stroke-width="3" stroke-dasharray="10 5" opacity="0"/>
  </svg>

  <!-- Isometric Ground Grid -->
  <div class="hologram-grid" style="position: absolute; bottom: 5%; left: 50%; width: 400px; height: 400px; background-image: linear-gradient(rgba(15,23,42,0.1) 2px, transparent 2px), linear-gradient(90deg, rgba(15,23,42,0.1) 2px, transparent 2px); background-size: 50px 50px; transform: translateX(-50%) rotateX(70deg) rotateZ(45deg);"></div>

  <!-- Materialized Workers -->
  <div class="holo-worker hw-1" style="position: absolute; left: 25%; top: 60%; width: 50px; height: 50px; background: rgba(59, 130, 246, 0.8); border: 2px solid #3b82f6; transform: rotateX(60deg) rotateZ(45deg); opacity: 0; box-shadow: 0 0 20px #3b82f6; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white;">UI</div>
  
  <div class="holo-worker hw-2" style="position: absolute; left: 45%; top: 60%; width: 50px; height: 50px; background: rgba(16, 185, 129, 0.8); border: 2px solid #10b981; transform: rotateX(60deg) rotateZ(45deg); opacity: 0; box-shadow: 0 0 20px #10b981; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white;">DB</div>
  
  <div class="holo-worker hw-3" style="position: absolute; left: 65%; top: 60%; width: 50px; height: 50px; background: rgba(239, 68, 68, 0.8); border: 2px solid #ef4444; transform: rotateX(60deg) rotateZ(45deg); opacity: 0; box-shadow: 0 0 20px #ef4444; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white;">NET</div>
  </div>
</div>

<div class="admonition concept">
  <p class="admonition-title">Core Philosophy: Deterministic Composition</p>
  <p>Never optimize a feature at the expense of the software platform. The Manager does not <em>do</em> things; it <em>composes</em> things. If you find yourself writing `if/else` logic in a Manager to handle a business case, you have violated the architecture. The Runtime should become smaller. Workers should become smarter.</p>
</div>

### Scaffolding the Manager

Go back to your terminal (outside the `notes_ui` directory) and scaffold a manager boundary:

```bash
atlas new manager my_app
cd my_app
```

### The Composition Script (`main.py`)

Open `main.py` in the `my_app` directory. We will use the `ManagerBuilder` API to compose our application topologically.

```python
import os
from atlas_sdk import ManagerBuilder

def build():
    builder = ManagerBuilder("notes_application", version="1.0.0")

    # 1. Add the Atlas Standard Library Storage Worker
    builder.add_worker("atlas.core.storage")
    
    # 2. Add our custom UI Worker
    builder.add_worker("myapp.notes_ui")
    
    # 3. Set global topological configuration
    builder.configure("STORAGE_PATH", "./notes_db")
    
    # 4. Define the entry point of the graph
    builder.set_entry_point("myapp.notes_ui")

    # 5. Compile to declarative manifest
    manifest = builder.build()
    manifest.write("atlas.yaml")

if __name__ == "__main__":
    build()
```

### Dynamic Composition, Static Execution

Run the build script:

```bash
python main.py
```

This generates an `atlas.yaml` file in the directory. This generated YAML is the finalized, immutable "blueprint" for the application.

```yaml
manager:
  name: notes_application
  version: 1.0.0
workers:
  - id: atlas.core.storage
    entry_point: false
  - id: myapp.notes_ui
    entry_point: true
config:
  STORAGE_PATH: ./notes_db
```

<div class="admonition deep-dive">
  <p class="admonition-title">Why use a Python script to generate YAML?</p>
  <p>Why didn't we just write the `atlas.yaml` by hand? Because a Python build script allows you to make <strong>dynamic composition decisions</strong> before execution begins. You can read from `.env` files, pull secrets from a vault, or selectively include a `DebuggerWorker` only if `DEBUG=1`. However, once the `atlas.yaml` is generated, it becomes perfectly <strong>deterministic</strong>. AI systems should assist deterministic systems. Business rules must remain deterministic.</p>
</div>

### Booting the Reality

It's time. From inside the `my_app` directory, execute:

```bash
atlas run
```

### What happens at the edge of reality?

1. The Atlas Runtime boots up.
2. It parses the `atlas.yaml`.
3. It discovers `atlas.core.storage` (from the standard library) and `myapp.notes_ui` (from your workspace).
4. It computes a directed acyclic graph (DAG) to ensure all dependencies are met.
5. It loads both into memory boundaries.
6. It triggers the `on_start()` lifecycle hooks.
7. Because `myapp.notes_ui` is the `entry_point`, it begins handling execution.

🎉 **Congratulations.** You have just built a modular, decoupled, dynamically-composed Atlas application.

---

### The End of the Beginning

In the next (and final) section of this journey, we will completely pull apart the Atlas Runtime and look at the engine room. We will observe the exact sequence of events that occurs when Atlas boots, sandboxes Workers into Rooms, and negotiates Bindings.

<br>
<strong><a href="../the-engine-room/" style="color: var(--atlas-red); text-decoration: none; border-bottom: 1px solid var(--atlas-red); padding-bottom: 2px;">Next Chapter: The Engine Room (Deep Dive) &rarr;</a></strong>

</div>
