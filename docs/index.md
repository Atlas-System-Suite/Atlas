# Welcome to Atlas

Atlas is a **framework** for building Personal Operating Systems.

It provides a modular, provider-based architecture that separates business logic from infrastructure, allowing applications to evolve without massive rewrites.

## Key Concepts

- **Modules:** Contain the business logic (e.g., Health, Finance).
- **Capabilities:** Abstract runtime service identities (e.g., "storage", "ai").
- **Protocols:** The code contracts for Capabilities.
- **Providers:** The concrete implementations of Protocols.

## Getting Started

Please see the [Architecture](architecture.md) guide to understand how these pieces fit together.
