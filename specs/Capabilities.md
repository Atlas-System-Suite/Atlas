# Capabilities

Status: Draft

Version: 0.1

---

# Purpose

Capabilities define **what Atlas can do**.

A Capability is a **runtime service identity** — a named, versioned service that the Capability Registry discovers, resolves, and injects.

Capabilities are not code contracts. Code contracts are defined by Protocols (see Protocols.md).

Capabilities are not implementations. Implementations are provided by Providers (see Providers.md).

## Relationship to Protocols and Providers

Capability (runtime service identity) → references → Protocol (code contract)

Provider (implementation) → satisfies → Protocol

Provider → registers for → Capability

See ADR-002 for the rationale behind this separation.

Modules consume Capabilities.

---

# Philosophy

Atlas Core never asks for a Provider.

It asks for a Capability.

Example

Health Module

↓

Storage Capability

↓

SQLite Provider

or

↓

Google Sheets Provider

The Health Module never knows which one is used.

---

# Relationship

Capability

↓

Implemented By

↓

Provider

↓

Consumed By

↓

Module

---

# Standard Capabilities

Storage

Artificial Intelligence

Authentication

Notifications

Search

Calendar

Backup

Synchronization

Analytics

Configuration

Logging

Scheduling

Permissions

Future Capabilities may be introduced without changing Atlas Core.

---

# Capability Lifecycle

Every Capability:

* Registers itself
* Declares its Interface
* Accepts compatible Providers
* Exposes functionality to Modules

---

# Capability Registry

Atlas Runtime maintains a Capability Registry.

The Registry stores:

Capability Name

Supported Interface Version

Active Provider

Available Providers

Status

Modules query the Registry instead of Providers.

---

# Resolution

When a Module requests a Capability:

1. Runtime checks Registry.
2. Finds compatible Provider.
3. Returns Provider instance.
4. Module interacts only with the Interface.

---

# Fallback

If multiple Providers support a Capability:

Runtime should select based on:

* User Preference
* Application Configuration
* Priority
* Availability

---

# Design Rules

Capabilities:

* Define behavior only.
* Never contain implementation.
* Must remain stable.
* Should evolve through versioning.
* Should avoid provider-specific concepts.

---

# Examples

Storage Capability

Implemented by:

SQLite

PostgreSQL

Google Sheets

Atlas Cloud

AI Capability

Implemented by:

Gemini

Claude

OpenAI

Ollama

DeepSeek

---

# Future

Support:

Capability discovery

Capability version negotiation

Capability priorities

Capability composition

Multiple active providers
