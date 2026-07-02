# State & Standard Models

A Worker without memory is just a function. But in Atlas, how a Worker remembers is just as important as what it remembers. We do not couple logic to infrastructure, and we do not couple data to language-specific runtimes.

<div class="atlas-narrative" markdown="1">

Right now, our `NotesUiWorker` stores data in a Python list. If the node crashes or the process restarts, the memory is wiped and the notes vanish. We need persistence.

In traditional software development, the easiest path to persistence is importing an SQL or MongoDB driver directly into your application code. You write a query, establish a TCP connection to the database, and save the data. 

**Atlas strictly forbids this.**

If your Worker imports an SQL driver, it is now tightly coupled to SQL. It is no longer an isolated, pure business-logic primitive. It requires a network connection to a database to even run its unit tests.

### The Capability Model

Instead of importing a database driver, we ask the **Global Registry** for a generic Storage Capability. 

By demanding `"atlas.core.storage@^1.0.0"`, our UI worker is making a declarative statement: *"I do not care if the underlying storage is Postgres, Redis, a local JSON file, or an S3 bucket. I just need something that can hold bytes."*

This is the power of the Atlas runtime. The Runtime will dynamically find a Worker that provides that capability, negotiate a secure Session tunnel between them, and allow them to pass messages.

But wait. If a Python UI Worker is talking to a Rust Storage Worker over a ZeroMQ tunnel, how do they understand each other's data structures? A Python dictionary is not a Rust struct.

---

## Enter: Standard Models

In Atlas, all inter-Worker communication must adhere to **Standard Models**. 
A Model is a declarative, language-agnostic data schema defined in your manifest. It acts as a universal translator. 

When a Worker emits data, the Atlas SDK intercepts the memory object, serializes it into the exact shape defined by the Model, and ships it over the wire. When the receiving Worker catches the payload, its SDK deserializes the payload back into a native language object (like a Go struct or a Python dictionary).

<div class="atlas-svg-container funnel-container" style="position: relative; width: 100%; height: 300px; display: flex; justify-content: center; align-items: center; margin: 3rem 0; background: rgba(15,23,42,0.03); border-radius: 20px; border: 1px solid rgba(15,23,42,0.1); overflow: hidden;">
  
  <div style="position: absolute; left: 10%; top: 20px; font-family: monospace; font-weight: bold; color: var(--atlas-red);">Raw Memory (Chaos)</div>
  <div style="position: absolute; right: 10%; top: 20px; font-family: monospace; font-weight: bold; color: #10b981;">Standard Model (Order)</div>

  <!-- The Funnel Core -->
  <div class="funnel-core" style="position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); width: 100px; height: 200px; background: linear-gradient(90deg, rgba(239, 68, 68, 0.1), rgba(16, 185, 129, 0.1)); border-left: 2px dashed #ef4444; border-right: 2px dashed #10b981; border-radius: 50px;"></div>
  
  <!-- Chaotic Input Nodes -->
  <div class="chaotic-node" style="position: absolute; left: 10%; top: 40%; width: 50px; height: 30px; background: rgba(239, 68, 68, 0.1); border: 2px solid #ef4444; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #ef4444;">dict</div>
  <div class="chaotic-node" style="position: absolute; left: 15%; top: 70%; width: 40px; height: 40px; background: rgba(239, 68, 68, 0.1); border: 2px solid #ef4444; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #ef4444;">{}</div>
  <div class="chaotic-node" style="position: absolute; left: 5%; top: 20%; width: 60px; height: 20px; background: rgba(239, 68, 68, 0.1); border: 2px solid #ef4444; border-radius: 0px; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #ef4444;">json</div>

  <!-- Central Binary Stream -->
  <div class="binary-stream" style="position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); color: var(--atlas-navy); font-family: monospace; font-size: 24px; font-weight: bold; letter-spacing: 5px; opacity: 0;">010101</div>

  <!-- Ordered Output Nodes -->
  <div class="ordered-node" style="position: absolute; right: 10%; top: 30%; width: 80px; height: 40px; background: rgba(16, 185, 129, 0.1); border: 2px solid #10b981; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #10b981; opacity: 0;">Model</div>
  <div class="ordered-node" style="position: absolute; right: 15%; top: 60%; width: 80px; height: 40px; background: rgba(16, 185, 129, 0.1); border: 2px solid #10b981; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #10b981; opacity: 0;">Model</div>

</div>

### Defining the Schema

Models are defined in YAML manifests. You have two options for where to write your Model configuration:

1. **Option A: Same File (Multi-Document YAML)**: Append the model definition directly to your `notes_ui/atlas.yaml` file, separating it from the worker definition with a triple dash (`---`).
2. **Option B: Separate File (Recommended)**: Create a new file named `note.yaml` (typically under a `models/` directory, e.g., `models/note.yaml`) to keep the worker configuration and model schema clean and independent.

Let's define a Model for our Notes (e.g. creating `models/note.yaml`):

```yaml
kind: model
id: myapp.models.note
version: 1.0.0

schema:
  id: string
  content: string
  timestamp: int64
  tags: list[string]
```

Let's break down this Model Manifest:
- `kind: model`: Tells Solon that this is a data schema contract, not an executable worker.
- `id: myapp.models.note`: The unique identifier for this model, used by other workers when import/export schemas are negotiated.
- `schema`: Defines the fields and types. Here, a Note has a string `id`, string `content`, 64-bit integer `timestamp`, and a list of strings called `tags`.

When you run `atlas build`, Solon (the Atlas compiler) reads this YAML file and auto-generates the native language bindings for every Worker in your workspace. For the Python UI Worker, it generates a Pydantic class. For a Rust Storage Worker, it would generate a Serde-derived struct.

---

### Utilizing the Model in Code

Now, let's update our `NotesUiWorker` to use the standard Storage capability, rather than an internal Python list.

Open `worker.py` and replace its contents with:

```python
import uuid
import time
import json
from atlas_sdk import WorkerBase, capability, on_invocation, require
from myapp.models import Note

class NotesUiWorker(WorkerBase):
    _worker_id = "myapp.notes_ui"
    _worker_name = "NotesUiWorker"
    _worker_version = "1.0.0"
    _worker_roles = ["worker"]

    # We declare that we REQUIRE the core storage capability to function.
    @require("atlas.core.storage", version="^1.0.0", as_alias="db")
    def on_init(self):
        """The Runtime guarantees 'db' is connected before calling this."""
        pass

    @capability("myapp.notes.add", version="1.0.0")
    @on_invocation("add")
    async def add(self, note_text: str) -> str:
        # We construct the strict auto-generated Model
        new_note = Note(
            id=str(uuid.uuid4()),
            content=note_text,
            timestamp=int(time.time()),
            tags=[]
        )
        
        # Serialize the model to a JSON string
        note_data = json.dumps({
            "id": new_note.id,
            "content": new_note.content,
            "timestamp": new_note.timestamp,
            "tags": new_note.tags
        })

        # We push the data across the network boundary to our required Storage capability.
        # We have NO idea if this is saving to Postgres, Redis, a local file, or memory.
        await self.db.write(new_note.id, note_data)
        
        return "Note perfectly saved across the boundary!"
```

### Code & YAML Deep Dive

Let's trace how the **Worker**, **Model**, and **YAML Manifests** connect together:

#### 1. The Python Worker Code (`worker.py`)
- **Imports**: `from myapp.models import Note` loads the Pydantic-based Model class that Solon generated from our `note.yaml` schema.
- **`@require("atlas.core.storage", ... as_alias="db")`**: Declares that this worker needs an external storage provider. The SDK automatically resolves this and injects a capability proxy object named `self.db` before `on_init()` runs.
- **`Note(...)`**: Instantiates the strongly-typed data contract. This prevents runtime typos or missing properties when passing data.
- **`await self.db.write(new_note.id, note_data)`**: Invokes the `write` capability on our proxy, pushing the serialized data through the network tunnel.

#### 2. The Worker's Manifest (`atlas.yaml`)
To make this code work, we must update the worker's `atlas.yaml` to declare this import dependency:
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

# Declares the required storage capability so the runtime can route self.db
imports:
  - capability: atlas.core.storage
    version: ^1.0.0
    optional: false
    reason: Required for notes database storage

exports:
  - capability: myapp.notes.add
    version: 1.0.0

translations: []
```

Here:
- `imports`: Declares that the runtime must bind a provider of the `"atlas.core.storage"` capability to our worker. This is what enables `self.db` to work under the hood!
- `exports`: Tells the runtime that this worker provides `"myapp.notes.add"`, meaning other workers in the system can call our `add` capability.

---

### The Invisible Serialization Engine

What actually happens when `await self.db.write(new_note.id, note_data)` is called?

Because we used the `@require` decorator, the `self.db` attribute is not a database client. It is an **Atlas SDK Capability Proxy**. 

When you invoke `.write()`, the proxy:
1. Validates and packages the request arguments.
2. Serializes the payload into a packed format.
3. Pushes the bytes through the ZeroMQ tunnel that the Runtime established during Boot.

The Storage Worker on the other end receives the bytes. Its own SDK validates the payload against the exact same manifest schema, deserializes it into a Rust struct, and passes it to the business logic function.

Neither developer had to write a single line of parsing code. Neither developer had to write an API route. Neither developer had to handle network reconnects.

**Atlas coordinates. Workers own.**

<br>
<strong><a href="../03-the-manager/" style="color: var(--atlas-red); text-decoration: none; border-bottom: 1px solid var(--atlas-red); padding-bottom: 2px;">Next Chapter: Orchestration & Managers &rarr;</a></strong>

</div>
