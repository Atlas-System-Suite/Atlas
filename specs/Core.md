# Atlas Core

Atlas Core is the framework kernel.

Core owns exactly one thing: **Execution Orchestration**.

## Responsibilities

Core is strictly limited to:
- **Discovery:** Finding installed Workers and Models.
- **Worker Registry:** Maintaining in-memory metadata about loaded Workers, exported Capabilities, and Roles.
- **Resolution:** Matching requests for Capabilities to exported Capabilities from other Workers.
- **Permission Negotiation:** Validating that a Worker is allowed to access the requested Capability.
- **Session Establishment:** Creating the binding between the importing Worker and exporting Worker.
- **Lifecycle:** Booting up Workers, managing their lifecycle states, and tearing them down gracefully.

## Anti-Responsibilities

Core **MUST NOT**:
- Store persistent data.
- Execute business logic or domain rules.
- Route Data Plane messages (Events are routed directly between bound Workers).
- Implement specific Capabilities.

Core is entirely Platform Agnostic, meaning it does not care if a Worker is a database, an AI model, or a UI widget. It treats all Workers identically.
