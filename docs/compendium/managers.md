# Building Managers

> The complete guide to creating, understanding, and running Atlas Managers — the application orchestrators.

---

## What is a Manager?

A Manager is an **application orchestrator** in Atlas. It does not contain business logic. Its job is to:

1. Declare which Workers are needed.
2. Provide configuration values (API keys, ports, log levels).
3. Generate a finalized `atlas.yaml` manifest for the Runtime to boot.

Think of Workers as musicians and the Manager as the conductor — it assembles the orchestra, hands out the sheet music, and starts the performance. It never plays an instrument itself.

---

## Quick Start

### 1. Scaffold

```bash
atlas new
```

Select `manager`, enter a name like `my_notes_app`, and choose `python`.

Or use the fast path:

```bash
atlas new manager my_notes_app
```

### 2. Configure

Open `main.py` and customize your worker composition and configuration.

### 3. Build

```bash
cd my_notes_app
python main.py
```

This generates the final `atlas.yaml` manifest.

### 4. Run

```bash
atlas run
```

This boots the Atlas Runtime using the generated manifest.

---

## Project Structure

When you scaffold a Manager, Atlas generates this directory:

```text
my_notes_app/
├── atlas.yaml     # The generated manifest — declares workers and config
├── main.py        # The build script — composes the application using ManagerBuilder
└── README.md      # Documentation — auto-generated project readme
```

---

## File Reference

### `main.py` — The Build Script

This is where you compose your application. It uses the `ManagerBuilder` API to declare which Workers your application needs and what configuration they require.

```python
"""
MyNotesApp — An Atlas Manager

A notes application built on Atlas.
"""
from atlas_sdk import ManagerBuilder


def build():
    manager = (
        ManagerBuilder("my_notes_app", version="1.0.0", description="A notes application")
        .add_worker("atlas.core.logger")
        .add_worker("atlas.core.config")
        .add_worker("atlas.core.storage")
        .configure("LOG_LEVEL", "INFO")
        .build()
    )
    manager.write("atlas.yaml")
    print(f"Manager '{manager.name}' built successfully!")
    return manager


if __name__ == "__main__":
    build()
```

> **Why a Python script instead of just YAML?**
> Because Python lets you dynamically compose your application — pull secrets from environment variables, toggle workers based on `DEBUG_MODE`, read from `.env` files. The generated YAML ensures the Runtime execution is purely declarative and deterministic.

---

### `atlas.yaml` — The Generated Manifest

When you run `python main.py`, it produces this file. This is the **source of truth** that the Atlas Runtime reads at boot time.

```yaml
kind: manager
id: atlas.my_notes_app
name: MyNotesApp
version: 1.0.0
description: A notes application

workers:
  - id: atlas.core.logger
  - id: atlas.core.config
  - id: atlas.core.storage

config:
  LOG_LEVEL: INFO
```

#### Field-by-Field Breakdown

| Field | Required | Description |
|---|---|---|
| `kind` | ✅ | Always `manager` for Managers. |
| `id` | ✅ | Globally unique identifier for this application. |
| `name` | ✅ | Human-readable display name. |
| `version` | ✅ | Semantic version string. |
| `description` | ❌ | Short description of the application. |
| `workers` | ✅ | List of Worker IDs that this application requires. |
| `workers[].id` | ✅ | The unique ID of a Worker to include. |
| `workers[].entry_point` | ❌ | If `true`, this Worker is the primary entry point. |
| `workers[].config` | ❌ | Per-worker configuration overrides. |
| `config` | ❌ | Global configuration key-value pairs. Accessible to all Workers via `ConfigModel`. |

---

### `README.md` — Documentation

Auto-generated project readme. Lists the Workers included and how to run the application.

---

## ManagerBuilder API Reference

The `ManagerBuilder` class provides a fluent, chainable API for composing applications.

### Constructor

```python
ManagerBuilder(name: str, version: str = "1.0.0", description: str = "")
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `name` | `str` | — | The application name. |
| `version` | `str` | `"1.0.0"` | Semantic version. |
| `description` | `str` | `""` | Short description. |

### `.add_worker(worker_id, **config_overrides)`

Adds a Worker to the application by its globally unique ID.

```python
builder.add_worker("atlas.core.logger")
builder.add_worker("my.db.worker", DATABASE_URL="sqlite:///data.db")
```

| Parameter | Type | Description |
|---|---|---|
| `worker_id` | `str` | The Worker's unique identifier (must match the Worker's `atlas.yaml` `id` field). |
| `**config_overrides` | `Any` | Optional per-worker configuration overrides. |

### `.set_entry_point(worker_id)`

Designates a Worker as the primary entry point. This Worker is invoked first when the Manager starts.

```python
builder.set_entry_point("my.notes.ui")
```

### `.configure(key, value)`

Sets a global configuration value. Workers can read these at runtime via the `ConfigModel`.

```python
builder.configure("LOG_LEVEL", "DEBUG")
builder.configure("PORT", 8080)
```

### `.build()`

Finalizes the composition and returns a `ManagerManifest` object. Validates that at least one Worker has been added.

```python
manifest = builder.build()  # Returns ManagerManifest
```

### `ManagerManifest.write(path)`

Serializes the manifest to a YAML file.

```python
manifest.write("atlas.yaml")
```

### `ManagerManifest.to_dict()`

Returns the manifest as a Python dictionary (useful for programmatic inspection).

```python
data = manifest.to_dict()
print(data["workers"])
```

---

## What Happens When You Run `atlas run`

When you execute `atlas run` in a directory containing an `atlas.yaml`:

1. **Read**: The CLI reads `atlas.yaml` from the current directory.
2. **Boot**: The Atlas Runtime initializes all subsystems (Registry, Worker Manager, Session Manager, etc.).
3. **Discover**: The Runtime searches for each Worker declared in `workers[]` by its ID.
4. **Load**: Workers are dynamically loaded and instantiated. Their `on_init()` hooks are called.
5. **Wire**: Capabilities and Invocations are registered in the Global Registry.
6. **Inject Config**: The `config` block is injected into the `ConfigModel`, making values available to all Workers.
7. **Start**: Each Worker's `on_start()` hook is called. The event loop begins.

---

## Dynamic Configuration

Because your Manager is a Python script, you can pull configuration dynamically at build time:

### Environment Variables

```python
import os
from atlas_sdk import ManagerBuilder

def build():
    builder = ManagerBuilder("production_app", version="2.0.0")
    builder.add_worker("atlas.core.logger")

    db_password = os.getenv("DB_PASSWORD")
    if not db_password:
        raise ValueError("DB_PASSWORD is required!")

    builder.configure("DB_PASSWORD", db_password)

    if os.getenv("DEBUG_MODE") == "1":
        builder.add_worker("atlas.tools.inspector")
        builder.configure("LOG_LEVEL", "DEBUG")
    else:
        builder.configure("LOG_LEVEL", "INFO")

    manifest = builder.build()
    manifest.write("atlas.yaml")
```

### `.env` Files

```python
from pathlib import Path
from atlas_sdk import ManagerBuilder

def build():
    env = {}
    env_file = Path(".env")
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()

    builder = ManagerBuilder("my_app")
    builder.add_worker("atlas.core.logger")
    builder.configure("API_KEY", env.get("API_KEY", "default"))

    manifest = builder.build()
    manifest.write("atlas.yaml")
```

---

## Complete Example: A Notes Application

### `main.py`

```python
"""
NotesApp — An Atlas Manager

A simple notes application that demonstrates Manager composition.
"""
import os
from atlas_sdk import ManagerBuilder


def build():
    builder = ManagerBuilder(
        "notes_app",
        version="1.0.0",
        description="A simple note-taking application"
    )

    # Core infrastructure
    builder.add_worker("atlas.core.logger")
    builder.add_worker("atlas.core.config")
    builder.add_worker("atlas.core.storage")
    builder.add_worker("atlas.core.clock")

    # Application worker
    builder.add_worker("my.notes.worker")
    builder.set_entry_point("my.notes.worker")

    # Configuration
    builder.configure("LOG_LEVEL", os.getenv("LOG_LEVEL", "INFO"))
    builder.configure("STORAGE_PATH", os.getenv("STORAGE_PATH", "./data"))
    builder.configure("MAX_NOTES", 1000)

    manifest = builder.build()
    manifest.write("atlas.yaml")
    print(f"✅ '{manifest.name}' built with {len(manifest.workers)} workers.")
    return manifest


if __name__ == "__main__":
    build()
```

### Generated `atlas.yaml`

```yaml
manager:
  name: notes_app
  version: 1.0.0
  description: A simple note-taking application
workers:
  - id: atlas.core.logger
    entry_point: false
  - id: atlas.core.config
    entry_point: false
  - id: atlas.core.storage
    entry_point: false
  - id: atlas.core.clock
    entry_point: false
  - id: my.notes.worker
    entry_point: true
config:
  LOG_LEVEL: INFO
  STORAGE_PATH: ./data
  MAX_NOTES: 1000
```

### Running

```bash
python main.py     # Generate atlas.yaml
atlas run          # Boot the Runtime
```

---

## Best Practices

1. **Keep it declarative.** Use `main.py` to *build* the configuration. Don't put runtime business logic here — once `atlas run` starts, `main.py` is no longer executing.
2. **Fail fast at build time.** If your app requires a `DB_PASSWORD`, raise an error in `main.py` when it's missing. Don't let the Worker crash at runtime.
3. **Commit the script, gitignore the YAML.** If your Manager pulls secrets from the environment, add `atlas.yaml` to `.gitignore`. Only commit `main.py`.
4. **Set an entry point.** Use `.set_entry_point()` to tell the Runtime which Worker should be invoked first.
5. **Use per-worker config overrides.** If a specific Worker needs different settings than the global config, pass them via `.add_worker("id", KEY="value")`.

---

## What's Next?

- **Build a Worker**: See [Building Workers](workers.md) for the complete guide to writing business logic.
- **Build an Adapter**: See [Building Adapters](adapters.md) for format translation workers.
- **Explore the SDK**: See [CLI Reference](cli-reference.md) for the full command reference.
