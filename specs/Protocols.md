# Protocols

Status: Draft

Version: 0.1

---

# Purpose

This document defines the core Protocol interfaces for Atlas.

Protocols are the code contracts that Providers and Modules must satisfy.

All Protocols use Python's `typing.Protocol` for structural subtyping.

---

# Relationship

Capability — A runtime service identity. Discovered, resolved, and injected by the Registry.

Protocol — The code contract that implementations must satisfy. Defined in this document.

Provider — A concrete implementation of one or more Protocols, registered for a Capability.

```
Capability (service identity)
    ↓ references
Protocol (code contract)
    ↑ satisfies
Provider (implementation)
```

---

# Design Principles

Protocols should:

* Use `async def` for all I/O-bound methods.
* Be minimal — define only the required surface.
* Be versioned.
* Be independent of any Provider.
* Be independently testable.

---

# Core Protocols

## LifecycleProtocol

Defines how any managed component transitions through lifecycle states.

```
LifecycleProtocol:
    async initialize() -> None
    async start() -> None
    async stop() -> None
    async dispose() -> None
    state: LifecycleState  (property)
```

LifecycleState is an enum:

Registered, Initialized, Started, Running, Paused, Stopped, Disposed, Error.

---

## ModuleProtocol

Defines the contract every Module must satisfy.

Extends LifecycleProtocol.

```
ModuleProtocol(LifecycleProtocol):
    id: str                    (property — globally unique identifier)
    name: str                  (property — human-readable name)
    version: str               (property — semantic version)
    manifest: ModuleManifest   (property — parsed manifest)

    async on_event(event: Event) -> None
    get_required_capabilities() -> list[str]
    get_published_events() -> list[str]
    get_subscribed_events() -> list[str]
```

---

## ProviderProtocol

Defines the contract every Provider must satisfy.

Extends LifecycleProtocol.

```
ProviderProtocol(LifecycleProtocol):
    id: str                      (property — globally unique identifier)
    name: str                    (property — human-readable name)
    version: str                 (property — semantic version)
    manifest: ProviderManifest   (property — parsed manifest)

    get_supported_capabilities() -> list[str]
    async validate_configuration(config: dict) -> bool
    async health_check() -> HealthStatus
```

HealthStatus: Healthy, Degraded, Unhealthy.

---

## EventBusProtocol

Defines the contract for event publishing and subscription.

```
EventBusProtocol:
    async publish(event: Event) -> None
    subscribe(event_name: str, handler: EventHandler) -> SubscriptionId
    unsubscribe(subscription_id: SubscriptionId) -> None
    async publish_and_wait(event: Event) -> list[Any]
```

EventHandler is a callable: `async (Event) -> None`

---

## Event

Defines the structure of an Atlas Event.

```
Event:
    id: str            (globally unique)
    name: str          (Domain.Action format)
    timestamp: datetime
    source: str        (component ID that published)
    payload: dict      (immutable event data)
    metadata: dict     (optional metadata)
    version: str       (event schema version)
```

---

## RegistryProtocol

Defines the contract for component discovery and lookup.

```
RegistryProtocol:
    register_module(module: ModuleProtocol) -> None
    register_provider(provider: ProviderProtocol) -> None
    register_capability(name: str, protocol_version: str) -> None

    get_module(module_id: str) -> ModuleProtocol | None
    get_provider(provider_id: str) -> ProviderProtocol | None
    get_modules() -> list[ModuleProtocol]
    get_providers() -> list[ProviderProtocol]

    has_module(module_id: str) -> bool
    has_provider(provider_id: str) -> bool
    has_capability(name: str) -> bool
```

---

## CapabilityRegistryProtocol

Defines the contract for Capability resolution.

Manages the binding between Capabilities and their Provider implementations.

```
CapabilityRegistryProtocol:
    register(capability_name: str, provider: ProviderProtocol) -> None
    resolve[T](capability_name: str) -> T
    resolve_optional[T](capability_name: str) -> T | None
    get_providers_for(capability_name: str) -> list[ProviderProtocol]
    is_available(capability_name: str) -> bool
    set_preferred_provider(capability_name: str, provider_id: str) -> None
```

---

## ConfigurationProtocol

Defines the contract for configuration access.

```
ConfigurationProtocol:
    get[T](key: str, default: T | None = None) -> T
    get_section(section: str) -> dict
    has(key: str) -> bool
    get_all() -> dict
    validate() -> list[ValidationError]
```

Configuration is read-only after boot.

Future versions may support live reload through Events.

---

## LoggerProtocol

Defines the contract for logging.

```
LoggerProtocol:
    debug(message: str, **context) -> None
    info(message: str, **context) -> None
    warning(message: str, **context) -> None
    error(message: str, **context) -> None
    critical(message: str, **context) -> None
    child(name: str) -> LoggerProtocol
```

The `child()` method creates a scoped logger (e.g., `atlas.runtime.lifecycle`).

Context kwargs are included as structured log data.

---

# Capability Protocols

## StorageProtocol

Defines the contract for persistent data access.

```
StorageProtocol:
    async create(entity_type: str, data: dict) -> str       (returns ID)
    async read(entity_type: str, id: str) -> dict | None
    async update(entity_type: str, id: str, data: dict) -> bool
    async delete(entity_type: str, id: str) -> bool
    async query(entity_type: str, filters: dict | None = None, 
                order_by: str | None = None, 
                limit: int | None = None,
                offset: int | None = None) -> list[dict]
    async count(entity_type: str, filters: dict | None = None) -> int

    # Optional capabilities
    async begin_transaction() -> TransactionContext
    async execute_batch(operations: list[BatchOperation]) -> list[Any]
```

TransactionContext is an async context manager.

Providers that do not support transactions must raise `StorageError` with a clear message.

---

## AIProtocol

Defines the contract for AI capabilities.

```
AIProtocol:
    async generate(request: AIRequest) -> AIResponse
    async generate_stream(request: AIRequest) -> AsyncIterator[str]
    get_supported_capabilities() -> list[str]    (e.g., ["planning", "summarization", "classification"])
    get_model_info() -> ModelInfo
```

```
AIRequest:
    capability: str          (e.g., "summarization", "classification")
    prompt: str
    context: dict            (structured context data)
    constraints: dict        (e.g., max_tokens, temperature)
    expected_format: str     (e.g., "text", "json", "markdown")

AIResponse:
    output: str
    confidence: float | None
    provider_metadata: dict
    processing_time_ms: int
    model: str
```

---

## NotificationProtocol

Defines the contract for sending notifications.

```
NotificationProtocol:
    async send(notification: Notification) -> bool
    async send_batch(notifications: list[Notification]) -> list[bool]
    get_supported_channels() -> list[str]     (e.g., ["console", "email", "webhook"])
```

```
Notification:
    title: str
    body: str
    channel: str
    priority: NotificationPriority    (Low, Normal, High, Critical)
    metadata: dict
```

---

## AuthenticationProtocol

Defines the contract for authentication.

```
AuthenticationProtocol:
    async authenticate(credentials: dict) -> AuthResult
    async validate_token(token: str) -> bool
    async refresh_token(token: str) -> AuthResult
    async revoke(token: str) -> bool
```

---

## SearchProtocol

Defines the contract for search capabilities.

```
SearchProtocol:
    async search(query: str, entity_types: list[str] | None = None,
                 limit: int = 20, offset: int = 0) -> SearchResults
    async index(entity_type: str, id: str, data: dict) -> None
    async remove_from_index(entity_type: str, id: str) -> None
```

---

## BackupProtocol

Defines the contract for backup operations.

```
BackupProtocol:
    async create_backup(target: str | None = None) -> BackupResult
    async restore_backup(backup_id: str) -> bool
    async list_backups() -> list[BackupInfo]
    async delete_backup(backup_id: str) -> bool
```

---

# Versioning

Every Protocol has a version.

Breaking changes require a new major version.

Providers declare which Protocol versions they support.

The Capability Registry validates compatibility before binding.

---

# Design Rules

Protocols must:

* Use `async def` for all I/O-bound operations.
* Never contain implementation logic.
* Never import Provider-specific types.
* Never import Module-specific types.
* Remain minimal — prefer many small Protocols over few large ones.
* Include docstrings describing expected behavior and error conditions.

Protocols must never:

* Contain default implementations (use mixins or base classes for convenience, separately from the Protocol).
* Reference concrete classes.
* Import from `providers/` or `modules/`.
