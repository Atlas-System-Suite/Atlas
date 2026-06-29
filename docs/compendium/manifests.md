# The Atlas Manifest (`atlas.yaml`)

> The complete reference guide to the declarative heart of every Atlas artifact.

Every Worker, Model, Adapter, and Manager in Atlas requires a `atlas.yaml` manifest. This file acts as the **identity card** for the artifact. It tells the Atlas Runtime exactly what the artifact is, what it needs, and what it provides.

---

## Anatomy of a Worker Manifest

Below is a complete example of a Worker manifest. 

```yaml
kind: worker
id: atlas.core.logger
name: ConsoleLoggerWorker
version: 1.0.0
description: Core logging facility for Atlas.
language: python
roles: [worker, core, stdlib]

execution:
  policy: singleton

communication:
  transports: [memory]
  formats: [python]
  default_format: python

imports:
  - capability: atlas.core.storage
    version: ">=1.0.0"

exports:
  - capability: atlas.core.logger
    version: 1.0.0
    precedence: 100

translations: []
```

---

## Top-Level Identity Fields

| Field | Description | Rules |
|---|---|---|
| `kind` | The artifact type. | Must be `worker`, `model`, `adapter`, or `manager`. |
| `id` | The globally unique identifier. | Must follow `namespace.name` convention (e.g. `acme.payments`). |
| `name` | Human-readable display name. | Usually matches the Python class name. |
| `version` | Semantic version string. | Must follow SemVer (e.g. `1.0.0`). |
| `description` | Short explanation of what it does. | Optional. |
| `language` | The implementation language. | Currently `python` is the only supported value. |
| `roles` | Metadata tags for grouping and tooling. | See [Roles Guide](workers.md#roles). |

??? info "Deep Dive: Why do we need an ID *and* a Name?"
    The `id` (e.g. `atlas.core.logger`) is used by the **Capability Resolver** during routing. It must be universally unique so there are no collisions when sharing Workers on the Atlas Marketplace. 
    
    The `name` (e.g. `ConsoleLoggerWorker`) is used for logging, UI display in Atlas Studio, and to match the implementation class in the source code.

---

## Execution Policy

The `execution.policy` field tells the Runtime how to manage instances of this Worker.

```yaml
execution:
  policy: singleton
```

| Policy | Behavior | Best For |
|---|---|---|
| `singleton` | Only one instance is created. All invocations route to it. | Loggers, database connections, UI. |
| `pool` | A pool of instances is maintained. | CPU-heavy tasks, rate-limited APIs. |
| `on_demand` | A new instance is created per invocation, then destroyed. | Stateless processing, simple calculations. |

??? abstract "Under the Hood: The Singleton Pattern"
    When `policy: singleton` is specified, the **WorkerManager** instantiates the Python class exactly once during boot. This instance is held in the `GlobalRegistry`. The `InvocationEngine` will route every request to this specific object instance in memory. If the Worker holds state (like a `self.counter`), that state will persist across all invocations.

---

## Communication

The communication block defines how this Worker expects to receive data.

```yaml
communication:
  transports: [memory, tcp]
  formats: [python, json]
  default_format: python
```

| Field | Description | Supported Values |
|---|---|---|
| `transports` | How data is physically moved. | `memory` (direct RAM), `tcp`, `grpc`. |
| `formats` | How data is serialized. | `python` (objects), `json`, `msgpack`. |
| `default_format` | The fallback format. | Usually `python` for local Workers. |

??? quote "Architecture Note: Why specify formats?"
    In Phase 1 of Atlas, everything runs locally using the `memory` transport and `python` objects, so this block might seem redundant. However, Atlas is designed for distributed computing. By forcing you to declare `formats: [json]` now, Atlas guarantees that in Phase 2, this Worker can be seamlessly moved to a different server without rewriting any code.

---

## Imports and Exports (The Capability Graph)

This is the most important part of the manifest. It defines the edges in the Atlas dependency graph.

### `exports`

Capabilities that this Worker provides to the ecosystem.

```yaml
exports:
  - capability: atlas.core.logger
    version: 1.0.0
    precedence: 100
```

- **`capability`**: The globally unique string identifying what this does.
- **`version`**: The specific version of the capability exported.
- **`precedence`**: (Optional) If two Workers export the exact same capability, the Runtime routes to the one with the higher precedence. Default is `0`.

### `imports`

Capabilities that this Worker **requires** to function.

```yaml
imports:
  - capability: atlas.core.storage
    version: ">=1.0.0"
```

If the Runtime cannot find a Worker exporting `atlas.core.storage` that satisfies the `version` constraint, it will refuse to boot your Worker and fail fast with a `ResolutionError`.

??? danger "Warning: Circular Dependencies"
    Atlas uses a directed acyclic graph (DAG) for capability resolution. If Worker A imports Worker B, and Worker B imports Worker A, the Runtime will detect the cycle during the `ExecutionPlanner` phase and crash the boot sequence. To fix this, extract the shared logic into Worker C, and have both A and B import C.

---

## Translations (Adapters Only)

If `kind: adapter`, the manifest must include a `translations` block instead of `exports`.

```yaml
translations:
  - source_format: json
    target_format: msgpack
    cost: 1
```

See the [Building Adapters](adapters.md) guide for more details on how the `TranslationResolver` uses this data to find multi-hop format conversions.
