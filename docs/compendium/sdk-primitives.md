# SDK Primitive Functions

The Atlas architecture is built on structural primitives (Workers, Managers, Models). This document covers the **primitive functions** within the Atlas Python SDK that you use to interact with those structural primitives.

The Atlas SDK is designed to be completely declarative and invisible. You rarely call functions imperatively; instead, you declare intent, and the Runtime executes it.

---

## 1. Worker Primitives

To create a Worker, you inherit from `WorkerBase`.

### `@capability(id: str, version: str)`
Declares that a method fulfills a specific Capability Model contract.
```python
from atlas_sdk import WorkerBase, capability

class MyWorker(WorkerBase):
    @capability("atlas.storage.write", version="1.0.0")
    def my_custom_write_handler(self, key: str, data: bytes) -> bool:
        pass
```

### `@on_invocation(capability_id: str)`
Maps an incoming Invocation from the Runtime directly to a class method. You do not write `if/else` routers. The SDK handles all invocation routing based on the header.
```python
    @on_invocation("atlas.storage.write")
    def handle_write(self, key: str, data: bytes) -> bool:
        # Business logic goes here
        return True
```

### `@on_event(event_id: str)`
Registers a listener for an asynchronous event published by another Worker.
```python
    @on_event("atlas.storage.written")
    def handle_write_notification(self, payload: dict):
        print(f"Key {payload['key']} was written!")
```

---

## 2. Context Primitives

Inside an executing method, you have access to the `AtlasContext`, which provides imperative functions for communicating with the Runtime.

### `Atlas.invoke(capability: str, payload: dict) -> Future`
Sends an execution request to another Worker. 
```python
from atlas_sdk import Atlas

def handle_something(self):
    # Sends an invocation to whatever Worker the Steward bound to this capability
    result = Atlas.invoke("atlas.storage.read", {"key": "user_123"})
```

### `Atlas.emit(event_id: str, payload: dict) -> void`
Publishes an asynchronous event to the Room Registry. Any Worker in the Room listening via `@on_event` will receive it.
```python
    Atlas.emit("atlas.custom.job_finished", {"status": "success"})
```

---

## 3. Manager Primitives

Managers do not use `WorkerBase`. Instead, they use the `ManagerBuilder` to declare application topology.

### `ManagerBuilder.require(worker_id: str, version: str)`
Declares a hard dependency. If this Worker cannot be resolved, the application will fail to start.
```python
from atlas_sdk import ManagerBuilder

app = ManagerBuilder("my_notes_app")
app.require("atlas.core.sqlite", version="2.x")
```

### `ManagerBuilder.optional(worker_id: str)`
Declares a soft dependency. If this Worker is missing, the application starts normally, but invocations sent to it will return a `CapabilityUnavailable` error.
```python
app.optional("atlas.ui.telemetry")
```

### `ConfigModel.set(key: str, value: Any)`
Injects global state into the Runtime environment before boot.
```python
from atlas_sdk import ConfigModel

ConfigModel.set("LOG_LEVEL", "DEBUG")
ConfigModel.set("STORAGE_ROOT", "/var/lib/atlas/data")
```

### `ManagerBuilder.build() -> Manifest`
Compiles the Manager's declarations into an `atlas.yaml` file that the Runtime can execute.
```python
manifest = app.build()
```

---

## 4. The CLI Primitives

While the SDK handles code, the Atlas CLI handles the ecosystem.

- `atlas run`: Boots the Atlas Runtime using the `atlas.yaml` in the current directory.
- `atlas new [type] [name]`: Scaffolds a new Worker, Model, Manager, or Adapter.
- `atlas test`: Invokes Solon to validate the Worker against its declared Models.
- `atlas inspect`: Opens Miron in the terminal to view the active Registry.
- `atlas build`: Packages a Worker into a distributable `.atlas` binary.
