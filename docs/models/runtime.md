# Runtime Models

Runtime Models expose the internal execution mechanics of the Atlas ecosystem to authorized Workers (like Miron or Varsity).

---

## `atlas.runtime.discovery`

**Type:** Capability Model
**Version:** `1.0.0`
**Description:** Queries the Global Registry for available Workers and Capabilities.

### Capabilities
- **`find_providers(capability: string) -> list[string]`** (Returns a list of Worker IDs)
- **`get_manifest(worker_id: string) -> dict`**

---

## `atlas.runtime.session`

**Type:** Capability Model
**Version:** `1.0.0`
**Description:** Manages the lifecycle of point-to-point connections.

### Capabilities
- **`establish(target_worker_id: string, header: dict) -> string`** (Returns Session ID)
- **`terminate(session_id: string) -> boolean`**
- **`send(session_id: string, payload: dict) -> void`**

---

## `atlas.runtime.room`

**Type:** Capability Model
**Version:** `1.0.0`
**Description:** Manages shared execution contexts.

### Capabilities
- **`create(header: dict) -> string`** (Returns Room ID)
- **`join(room_id: string, worker_id: string) -> boolean`**
- **`leave(room_id: string, worker_id: string) -> boolean`**
- **`freeze(room_id: string) -> boolean`**
- **`recover(room_id: string) -> boolean`**

### Events
- `room_created` (room_id: string)
- `room_destroyed` (room_id: string)

---

## `atlas.resource.invocation`

**Type:** Resource Model
**Version:** `1.0.0`
**Description:** Canonical representation of an execution request in the Atlas Runtime.

### Schema
```yaml
schema:
  type: object
  properties:
    id:
      type: string
    session_id:
      type: string
    capability:
      type: string
    payload:
      type: dict
    timestamp:
      type: float
```

---

## Other Planned Runtime Capabilities
- **Translation:** Hooks for injecting custom format serializers dynamically.
- **Package:** For unpacking and validating `.atlas` distribution binaries.
- **Update:** For downloading and hot-swapping new versions of Workers.
- **Diagnostics:** For gathering heap dumps, CPU profiles, and tracing spans (used by Miron).
