# Storage Models

Storage Models decouple business logic from persistence technologies.

---

## `atlas.storage`

**Type:** Capability Model
**Version:** `1.0.0`
**Description:** Standard raw byte key-value store.

### Capabilities
- **`write(key: string, data: bytes) -> boolean`**
- **`read(key: string) -> bytes`**
- **`delete(key: string) -> boolean`**
- **`exists(key: string) -> boolean`**
- **`list(prefix: string) -> list[string]`**

### Errors
- `StorageFullError`
- `KeyNotFoundError`
- `PermissionDeniedError`

---

## `atlas.storage.document`

**Type:** Capability Model
**Version:** `1.0.0`
**Description:** Structural document store (JSON, YAML, NoSQL).

### Capabilities
- **`insert(collection: string, doc_id: string, document: dict) -> boolean`**
- **`get(collection: string, doc_id: string) -> dict`**
- **`query(collection: string, filters: dict) -> list[dict]`**
- **`delete(collection: string, doc_id: string) -> boolean`**

---

## `atlas.storage.cache`

**Type:** Capability Model
**Version:** `1.0.0`
**Description:** Ephemeral storage with Time-To-Live (TTL).

### Capabilities
- **`set(key: string, value: bytes, ttl_seconds: integer) -> boolean`**
- **`get(key: string) -> bytes`**
- **`invalidate(key: string) -> void`**
- **`clear() -> void`**

---

## `atlas.resource.file`

**Type:** Resource Model
**Version:** `1.0.0`
**Description:** Canonical representation of a file on a disk.

### Schema
```yaml
schema:
  type: object
  properties:
    path:
      type: string
      description: "Absolute or relative path to the file."
    size_bytes:
      type: integer
    content_type:
      type: string
      description: "MIME type (e.g., text/plain)."
    created_at:
      type: float
    modified_at:
      type: float
    raw_data:
      type: bytes
      description: "The file payload (optional, usually streamed instead)."
```

---

## Other Planned Storage Capabilities
- **Filesystem:** Exposes raw directory manipulation (mkdir, rmdir) outside of basic `write/read`.
- **Database:** Exposes SQL-like relational queries and migrations.
- **Blob Storage:** Optimized for multi-part uploads of large media.
- **Configuration Store:** A persistent layer specifically tuned for reading and writing `atlas.core.settings`.
