# Atlas

> **Atlas is a modular framework for building Personal Operating Systems.**

LifeOS is the first implementation built using Atlas.

## Fun Fact

During Atlas' design, the Model system almost had a very different name.

For roughly one design session it was internally called **Hookers**, because they "hooked" Workers to standardized behavior.

That idea survived exactly until someone pointed out what "hooker" usually means in English.

The name was immediately retired.

Models were born.

The joke, however, became part of Atlas history.

---

# What is Atlas?

Atlas is not a productivity app.
Atlas is not a habit tracker.
Atlas is not a Google Sheets template.

Atlas is a framework that allows developers to build highly customizable personal operating systems.

An Atlas implementation can help users manage their health, finances, learning, projects, schedules, and personal knowledge while remaining completely modular and extensible.

---

# Philosophy

Atlas follows a few core principles:

* **Atlas coordinates. Workers own.**
* **Atlas owns execution. Workers own business state.**
* **Atlas owns lifecycle. Workers own communication.**
* **Atlas owns discovery. Workers own persistence.**
* The Runtime should be as small as possible. Workers should be as smart as possible.
* Favor tooling (Solon) over runtime magic.
* Favor metadata over runtime logic.

---

# Core Concepts

## Workers
**Worker** is the ONLY executable primitive in Atlas. There is no architectural distinction between an "application", a "provider", or a "module". A Worker can be a database, a UI widget, an AI integration, or a full dashboard.

## Models
**Models** are the ideal, tool-independent specifications that Workers implement. Models are declarative blueprints that define what interfaces, schemas, and capabilities a Worker should provide or consume.

## Solon
**Solon** is the developer toolchain. It consumes Models to validate Workers, generate tests, and scaffold SDKs. Solon guarantees consistency without bloating the Runtime.

## Atlas Core (The Control Plane)
The Runtime that powers the framework. It handles Discovery, Lifecycle Management, and Session Binding. It explicitly does **not** route messages or store data.

## Roles
Metadata tags attached to Workers. Roles are consumed by tooling (Solon) and documentation, but they **do not change runtime execution**. Atlas treats all Workers equally. 

Some predefined roles include:
- `manager`: Orchestrates other Workers (e.g., LifeOS, StudentOS).
- `database`: Provides persistent data storage (e.g., SQLite, Postgres).
- `storage`: Provides object or file storage.
- `ai`: Provides language model or inference capabilities.
- `widget`: Primarily focused on exporting UI capabilities.
- `network`: Handles external communication (e.g., HTTP clients, webhooks).

---

# Repository Structure

`/specs`
Engineering specifications. The absolute source of truth for the architecture.

`/docs`
Architectural deep-dives, historical context, and MKDocs site files.

`/src`
The implementation codebase (Control Plane, Solon Toolchain, etc.).

---

# Current Goal

Validate the Atlas Architecture by building the Control Plane (Core).

Once Atlas Core is stable, build LifeOS as the reference Manager Worker.

---

# Development Philosophy

Architecture First.

Implementation Second.

Optimization Last.

Every implementation should be derived from the specifications contained inside `/specs`.

Never implement features before they are architecturally defined.

---

# Long-Term Vision

Atlas should eventually support:

* Local desktop applications
* Web applications
* Mobile applications
* Self-hosted deployments
* Managed cloud deployments
* Multiple storage providers
* Multiple AI providers
* Third-party extensions
* Community marketplaces

---

# License

TBD
