# Atlas Primitives 🧩

Welcome to the definitive guide to Atlas Primitives. 

Atlas enforces a strict, modular architecture. Everything in the ecosystem is built using these foundational blocks. If it isn't one of these, it doesn't exist to the runtime.

---

## 1. Workers

> **The execution engines of Atlas.**

Workers are the fundamental, undeniable unit of execution in Atlas. **They are the ONLY things that contain business logic.** If code is running, it is running inside a Worker.

* **Identity:** Every Worker has a unique `id` (e.g., `atlas.core.storage`).
* **Isolation:** Workers do not share memory or state directly. They communicate exclusively by sending Invocations over Sessions.
* **Declarative:** Workers are declared via a `manifest.yaml` (or `atlas.yaml`) file that defines their imports, exports, roles, and communication protocols.

### Rules of Workers:
- A Worker should do one thing and do it well.
- A Worker must never import another Worker's code directly (`from my_other_worker import ...` is strictly forbidden).
- A Worker owns its internal state and persistence.

---

## 2. Managers

> **The orchestrators and conductors.**

A Manager is an application boundary. It does not execute business logic. Instead, a Manager's sole responsibility is to define **which Workers** are needed to run an application, and to provide **configuration** for them.

* **Composition:** Managers compose Workers together using the `ManagerBuilder`.
* **Configuration:** Managers inject global state (like environment variables, API keys, or ports) into the runtime environment via the `ConfigModel`.
* **Output:** A Manager script compiles into a single, declarative `atlas.yaml` manifest that the Atlas Runtime can boot.

### Rules of Managers:
- A Manager must NEVER contain `if/else` business logic relating to the application's domain.
- A Manager's execution ends the moment the `atlas.yaml` file is generated or the runtime boots.

---

## 3. Models

> **The contracts and blueprints.**

Models are language-agnostic contracts. They define *what* a Worker does, without caring *how* it does it. 

Think of Models as the USB-C ports of Atlas. If a Worker implements the `StorageModel`, Atlas knows exactly how to talk to it, regardless of whether that Worker uses SQLite, PostgreSQL, or an AWS S3 bucket under the hood.

* **Interfaces:** Models define expected capabilities (e.g., `write(key, data)`, `read(key)`).
* **Tooling:** Solon (the Atlas build system) uses Models to auto-generate SDKs, documentation, and mock implementations for testing.
* **Decoupling:** Workers should always program against a Model, never a concrete implementation.

### Rules of Models:
- Models must be completely declarative (abstract base classes in Python).
- Models must never contain implementation details.

---

## 4. Adapters (Translators)

> **The universal translators.**

What happens if a Python Worker wants to talk to a Rust Worker, but they don't speak the same data format? You use an Adapter.

Adapters are a specialized type of Worker. They do not export capabilities or maintain state. Their only job is to provide `translations` (e.g., converting a Python dictionary to a JSON payload, or JSON to MessagePack).

* **Stateless:** Adapters must be entirely stateless.
* **Invisible:** The Atlas Runtime automatically discovers Adapters and inserts them into the communication pipeline when two Workers cannot natively understand each other.

### Rules of Adapters:
- Adapters must declare a `source_format`, a `target_format`, and a `cost` in their manifest.
- Adapters must never mutate the semantic meaning of the data—only its format.

---

## 5. Roles

> **The metadata tags.**

Roles are tags defined in a Worker's manifest (e.g., `roles: [database, storage]`). 

**Roles do not change how the Atlas Runtime executes the Worker.** The Runtime treats all Workers equally. 

However, Roles fundamentally change how the **Ecosystem** (like Atlas Studio, Miron, and Varsity) treats the Worker.

### Common Roles:

- `[app]`: A frontend or UI application. Usually consumes capabilities but rarely exports them.
- `[database]`: A worker that persists data.
- `[translator]`: An adapter that converts data formats.
- `[telemetry]`: An observer that binds to Rooms to monitor traffic, but is structurally forbidden from modifying state.
- `[cli]`: A worker that handles command-line interface routing.

### Rules of Roles:
- A Worker should have a narrow, focused set of Roles. If a Worker has 10 roles, it is a monolith and should be broken apart.
