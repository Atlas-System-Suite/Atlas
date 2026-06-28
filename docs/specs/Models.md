# Models

> Every project accumulates a few stories.
>
> During Atlas' design, Models were briefly called "Hookers" because they connected Workers to standardized behaviour.
>
> The idea lasted approximately one conversation before everyone realized introducing Atlas with "Workers implement Hookers" was probably not ideal.
>
> The name was retired.
>
> Models are now the authoritative specification Workers implement.
>
> The joke remains part of Atlas lore.

<details>
<summary>The Lore</summary>
The term was initially coined because the framework needed a way to "hook" standalone code into a larger operating system context. The engineering team jokingly referred to the declarative rulesets as "Hookers". It was dropped instantly once the marketing implications were discussed, but the "Hooker" naming survives as an internal easter egg.
</details>

---

## What is a Model?

A **Model** is the ideal, tool-independent specification that Workers implement. 

Models are **NOT** executable. They are declarative definitions. Multiple tools must be able to consume Models (e.g., Solon, Atlas Studio, the Runtime).

### The Two Types of Models

Atlas strictly separates behavior from data. Therefore, there are two distinct types of Models:

#### 1. Capability Models (Verbs)
Capability Models define **what something can do**. They are behavioral contracts.
*Example:* `atlas.storage` defines the ability to write and read bytes. It expects methods like `write(key, data)`. 

#### 2. Resource Models (Nouns)
Resource Models define **what something is**. They are structural data contracts.
*Example:* `atlas.resource.image` defines the standard schema for an Image (width, height, channels, raw bytes). 

This distinction is crucial for the **Translation Layer**. By standardizing the data structures (Resource Models) flowing between Workers, Translators do not need to guess how to map an `Image` object between a Python Worker and a Rust Worker—they simply translate the canonical `atlas.resource.image` schema.

---

## Model Metadata Specification

Every Model (Capability or Resource) is defined by a standard metadata schema. This schema is language-agnostic and acts as the source of truth for Solon generation and Runtime validation.

```yaml
kind: model
id: atlas.storage
version: 1.0.0
description: Standard storage contract for persisting raw bytes.

# For Capability Models: What actions can be invoked?
capabilities:
  write:
    description: "Write bytes to a key."
    inputs:
      key: string
      data: bytes
    returns: boolean
  read:
    description: "Read bytes from a key."
    inputs:
      key: string
    returns: bytes

# What asynchronous events are published?
events:
  written:
    description: "Fired when data is written."
    schema:
      key: string
      size: integer

# What specific domain errors can occur?
errors:
  StorageFullError: "The underlying storage medium is exhausted."
  PermissionDeniedError: "Worker lacks filesystem permissions."

# What global configuration does this Model require?
configuration:
  STORAGE_ROOT_PATH:
    type: string
    required: true

# For Resource Models: What is the canonical data shape?
schema: null # (Used in Resource Models like atlas.resource.image)
```

## Runtime & Worker Integration

### Worker Integration
Workers explicitly declare the Models they implement in their manifest.

```yaml
kind: worker
id: my.sqlite.worker
implements:
  - atlas.storage@1.x
```
Because the Worker implements a standard Model, it is completely replaceable. Managers can swap it out for a `my.postgres.worker` without changing any application logic.

### Runtime Integration
The Atlas Runtime uses Models for:
- **Capability discovery:** Finding Providers that implement the requested Model.
- **Translation negotiation:** Using Resource Models to map data structures between languages.
- **Session establishment:** Ensuring the Requester and Provider agree on the semantic contract.

## The Rule of Ownership
- **Workers implement Models.**
- **Workers NEVER own Models.**

Models exist independently of any implementation. This allows the Solon developer toolchain to validate any Worker against a Model without executing the Worker itself.

## Model Versioning Policy

Because Models are contracts between independent Workers, they must be strictly versioned using Semantic Versioning (e.g., `v1.0.0`).

### Compatibility Rules
- **Minor Version Bumps (e.g., `v1.0` -> `v1.1`):** Indicate backward-compatible additions (e.g., a new optional capability or event). A Worker requiring `v1.0` can safely bind to a Provider exporting `v1.1`.
- **Major Version Bumps (e.g., `v1.0` -> `v2.0`):** Indicate breaking changes to the contract (e.g., changing input schemas, dropping a capability). A Worker requiring `v1.0` **will not bind** to a Provider exporting `v2.0` unless a backward-compatibility Adapter (Translator) is explicitly declared.

If a Standard Model evolves and introduces a breaking change, ecosystem stability is preserved because the Runtime enforces these strict version boundaries during Binding negotiation.
