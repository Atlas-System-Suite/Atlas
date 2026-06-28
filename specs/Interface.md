# Interfaces

Status: Draft

Version: 0.1

---

# Purpose

Interfaces define the **code contracts** that Atlas components must implement.

In Atlas, Interfaces are implemented as Python `typing.Protocol` classes (structural subtyping).

They provide consistency across the platform.

Interfaces are implementation-independent.

For concrete Protocol definitions, see Protocols.md.

## Relationship to Capabilities

Interfaces (Protocols) are the code contracts. Capabilities are runtime service identities.

A Capability references one or more Protocols. A Provider satisfies Protocols and registers for Capabilities.

See ADR-002 for the rationale behind this separation.

---

# Philosophy

Atlas depends on Protocols.

Not implementations.

Every interchangeable component should satisfy a Protocol.

---

# Standard Interfaces

Storage Interface

AI Interface

Provider Interface

Module Interface

Widget Interface

Application Interface

Notification Interface

Authentication Interface

Search Interface

Backup Interface

Configuration Interface

---

# Interface Design Principles

Interfaces should:

* Be minimal
* Be stable
* Be versioned
* Be extensible
* Avoid implementation details

---

# Versioning

Every Interface has:

Name

Version

Compatibility

Deprecation Status

Breaking changes require a new major version.

---

# Implementation Rules

Every implementation must:

Satisfy the Interface.

Reject unsupported operations clearly.

Document optional functionality.

Avoid extending Interfaces privately.

---

# Discovery

The Runtime discovers Interfaces during startup.

Providers declare which Interfaces they implement.

Modules declare which Interfaces they require.

---

# Compatibility

An implementation is compatible if:

Interface Version is supported.

Capability matches.

Runtime Version is compatible.

Application Version is compatible.

---

# Validation

Atlas validates:

Required methods

Required metadata

Version compatibility

Configuration

Permissions

before initialization.

---

# Evolution

Interfaces should evolve through:

Minor versions

↓

Backward compatibility

↓

Major versions only when necessary.

---

# Design Rules

Interfaces must:

* Never contain business logic.
* Never depend on Providers.
* Never depend on Modules.
* Remain technology agnostic.

---

# Examples

Storage Interface

Implemented by:

SQLite

PostgreSQL

Google Sheets

Atlas Cloud

Notification Interface

Implemented by:

Discord

Slack

Email

Push

SMS

---

# Future

Support:

Interface inheritance

Capability-specific extensions

Optional Interface features

Automatic compatibility checking
