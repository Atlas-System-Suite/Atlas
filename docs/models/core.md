# Core Models

Core Models represent the fundamental capabilities required to operate an Atlas application. 

---

## `atlas.core.logger`

**Type:** Capability Model
**Version:** `1.0.0`
**Description:** Standardized logging and telemetry.

### Capabilities
- **`info(message: string, context: dict) -> void`**
- **`warn(message: string, context: dict) -> void`**
- **`error(message: string, exc_info: string, context: dict) -> void`**
- **`debug(message: string, context: dict) -> void`**

### Configuration
- `LOG_LEVEL` (string, required: false) - Limits output below the specified severity.

---

## `atlas.core.config`

**Type:** Capability Model
**Version:** `1.0.0`
**Description:** Global configuration resolution.

### Capabilities
- **`get(key: string, default: string) -> string`**
- **`has(key: string) -> boolean`**
- **`keys() -> list[string]`**

### Lifecycle
Must be fully initialized during the `on_start()` phase. Mutations to configuration during execution are strictly prohibited to maintain determinism.

---

## `atlas.core.clock`

**Type:** Capability Model
**Version:** `1.0.0`
**Description:** Deterministic time resolution and sleeping.

### Capabilities
- **`now() -> string`** (Returns ISO 8601 UTC string)
- **`timestamp() -> float`** (Returns Unix epoch time)
- **`sleep(seconds: float) -> void`**

---

## `atlas.core.scheduler`

**Type:** Capability Model
**Version:** `1.0.0`
**Description:** Recurring or delayed Invocation execution.

### Capabilities
- **`schedule(cron: string, capability: string, payload: dict) -> string`** (Returns job ID)
- **`delay(seconds: float, capability: string, payload: dict) -> string`**
- **`cancel(job_id: string) -> boolean`**

### Events
- `job_started` (job_id: string)
- `job_completed` (job_id: string, success: boolean)

---

## `atlas.core.uuid`

**Type:** Capability Model
**Version:** `1.0.0`
**Description:** Unique identifier generation.

### Capabilities
- **`v4() -> string`** (Standard random UUID)
- **`v7() -> string`** (Time-ordered UUID)

---

## Other Planned Core Capabilities
- **Settings:** Persistent, user-specific configurations (differs from global `config`).
- **Registry:** Exposes read-only queries against the local Room Registry.
- **Environment:** Exposes safe, filtered access to host OS environment variables.
- **Resource:** Extracts binary resources bundled in an `.atlas` package.
- **Lifecycle:** Allows Managers to listen for or trigger graceful shutdown sequences.
- **Health:** Exposes application liveness and readiness probes.
- **Timer:** Provides high-resolution profiling durations.
- **Random:** Provides seedable, deterministic random number generation.
