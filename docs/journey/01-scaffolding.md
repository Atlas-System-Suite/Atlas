# The Lifecycle of a Worker

Before writing any code, we must understand the fundamental paradigm shift of Atlas: You no longer own the execution lifecycle of your application. The Runtime does.

In traditional software, your `main()` function explicitly instantiates objects, sets up servers, and wires dependencies together. If Service A needs to talk to Service B, Service A imports it directly. This creates a brittle, tightly-coupled monolith.

Atlas takes a radically different approach. 

<div class="admonition concept">
  <p class="admonition-title">The First Invariant: Atlas Coordinates. Workers Own.</p>
  <p>In Atlas, you write small, isolated units of business logic called <strong>Workers</strong>. A Worker never instantiates another Worker. A Worker never imports another Worker. Instead, Workers declare <em>Capabilities</em> they can provide, and <em>Dependencies</em> they require. The Atlas Runtime reads these declarations, resolves the dependency graph, and handles all orchestration.</p>
</div>

---

## The Worker State Machine

Because Atlas owns the lifecycle, every Worker is strictly bound to a deterministic State Machine. The Runtime transitions the Worker through these states. You cannot force a transition; you can only hook into it.

<div class="atlas-svg-container new-lifecycle-container" style="position: relative; width: 100%; height: 350px; background: rgba(15,23,42,0.03); border-radius: 20px; border: 1px solid rgba(15,23,42,0.1); overflow: hidden; margin: 3rem 0; display: flex; align-items: center; justify-content: center;">
  <!-- Vertical Energy Tower -->
  <div class="lifecycle-tower" style="position: relative; width: 200px; height: 280px; display: flex; flex-direction: column; align-items: center; justify-content: space-between; padding: 20px 0;">
    
    <!-- State Ring: BOOT (top) -->
    <div class="state-ring ring-boot" style="position: relative; width: 120px; height: 50px; border: 2px solid rgba(239, 68, 68, 0.3); border-radius: 50%; display: flex; align-items: center; justify-content: center; background: rgba(15,23,42,0.6); z-index: 2;">
      <span style="color: #ef4444; font-weight: bold; font-family: monospace; font-size: 0.85rem;">BOOT</span>
    </div>

    <!-- State Ring: RESOLVE -->
    <div class="state-ring ring-resolve" style="position: relative; width: 120px; height: 50px; border: 2px solid rgba(59, 130, 246, 0.3); border-radius: 50%; display: flex; align-items: center; justify-content: center; background: rgba(15,23,42,0.6); z-index: 2;">
      <span style="color: #3b82f6; font-weight: bold; font-family: monospace; font-size: 0.85rem;">RESOLVE</span>
    </div>

    <!-- State Ring: READY -->
    <div class="state-ring ring-ready" style="position: relative; width: 120px; height: 50px; border: 2px solid rgba(16, 185, 129, 0.3); border-radius: 50%; display: flex; align-items: center; justify-content: center; background: rgba(15,23,42,0.6); z-index: 2;">
      <span style="color: #10b981; font-weight: bold; font-family: monospace; font-size: 0.85rem;">READY</span>
    </div>

    <!-- State Ring: TERM (bottom) -->
    <div class="state-ring ring-term" style="position: relative; width: 120px; height: 50px; border: 2px solid rgba(239, 68, 68, 0.3); border-radius: 50%; display: flex; align-items: center; justify-content: center; background: rgba(15,23,42,0.6); z-index: 2;">
      <span style="color: #ef4444; font-weight: bold; font-family: monospace; font-size: 0.85rem;">TERM</span>
    </div>

    <!-- Central Energy Bar (vertical, behind rings) -->
    <div class="energy-bar" style="position: absolute; left: 50%; top: 20px; width: 4px; height: 0; background: linear-gradient(to bottom, #ef4444, #3b82f6, #10b981, #ef4444); transform: translateX(-50%); z-index: 1; box-shadow: 0 0 15px rgba(239, 68, 68, 0.6); border-radius: 2px;"></div>

    <!-- Pulse dot that travels down -->
    <div class="energy-pulse" style="position: absolute; left: 50%; top: 20px; width: 12px; height: 12px; background: #fff; border-radius: 50%; transform: translateX(-50%); z-index: 3; opacity: 0; box-shadow: 0 0 20px #fff, 0 0 40px #ef4444;"></div>
  </div>
</div>

1. **BOOT**: The OS process launches. The SDK parses the file to locate capabilities but executes zero business logic.
2. **RESOLVE**: The Worker connects to the Room Registry. It pauses completely until the Runtime guarantees that all required dependencies exist in the network topology.
3. **READY**: The Runtime fires the `on_init` hook. The Worker is now allowed to allocate state, open database connections, and process invocations.
4. **TERM**: The Runtime sends a shutdown signal. The Worker fires `on_destroy` and elegantly closes its memory.

---

## Scaffolding the Declarative Shell

Every great application in Atlas starts with defining a boundary. Open your terminal and run the interactive scaffolding wizard:

```bash
atlas new
```

Follow the prompts to create our first Worker:
1. **Type**: `worker`
2. **Name**: `notes_ui`
3. **Namespace**: `myapp`
4. **Version**: `1.0.0`
5. **Language**: `python`

Atlas will generate a directory called `notes_ui`. Change into it and open `worker.py`.

### Code as a Contract

Notice the structure of the generated Python file. It is a boilerplate worker containing a template `hello` capability:

```python
from atlas_sdk import WorkerBase, capability, on_invocation

class NotesUiWorker(WorkerBase):
    _worker_id = "myapp.notes_ui"
    _worker_name = "NotesUiWorker"
    _worker_version = "1.0.0"
    _worker_roles = ["worker"]

    def on_init(self):
        """Called after construction. Set up your state here."""
        pass

    def on_start(self):
        """Called when the runtime starts this worker."""
        pass

    def on_stop(self):
        """Called on shutdown. Clean up resources here."""
        pass

    @capability("myapp.notes_ui.hello", version="1.0.0")
    @on_invocation("hello")
    def hello(self, name: str = "World") -> str:
        """A simple hello capability. Replace me with real logic!"""
        return f"Hello, {name}! From NotesUiWorker."
```

#### Detailed Breakdown of Boilerplate Code:
* **`WorkerBase`**: The base class for all Atlas Python workers. Inheriting from it configures metaclasses that collect decorator annotations at import time.
* **Metadata Fields (`_worker_id`, `_worker_name`, etc.)**:
  - `_worker_id`: The global unique ID for this worker instance (e.g. `"myapp.notes_ui"`).
  - `_worker_roles`: Tags that describe this worker's responsibility (e.g., `["worker"]` or `["app"]`).
* **Lifecycle Hooks**:
  - `on_init()`: Invoked by the runtime immediately after instantiation. This is where you allocate in-memory state.
  - `on_start()`: Invoked when the runtime finishes resolving all bindings and boots the worker loop.
  - `on_stop()`: Invoked during a graceful shutdown. This is where you close any open connections or files.
* **Capability Routing**:
  - `@capability("myapp.notes_ui.hello", version="1.0.0")`: Declares that this worker implements the specific capability contract `"myapp.notes_ui.hello"` at version `1.0.0`.
  - `@on_invocation("hello")`: Tells the SDK to route any incoming requests targeting the `"hello"` action to this Python method.

---

### Implementing our Business Logic

Let's modify this boilerplate to implement our Note-taking application.
First, we want the worker to keep track of a list of notes in memory. We initialize this list in `on_init()`.
Second, we replace the `hello` capability with an `add` capability that appends a note to the list.

Open `worker.py` and update it as follows:

```python
from atlas_sdk import WorkerBase, capability, on_invocation

class NotesUiWorker(WorkerBase):
    _worker_id = "myapp.notes_ui"
    _worker_name = "NotesUiWorker"
    _worker_version = "1.0.0"
    _worker_roles = ["worker"]
    
    def on_init(self):
        """Called by the Runtime after graph resolution."""
        self.notes = []

    @capability("myapp.notes.add", version="1.0.0")
    @on_invocation("add")
    def add(self, note_text: str) -> str:
        self.notes.append(note_text)
        return f"Note added! Total notes: {len(self.notes)}"
```

#### How this logic functions:
* **`self.notes = []`**: Initializes a simple in-memory list on this specific worker instance.
* **`add(self, note_text: str)`**: This method will be invoked when a caller requests the `myapp.notes.add` capability. It accepts a `note_text` string, appends it to our state, and returns a confirmation string.

Why is it written this way?

First, notice `on_init()`. You do not write an `__init__()` constructor. **Atlas owns the lifecycle.** The Runtime must guarantee that all network topologies, registries, and logging mechanisms are fully primed *before* your worker allocates state. The `on_init` hook is invoked by the Runtime exactly when it hits the `READY` state shown in the diagram above.

Second, look at the `@capability` decorator. This is not a web endpoint. This is a semantic contract. By declaring `"myapp.notes.add"`, you are telling the Global Registry: *"I guarantee I can fulfill this specific business capability."*

### How does Routing Actually Work?

When you decorate a method with `@capability`, the Atlas SDK inspects the Abstract Syntax Tree (AST) at compile time. During boot, the Runtime's Invocation Engine maps the string `"myapp.notes.add"` to the memory address of this specific worker instance. 

If a Rust worker on a completely different physical machine requests `"myapp.notes.add"`, the Invocation Engine intercepts the call, translates the binary payload, and routes it to this exact Python function, completely invisibly to you.

---

## The Source of Truth: `atlas.yaml`

Alongside your Python code, Atlas generated a declarative manifest. Let's update it to export `myapp.notes.add` rather than the default hello capability:

```yaml
kind: worker
id: myapp.notes_ui
name: NotesUiWorker
version: 1.0.0
description: An Atlas Project
language: python
roles: [worker]

execution:
  policy: singleton

communication:
  transports: [memory]
  formats: [python]
  default_format: python

imports: []

exports:
  - capability: myapp.notes.add
    version: 1.0.0

translations: []
```

#### Detailed Breakdown of the YAML Manifest:
* **`kind: worker`**: Identifies this file as a Worker specification.
* **`id: myapp.notes_ui`**: Matches the `_worker_id` string in our Python file, allowing the Runtime to pair this manifest with the Python class.
* **`execution`**:
  - `policy: singleton`: Tells the Runtime that only one instance of this worker should be spawned per Room.
* **`communication`**:
  - `transports: [memory]`: The underlying communication protocol. Memory transport is fast and keeps the worker in-process.
  - `formats: [python]`: The data serialization format used (in this case, native Python structures).
* **`exports`**: Lists the capabilities this worker makes available to other workers. This must match the `@capability` decorators in your code.

Why do we need a YAML file if the Python code already has the `@capability` decorator?

Because Atlas is **language agnostic**. Although the core reference Runtime in this repository is implemented in Python (to be ported to Rust/native binaries in the future), the design separates the runtime's orchestration from the language-specific workers. It cannot read your Python decorators directly. The `atlas.yaml` manifest serves as a universal, language-independent specification that the Runtime reads *before* loading any worker code. It allows the Runtime to understand the shape of your application instantly, without needing to boot up the worker's language runtime just to map the capability network.

---

## Verifying the Isolation

Because Workers are completely isolated from their infrastructure, we can test them without spinning up the entire operating system or compiling the whole project. 

Atlas provides a `MockRuntime` for this exact purpose. Open `test_notes_ui.py` and update it to test our new `add` capability:

```python
from atlas_sdk.testing import MockRuntime
from worker import NotesUiWorker

def test_add_note():
    # 1. Boot a mock runtime in memory (instant)
    runtime = MockRuntime()

    # 2. Register our isolated worker
    runtime.register(NotesUiWorker, "myapp.notes_ui")

    # 3. Simulate a network capability request (using the registered Worker ID)
    result = runtime.invoke("myapp.notes_ui", "add", {"note_text": "Buy milk"})

    assert "Total notes: 1" in result
```

#### Detailed Breakdown of the Test Code:
* **`MockRuntime`**: A lightweight, pure-Python class that simulates the Atlas invocation loop in-memory, without opening real network sockets or spin-locking threads.
* **`runtime.register(NotesUiWorker, "myapp.notes_ui")`**: Instantiates and binds our worker to a mock address, just like the real Runtime bootloader would.
* **`runtime.invoke("myapp.notes_ui", "add", ...)`**: Simulates an invocation. The first parameter is the **Worker ID** (`"myapp.notes_ui"`), the second is the action name (`"add"`), and the third is the payload dictionary matching the method signature.

Run the tests:

```bash
atlas test
```

By aggressively decoupling the *logic* from the *transport*, your worker becomes infinitely scalable and perfectly testable. You never have to mock a database connection just to test a string parsing function.

---

### What's Next?

Right now, our notes are just stored in a Python list `self.notes = []`. If the worker restarts, our notes are gone! 

In traditional architecture, you would import an SQL library right here and tightly couple your UI worker to a database. But in Atlas, **Workers own business state, but the Runtime owns persistence.**

In the next step, we will explore how to consume external Capabilities without breaking our isolation.

<br>
<strong><a href="../02-state-and-models/" style="color: var(--atlas-red); text-decoration: none; border-bottom: 1px solid var(--atlas-red); padding-bottom: 2px;">Next Chapter: State & Standard Models &rarr;</a></strong>
