# Atlas Explained

> This document is the first thing a new contributor should read.
>
> Before reading 20 spec files, read this.

---

## What is Atlas?

Atlas is a **framework** for building Personal Operating Systems.

It is not an app. It is not a template. It is the engine behind apps.

LifeOS is the first application built on Atlas. Others can follow without changing Atlas Core.

---

## The Big Picture

```
Application (LifeOS, StudentOS)
    ↓ assembles
Modules (Health, Finance, Journal)
    ↓ consume
Capabilities (Storage, AI, Notifications)
    ↓ resolved through
Protocols (StorageProtocol, AIProtocol)
    ↑ satisfied by
Providers (SQLite, Gemini, Console)
    ↓ talk to
External Systems (databases, APIs, services)
```

That's it. That's the whole architecture.

Everything else is details about how these six layers interact.

---

## Why Capabilities Exist

Without Capabilities:

```
Health Module → SQLite
Finance Module → SQLite
Journal Module → SQLite
```

Every Module is hardcoded to SQLite. Want to switch to PostgreSQL? Change every Module.

With Capabilities:

```
Health Module → Storage Capability → (SQLite | PostgreSQL | Google Sheets)
```

Modules never know which storage they use. The Runtime decides. Modules just ask for "storage."

---

## Why Protocols Exist

A Capability says *what* service exists ("storage").

A Protocol says *how* to talk to it (the actual Python methods).

```python
class StorageProtocol(Protocol):
    async def create(self, entity_type: str, data: dict) -> str: ...
    async def read(self, entity_type: str, id: str) -> dict | None: ...
    async def update(self, entity_type: str, id: str, data: dict) -> bool: ...
    async def delete(self, entity_type: str, id: str) -> bool: ...
```

Any Provider that satisfies this shape can be used. No base class needed. No inheritance. Just match the shape.

This is structural subtyping — Python's `typing.Protocol`.

---

## Why Providers Exist

Providers are the only components that know about external systems.

```
SQLiteProvider knows about SQLite.
GeminiProvider knows about the Gemini API.
ConsoleNotificationProvider knows about stdout.
```

Everything else in Atlas is ignorant of infrastructure. That's the point.

Swapping SQLite for PostgreSQL means replacing one Provider. Zero Module changes.

---

## Why the Runtime Owns the Registry

The Runtime is the only component that can see everything.

```
Runtime
├── knows all Modules
├── knows all Providers
├── knows all Capabilities
├── manages all lifecycles
└── dispatches all Events
```

No Module can see another Module directly. No Provider can see a Module. The Runtime mediates everything through the Registry and Event Bus.

This isolation is what makes Atlas modular.

---

## Why Core Has No Framework

Atlas Core does not embed FastAPI, Django, or any web framework.

Because Atlas is not a web app.

Atlas is an engine. Applications decide their own surface:

* CLI apps use Typer or Click.
* Web apps use FastAPI or Django.
* Desktop apps use Tauri.
* Mobile apps use whatever mobile frameworks exist.

If Core embedded FastAPI, a CLI application would have FastAPI as a dependency for no reason.

---

## Why Storage is a Capability

Storage seems fundamental. Why not bake it into Core?

Because "where data lives" is an infrastructure decision, not a framework decision.

* During development → SQLite file
* In production → PostgreSQL
* For a spreadsheet user → Google Sheets
* In the cloud → Atlas Cloud

The framework shouldn't care. The user's configuration decides.

---

## Why SQLite is First

SQLite is the simplest storage provider that proves the full architecture:

```
Module → Capability → Protocol → Provider → Database → Disk
```

If this chain works with SQLite, it works with anything.

Build the simplest thing that validates the pattern. Then move on.

---

## Why Events Instead of Direct Calls

Without Events:

```
Health Module → Dashboard Module
Health Module → Analytics Module
Health Module → Achievements Module
Health Module → AI Module
```

Health knows about four other Modules. Change any of them? Might break Health.

With Events:

```
Health Module → publishes "Health.WorkoutCompleted"

Dashboard Module → subscribes ← reacts independently
Analytics Module → subscribes ← reacts independently
Achievements Module → subscribes ← reacts independently
AI Module → subscribes ← reacts independently
```

Health doesn't know subscribers exist. Subscribers don't know who published. Zero coupling.

---

## Why Hybrid Async

Atlas talks to databases, AI APIs, and notification services. All I/O.

Synchronous I/O means waiting. Async I/O means doing useful work while waiting.

But pure async forces every consumer to write `async/await`. That's friction for simple scripts.

So: async internally, sync wrappers for convenience. Best of both worlds.

---

## Common Misconceptions

### "Atlas is a productivity app"

No. Atlas is a framework. LifeOS is an app built with Atlas.

### "Modules can talk to each other"

Not directly. Modules communicate through Events and Capabilities only.

### "Core contains business logic"

Never. Core coordinates. Modules contain business logic. Providers contain infrastructure logic.

### "You need all Providers to run Atlas"

No. You need exactly one Storage Provider. Everything else is optional.

### "Atlas requires AI"

No. AI is a Capability. If no AI Provider is configured, Modules that request AI gracefully degrade.

### "Atlas is a web app"

No. Atlas Core has no web framework. Applications choose their own surface.

---

## Reading Order for Contributors

1. This document (you're here)
2. `specs/Architecture.md` — Layer model
3. `specs/Protocols.md` — Interface shapes
4. `specs/Technology.md` — Stack decisions
5. `specs/adr/` — Why decisions were made
6. `specs/Core.md` → `Runtime.md` → `Events.md` — Core internals
7. `specs/Capabilities.md` → `Providers.md` → `Modules.md` — Extension model
8. `specs/engineering/` — Coding standards
9. `AGENTS.md` — Rules for AI agents
