# Error Handling

Status: Draft

Version: 0.1

---

# Purpose

This document defines the error handling strategy for Atlas.

All components must follow these conventions.

Consistent error handling enables debuggability, isolation, and graceful degradation.

---

# Philosophy

Fail early.

Fail clearly.

Recover whenever possible.

Never silently ignore failures.

---

# Error Hierarchy

Atlas uses a structured exception hierarchy rooted in a single base class.

```
AtlasError
├── ConfigurationError
│   ├── ConfigNotFoundError
│   ├── ConfigValidationError
│   └── ConfigMergeError
├── LifecycleError
│   ├── InvalidTransitionError
│   ├── InitializationError
│   └── ShutdownError
├── RegistryError
│   ├── DuplicateRegistrationError
│   ├── ComponentNotFoundError
│   └── IncompatibleVersionError
├── CapabilityError
│   ├── CapabilityNotFoundError
│   ├── ProviderNotAvailableError
│   └── CapabilityResolutionError
├── EventError
│   ├── EventDeliveryError
│   ├── SubscriberError
│   └── EventValidationError
├── ModuleError
│   ├── ModuleNotFoundError
│   ├── ModuleDependencyError
│   ├── ModuleManifestError
│   └── ModuleLoadError
├── ProviderError
│   ├── ProviderNotFoundError
│   ├── ProviderInitializationError
│   ├── ProviderManifestError
│   └── ProviderOperationError
├── StorageError
│   ├── ConnectionError
│   ├── QueryError
│   ├── TransactionError
│   └── MigrationError
└── RuntimeError
    ├── BootError
    ├── DependencyResolutionError
    └── ShutdownError
```

---

# Base Error Contract

Every AtlasError must contain:

* message — Human-readable description.
* reason — Why the error occurred.
* context — Relevant state at the time of failure (component name, operation, input values).
* resolution — Suggested fix or next step.

Optional:

* cause — The underlying exception, if wrapping another error.
* error_code — Machine-readable error code for programmatic handling.

---

# Error Context

All errors should include sufficient context to diagnose the problem without needing to reproduce it.

Example:

```
ModuleDependencyError(
    message="Cannot load HealthModule: required capability 'storage' is not available.",
    reason="No Provider registered for the 'storage' capability.",
    context={"module": "health", "required_capability": "storage", "available_capabilities": ["ai", "notifications"]},
    resolution="Register a storage Provider (e.g., SQLiteProvider) before loading HealthModule."
)
```

---

# Error Propagation Rules

## Within Core

Errors in Core components should propagate immediately.

Core must not swallow errors.

Boot failures must halt startup with a clear error message.

## Within Providers

Provider errors should be caught and wrapped in ProviderError.

Provider failures should be isolated — a single Provider failure should not crash Atlas.

Non-critical Provider failures should log and continue.

Critical Provider failures (e.g., primary Storage) should prevent startup.

## Within Modules

Module errors should be caught and wrapped in ModuleError.

Module failures should be isolated — a failing Module should not affect unrelated Modules.

## Within Event Bus

Subscriber errors must never stop Event delivery.

Subscriber errors should be logged and wrapped in SubscriberError.

The Event Bus should continue delivering to remaining subscribers.

---

# Error Severity Levels

Critical — Atlas cannot continue. Requires shutdown.

Error — Component cannot function. Requires isolation or restart.

Warning — Unexpected condition. Component can continue with degraded functionality.

Info — Informational error context. No action required.

---

# Error Logging

All errors must be logged before propagation.

Log entries must include:

* Timestamp
* Severity
* Component Name
* Error Type
* Message
* Context
* Stack Trace (for Error and Critical)

---

# Error Recovery

Where possible, Atlas should attempt recovery:

* Retry transient failures (network, file I/O) with exponential backoff.
* Fall back to alternative Providers if configured.
* Disable non-critical components and continue running.
* Report degraded state through Diagnostics.

Recovery attempts must be logged.

Recovery must never mask the original error.

---

# Design Rules

Errors must:

* Be specific (not generic Exception or ValueError).
* Carry context.
* Suggest resolution.
* Be typed (use the hierarchy, not bare strings).
* Be testable.

Errors must never:

* Be silently ignored.
* Expose internal implementation details to end users.
* Contain secrets or sensitive data.
* Use print() instead of the Logger.
