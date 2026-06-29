# Building Workers

> The complete guide to creating, understanding, and running Atlas Workers.

---

## What is a Worker?

A Worker is the **fundamental unit of execution** in Atlas. Every piece of business logic — logging, storage, AI inference, UI rendering — lives inside a Worker. The Atlas Runtime itself contains zero business logic; it only coordinates Workers.

Workers communicate through **Capabilities** (what they can do) and **Invocations** (requests to do something). They are discovered, loaded, and wired together automatically by the Runtime based on a declarative manifest.

---

## Quick Start

### 1. Scaffold

```bash
atlas new
```

Select `worker`, enter a name like `my_greeter`, and choose `python`.

Or use the fast path:

```bash
atlas new worker my_greeter
```

### 2. Implement

Open `my_greeter/worker.py` and write your logic.

### 3. Test

```bash
cd my_greeter
atlas test
```

### 4. Run

```bash
atlas run
```

This reads the `atlas.yaml` manifest in your project directory and boots the Runtime.

---

## Project Structure

When you scaffold a Worker, Atlas generates this directory:

```text
my_greeter/
├── atlas.yaml          # The manifest — declares identity, capabilities, and metadata
├── worker.py           # The implementation — your actual business logic
├── test_my_greeter.py  # Tests — validates capabilities and behavior
└── README.md           # Documentation — auto-generated project readme
```

Every file has a specific purpose. Let's walk through each one.

---

## File Reference

### `atlas.yaml` — The Manifest

The manifest is the **identity card** of your Worker. The Runtime reads this file to understand what your Worker is, what it can do, and how to load it. You never import or reference this file in Python — the Runtime handles it.

```yaml
kind: worker

id: atlas.my_greeter
name: MyGreeterWorker
version: 1.0.0
description: A simple greeter worker
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
  - capability: atlas.my_greeter
    version: 1.0.0

translations: []
```

#### Field-by-Field Breakdown

| Field | Required | Description |
|---|---|---|
| `kind` | ✅ | Always `worker` for Workers. Other values: `adapter`, `manager`. |
| `id` | ✅ | Globally unique identifier. Convention: `namespace.name` (e.g. `atlas.core.logger`). |
| `name` | ✅ | Human-readable display name. |
| `version` | ✅ | Semantic version string (e.g. `1.0.0`). |
| `description` | ❌ | Short description of what this Worker does. |
| `language` | ✅ | Implementation language. Currently `python`. |
| `roles` | ✅ | Tags describing what kind of Worker this is. See [Roles](#roles) below. |
| `execution.policy` | ✅ | How many instances the Runtime should create. Options: `singleton`, `pool`, `on_demand`. |
| `communication.transports` | ✅ | How this Worker communicates. Options: `memory`, `tcp`, `grpc`. |
| `communication.formats` | ✅ | Data serialization formats. Options: `python`, `json`, `msgpack`, `protobuf`. |
| `communication.default_format` | ✅ | The default format used when none is specified. |
| `imports` | ✅ | Capabilities this Worker **requires** from other Workers. |
| `exports` | ✅ | Capabilities this Worker **provides** to the ecosystem. |
| `translations` | ✅ | Format conversions this Worker can perform (for Adapters). |

---

### `worker.py` — The Implementation

This is where your business logic lives. Every Worker is a Python class that extends `WorkerBase` from the Atlas SDK.

```python
"""
MyGreeterWorker — An Atlas Worker

A simple greeter worker.
"""
from atlas_sdk import WorkerBase, capability, on_invocation


class MyGreeterWorker(WorkerBase):
    _worker_id = "atlas.my_greeter"
    _worker_name = "MyGreeterWorker"
    _worker_version = "1.0.0"
    _worker_roles = ["worker"]

    def on_init(self):
        """Called after construction. Set up your state here."""
        self.greeting_count = 0

    def on_start(self):
        """Called when the runtime starts this worker."""
        pass

    def on_stop(self):
        """Called on shutdown. Clean up resources here."""
        pass

    @capability("atlas.my_greeter.hello", version="1.0.0")
    @on_invocation("hello")
    def hello(self, name: str = "World") -> str:
        """A simple hello capability."""
        self.greeting_count += 1
        return f"Hello, {name}! From MyGreeterWorker."
```

#### Class Attributes

These static attributes must match your `atlas.yaml`:

### Core Attributes

- `_worker_id`: **(Required)** Must match the `id` in `atlas.yaml`.
- `_worker_name`: **(Required)** Must match the `name` in `atlas.yaml`.
- `_worker_version`: **(Required)** Must match the `version` in `atlas.yaml`.
- `_worker_roles`: *(Optional)* A list of roles this worker fulfills.

??? abstract "Under the Hood: The WorkerBase Metaclass"
    When you define a class inheriting from `WorkerBase`, a metaclass called `WorkerMeta` is secretly inspecting your class at definition time. It looks for any methods tagged with `@capability` and `@on_invocation`, extracts their metadata, and stores it in a hidden class attribute. This is how the SDK can introspect your worker without ever instantiating it!

---

## Lifecycle Hooks

These methods are called automatically by the Runtime at specific points in the Worker's lifetime. Override them as needed.

| Method | When It's Called | Use Case |
|---|---|---|
| `on_init()` | Immediately after the Worker object is constructed. | Initialize internal state, open files, set up data structures. |
| `on_start()` | When the Runtime starts executing this Worker. | Start background threads, connect to external services. |
| `on_stop()` | When the Runtime shuts down this Worker. | Close connections, flush buffers, release resources. |
| `on_health_check()` | Periodically by the Runtime. Return a `dict`. | Report health status. Default returns `{"healthy": True}`. |

---

### `test_my_greeter.py` — Tests

Atlas generates a test file that validates your Worker's capabilities using the SDK's testing utilities.

```python
"""Tests for MyGreeterWorker."""
from atlas_sdk.testing import MockRuntime, assert_capability_exported
from worker import MyGreeterWorker


def test_my_greeter_exports_capability():
    worker = MyGreeterWorker()
    assert_capability_exported(worker, "atlas.my_greeter.hello")


def test_my_greeter_hello():
    runtime = MockRuntime()
    runtime.register(MyGreeterWorker, "atlas.my_greeter")
    result = runtime.invoke("atlas.my_greeter", "hello", {"name": "Atlas"})
    assert "Hello" in result
```

#### Testing Utilities

| Function | Description |
|---|---|
| `MockRuntime()` | A lightweight fake runtime. Does **not** boot Atlas. Lets you register workers, invoke actions, and inspect results in isolation. |
| `MockRuntime.register(cls, id)` | Instantiates a Worker class, calls `on_init()`, and registers it under the given ID. |
| `MockRuntime.invoke(id, action, payload)` | Simulates an Invocation against a registered Worker. Returns the result. |
| `assert_capability_exported(worker, name)` | Asserts that a Worker instance exports a specific capability. Fails with a clear message if not. |
| `assert_invocation_handled(worker, action)` | Asserts that a Worker has a handler registered for a given action string. |
| `assert_model_compliant(model, impl)` | Asserts that a class correctly implements all abstract methods defined by a Model. |
| `TestHarness()` | A heavier-weight environment that boots a **real** `AtlasRuntime` for integration testing. Use as a context manager: `with TestHarness() as runtime:`. |

Run tests with:

```bash
atlas test
```

This discovers and runs all `test_*.py` files using `pytest`.

---

### `README.md` — Documentation

Auto-generated project documentation. Lists your capabilities and provides usage examples. Update this as your Worker evolves.

---

## Decorators Reference

Decorators are how you tell the Atlas SDK what your methods do. The SDK reads them at class definition time and automatically builds a metadata registry.

### `@capability(name, version, precedence)`

Marks a method as an **exported Capability**. This is what other Workers can discover and invoke.

```python
@capability("atlas.my_greeter.hello", version="1.0.0")
def hello(self, name: str = "World") -> str:
    return f"Hello, {name}!"
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `name` | `str` | — | The globally unique capability identifier. |
| `version` | `str` | `"1.0.0"` | Semantic version of this capability. |
| `precedence` | `int` | `0` | Priority when multiple Workers export the same capability. Higher wins. |

### `@on_invocation(action)`

Registers a method as a handler for a specific **Invocation action**. When the Runtime receives an invocation with this action string, it routes it to this method.

```python
@on_invocation("greet")
def handle_greet(self, name: str) -> str:
    return f"Hello, {name}!"
```

| Parameter | Type | Description |
|---|---|---|
| `action` | `str` | The action string that triggers this handler. |

> **Tip:** You can stack `@capability` and `@on_invocation` on the same method. This is common — it exports the method as a capability AND registers it as an invocation handler:
> ```python
> @capability("atlas.my_greeter.hello", version="1.0.0")
> @on_invocation("hello")
> def hello(self, name: str = "World") -> str:
>     return f"Hello, {name}!"
> ```

### `@configure(key, default, required)`

Marks a method as a **configuration consumer**. The SDK injects the value from the global config before the Worker starts.

```python
@configure("DATABASE_URL", required=True)
def set_db_url(self, value: str):
    self.db_url = value
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `key` | `str` | — | The configuration key to read. |
| `default` | `Any` | `None` | Fallback value if the key is not set. |
| `required` | `bool` | `False` | If `True`, the Runtime raises an error if the key is missing. |

---

## Roles

Roles are metadata tags in your manifest's `roles` array. They do **not** change how the Runtime executes your Worker, but they tell Atlas Studio and other developers what kind of Worker this is.

| Role | Description | Example |
|---|---|---|
| `worker` | Generic Worker. The default. | Any custom business logic. |
| `app` | User-facing entry point. Typically imports many capabilities. | A CLI interface, a web UI. |
| `database` | Provides data persistence. | SQLite worker, S3 worker. |
| `translator` | Converts between data formats. Stateless. | JSON → MessagePack converter. |
| `observer` | Read-only. Binds to Rooms for monitoring. Cannot modify state. | Telemetry, logging, tracing. |
| `core` | Part of the Atlas standard library. | `atlas.core.logger`, `atlas.core.storage`. |
| `stdlib` | Shipped with Atlas. | Standard library workers. |
| `ai` | Provides AI/ML capabilities. | LLM inference, embedding generation. |
| `hardware` | Interfaces with physical devices. | GPIO, USB, Bluetooth. |

You can combine roles freely:

```yaml
roles: [database, storage, core, stdlib]
```

---

## Execution Policies

The `execution.policy` field in your manifest controls how many instances the Runtime creates.

| Policy | Behavior | Use Case |
|---|---|---|
| `singleton` | Exactly one instance exists at all times. | Loggers, config managers, UI workers. |
| `pool` | A pool of instances, reused across invocations. | Database connections, CPU-heavy compute. |
| `on_demand` | A new instance is created per invocation, then destroyed. | Stateless processors, one-shot tasks. |

---

## Using Standard Models

Atlas ships with **Standard Models** — abstract contracts that define how common capabilities should behave. You should always program against a Model, never a concrete implementation.

### Logger (`atlas.core.logger`)

```python
from models.core.logger_model import LoggerModel

class MyWorker:
    def __init__(self, logger: LoggerModel):
        self.logger = logger

    def do_work(self):
        self.logger.info("Starting work", context={"task": "process_data"})
        try:
            result = self.process()
        except Exception as e:
            self.logger.error("Work failed", exc_info=str(e))
```

**LoggerModel methods:**

| Method | Parameters | Description |
|---|---|---|
| `debug(message, context=None)` | `str`, `dict` | Debug-level log entry. |
| `info(message, context=None)` | `str`, `dict` | Informational log entry. |
| `warn(message, context=None)` | `str`, `dict` | Warning log entry. |
| `error(message, exc_info=None, context=None)` | `str`, `str`, `dict` | Error log entry with optional exception info. |

### Config (`atlas.core.config`)

```python
from models.core.config_model import ConfigModel

class SecureWorker:
    def __init__(self, config: ConfigModel):
        self.api_key = config.get("API_KEY", default="guest")
        if config.has("DEBUG_MODE"):
            print("Debug mode activated!")
```

### Storage (`atlas.core.storage`)

```python
from models.core.storage_model import StorageModel

class NoteTaker:
    def __init__(self, storage: StorageModel):
        self.storage = storage

    def save(self, title: str, content: str):
        self.storage.write(f"notes/{title}.txt", content)

    def load(self, title: str) -> str | None:
        if self.storage.exists(f"notes/{title}.txt"):
            return self.storage.read(f"notes/{title}.txt").decode("utf-8")
        return None
```

### Clock (`atlas.core.clock`)

```python
from models.core.clock_model import ClockModel

class ScheduledWorker:
    def __init__(self, clock: ClockModel):
        self.clock = clock

    def run(self):
        start = self.clock.timestamp()
        self.clock.sleep(2.0)
        elapsed = self.clock.timestamp() - start
        print(f"Elapsed: {elapsed}s")
```

---

## Complete Example: Building a Counter Worker

Here is a full, end-to-end example of a Worker that maintains a counter.

### `atlas.yaml`

```yaml
kind: worker

id: atlas.example.counter
name: CounterWorker
version: 1.0.0
description: A stateful counter that tracks a running total.
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
  - capability: atlas.example.counter.increment
    version: 1.0.0
  - capability: atlas.example.counter.get
    version: 1.0.0
  - capability: atlas.example.counter.reset
    version: 1.0.0

translations: []
```

### `worker.py`

```python
"""
CounterWorker — An Atlas Worker

A stateful counter that tracks a running total.
"""
from atlas_sdk import WorkerBase, capability, on_invocation


class CounterWorker(WorkerBase):
    _worker_id = "atlas.example.counter"
    _worker_name = "CounterWorker"
    _worker_version = "1.0.0"
    _worker_roles = ["worker"]

    def on_init(self):
        self.count = 0

    def on_start(self):
        print(f"CounterWorker started. Initial count: {self.count}")

    def on_stop(self):
        print(f"CounterWorker stopped. Final count: {self.count}")

    @capability("atlas.example.counter.increment", version="1.0.0")
    @on_invocation("increment")
    def increment(self, amount: int = 1) -> int:
        """Increment the counter by the given amount."""
        self.count += amount
        return self.count

    @capability("atlas.example.counter.get", version="1.0.0")
    @on_invocation("get")
    def get(self) -> int:
        """Return the current count."""
        return self.count

    @capability("atlas.example.counter.reset", version="1.0.0")
    @on_invocation("reset")
    def reset(self) -> int:
        """Reset the counter to zero."""
        self.count = 0
        return self.count
```

### `test_counter.py`

```python
"""Tests for CounterWorker."""
from atlas_sdk.testing import MockRuntime, assert_capability_exported


def test_counter_exports():
    from worker import CounterWorker
    worker = CounterWorker()
    assert_capability_exported(worker, "atlas.example.counter.increment")
    assert_capability_exported(worker, "atlas.example.counter.get")
    assert_capability_exported(worker, "atlas.example.counter.reset")


def test_counter_lifecycle():
    from worker import CounterWorker
    runtime = MockRuntime()
    runtime.register(CounterWorker, "atlas.example.counter")

    # Initial state
    result = runtime.invoke("atlas.example.counter", "get")
    assert result == 0

    # Increment
    result = runtime.invoke("atlas.example.counter", "increment", {"amount": 5})
    assert result == 5

    # Increment again
    result = runtime.invoke("atlas.example.counter", "increment", {"amount": 3})
    assert result == 8

    # Reset
    result = runtime.invoke("atlas.example.counter", "reset")
    assert result == 0
```

### Running it

```bash
# Run tests
atlas test

# Run the worker
atlas run
```

---

## Best Practices

1. **One responsibility per Worker.** If your Worker has roles `[app, database, translator, ai]`, it's a monolith. Break it apart.
2. **Program against Models, not implementations.** Depend on `LoggerModel`, not `ConsoleLoggerWorker`. This lets anyone swap the implementation without touching your code.
3. **Use lifecycle hooks.** Don't put setup logic in `__init__`. Use `on_init()` for state setup, `on_start()` for connections, and `on_stop()` for cleanup.
4. **Keep your manifest in sync.** The `id`, `name`, `version`, and `roles` in `atlas.yaml` must match the class attributes in `worker.py`.
5. **Test with MockRuntime.** Never boot the full Atlas Runtime for unit tests. Use `MockRuntime()` for fast, isolated testing.
6. **Export meaningful capabilities.** Don't export `my.worker.do_stuff`. Be specific: `atlas.example.counter.increment`.

---

## What's Next?

- **Build an Application**: See [Building Managers](managers.md) to compose multiple workers together.
- **Define Contracts**: See [Building Models](models.md) to define abstract interfaces.
- **Translate Formats**: See [Building Adapters](adapters.md) to convert data types.
- **Explore the SDK**: See [SDK Primitives](sdk-primitives.md) for the complete API reference.
