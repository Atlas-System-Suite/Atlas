# Atlas SDK Quick Start 🚀

Welcome to Atlas! This guide will get you from zero to a running Worker in under 5 minutes.

---

## Prerequisites

Make sure you have:
- Python 3.13+
- PyYAML (`pip install pyyaml`)
- pytest (`pip install pytest`)

Run `atlas doctor` to verify your environment:

```bash
atlas doctor
```

---

## 1. Create Your First Worker

```bash
atlas new worker my_greeter
cd my_greeter
```

This scaffolds a complete Worker project:
```text
my_greeter/
  manifest.yaml      # Declares capabilities & metadata
  worker.py          # Your business logic
  test_my_greeter.py # Pre-written tests
  README.md          # Auto-generated docs
```

---

## 2. Write Your Logic

Open `worker.py` and modify the `hello` method:

```python
from atlas_sdk import WorkerBase, capability, on_invocation


class MyGreeterWorker(WorkerBase):
    _worker_id = "atlas.my_greeter"
    _worker_name = "MyGreeterWorker"
    _worker_roles = ["worker"]

    @capability("atlas.my_greeter.greet", version="1.0.0")
    @on_invocation("greet")
    def greet(self, name: str = "World") -> str:
        return f"Hello, {name}! Welcome to Atlas. 🌍"
```

That's it. No boilerplate. No XML. No 47-step configuration ritual. Just a class, a decorator, and your logic.

---

## 3. Test It

```bash
atlas test
```

The scaffolded tests verify that your capabilities are exported correctly and your invocation handlers work.

---

## 4. Validate Your Manifest

```bash
atlas validate
```

This checks your `manifest.yaml` for missing fields, invalid policies, and circular dependencies.

---

## 5. Inspect It

```bash
atlas inspect
```

See a pretty-printed summary of your Worker's capabilities, imports, and translations.

---

## 6. Build a Package

```bash
atlas build
```

This creates a deterministic `.atlas` package in the `dist/` directory, ready for distribution.

---

## What's Next?

- **Build a Model**: `atlas new model my_storage_model`
- **Build an Adapter**: `atlas new adapter json_to_msgpack`
- **Compose a Manager**: `atlas new manager my_notes_app`
- **Read the full guides**:
  - [Building Workers & Roles](building-workers.md)
  - [Building Managers](building-managers.md)

---

## The Golden Rule

> **Program against Models, never implementations.**

If your Worker needs storage, import the `StorageModel`. If it needs logging, import the `LoggerModel`. Atlas will resolve the right Worker at runtime. You just focus on your business logic.

Happy building! ✨
