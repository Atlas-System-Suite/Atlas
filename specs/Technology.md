# Technology

Status: Approved

Version: 0.1

---

# Purpose

This document records the concrete technology decisions for Atlas.

All implementation must conform to these choices.

Changes to technology choices require an ADR.

---

# Language

Python 3.13+

Atlas is implemented entirely in Python.

Rationale:

* Rich ecosystem for data processing, AI, and automation.
* Strong typing support through Protocols and type hints.
* Async/await support for I/O-bound operations.
* Large developer community.
* Mature package ecosystem.

---

# Runtime Model

Hybrid Async.

The Atlas Runtime uses async/await internally.

All Core Protocols define async methods.

Sync convenience wrappers are provided for contexts that do not require async.

Rules:

* Core components use `async def` for all I/O-bound operations.
* Sync wrappers use `asyncio.run()` at the boundary only.
* Never call `asyncio.run()` from within an async context.
* Event Bus delivery is async.
* Module lifecycle hooks are async.
* Provider operations are async.

---

# Package Manager

To be decided.

The repository currently uses `uv.lock`, suggesting `uv` as a candidate.

This decision will be formalized in a future ADR.

---

# Type Checking

BasedPyright.

All public APIs must pass strict type checking.

---

# Linting and Formatting

Ruff (Linter)

Ruff Format (Formatter)

---

# Testing

pytest.

Rationale:

* Industry standard for Python testing.
* Rich plugin ecosystem.
* Fixture-based dependency injection.
* Async test support via pytest-asyncio.

---

# Interfaces

Python Protocols (typing.Protocol).

Atlas uses structural subtyping rather than nominal inheritance.

Rationale:

* No coupling between interface definition and implementation.
* Supports duck typing with static verification.
* Enables third-party implementations without importing Atlas base classes.

---

# Configuration Format

YAML.

Atlas configuration files use YAML syntax.

Rationale:

* Human-readable.
* Supports complex nested structures.
* Widely understood.
* Good library support (PyYAML, ruamel.yaml).

---

# Web Framework

None.

Atlas Core is a library, not a web application.

Applications built on Atlas choose their own surface:

* CLI
* FastAPI
* Django
* Desktop (Tauri, Electron)
* Mobile

Atlas Core must remain framework-agnostic.

---

# Database

SQLite is the default Storage Provider.

Additional providers (PostgreSQL, Google Sheets, etc.) are optional.

Atlas Core never depends on a specific database technology.

---

# Serialization

To be decided.

Candidates:

* Pydantic (validation + serialization)
* msgspec (performance)
* dataclasses + manual validation

This decision will be formalized during Phase 1 implementation.

---

# Key Dependencies

The following are expected core dependencies:

* PyYAML or ruamel.yaml (configuration)
* aiosqlite (async SQLite)
* pytest + pytest-asyncio (testing)
* ruff (linting/formatting)
* basedpyright (type checking)

Additional dependencies will be introduced per Provider and documented in their manifests.

---

# Design Rules

Technology choices should:

* Prefer standard library when sufficient.
* Minimize external dependencies in Core.
* Avoid framework lock-in.
* Support the hybrid async model.
* Remain replaceable where practical.
