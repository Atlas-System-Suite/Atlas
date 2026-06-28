# Manifest Schema

Status: Draft

Version: 0.1

---

# Purpose

This document defines the YAML manifest schema for Atlas Modules and Providers.

Manifests enable automatic discovery, validation, and lifecycle management.

Every Module and Provider must include a `manifest.yaml` file.

---

# Module Manifest

## Required Fields

```yaml
# manifest.yaml — Module
kind: module

id: string            # Globally unique identifier (e.g., "atlas.modules.health")
name: string          # Human-readable name (e.g., "Health Module")
version: string       # Semantic version (e.g., "0.1.0")
description: string   # Brief description of the module's purpose

atlas:
  min_version: string   # Minimum compatible Atlas Runtime version (e.g., "0.1.0")
```

## Optional Fields

```yaml
author: string          # Module author or organization
license: string         # License identifier (e.g., "MIT", "Apache-2.0")
homepage: string        # URL to module documentation or repository

capabilities:
  required:             # Capabilities the module requires to function
    - storage           # Module will not load without these
    - ai
  optional:             # Capabilities the module can use if available
    - notifications
    - search

dependencies:
  modules:              # Other modules this module depends on (by ID)
    - atlas.modules.calendar
  providers: []         # Provider-specific dependencies (discouraged)

events:
  publishes:            # Events this module emits
    - Health.WorkoutCompleted
    - Health.MetricRecorded
  subscribes:           # Events this module listens to
    - System.StartupCompleted
    - Calendar.EventCreated

permissions:            # Capabilities and scopes the module requests
  - storage.read
  - storage.write
  - ai.generate
  - notifications.send

configuration:
  schema:               # Module-specific configuration keys
    daily_goal:
      type: integer
      default: 10000
      description: "Daily step goal"
    tracking_enabled:
      type: boolean
      default: true
      description: "Enable automatic tracking"

widgets:                # UI widgets this module provides
  - id: health-dashboard
    name: "Health Dashboard"
    type: dashboard
  - id: workout-log
    name: "Workout Log"
    type: form

commands:               # CLI or UI commands this module registers
  - id: health.log-workout
    name: "Log Workout"
    description: "Record a completed workout"

tags:                   # Discovery and categorization tags
  - health
  - fitness
  - tracking
```

---

# Provider Manifest

## Required Fields

```yaml
# manifest.yaml — Provider
kind: provider

id: string              # Globally unique identifier (e.g., "atlas.providers.sqlite")
name: string            # Human-readable name (e.g., "SQLite Storage Provider")
version: string         # Semantic version (e.g., "0.1.0")
description: string     # Brief description

category: string        # Provider category (e.g., "storage", "ai", "notifications")

atlas:
  min_version: string   # Minimum compatible Atlas Runtime version

capabilities:
  provides:             # Capabilities this provider implements
    - storage
```

## Optional Fields

```yaml
author: string
license: string
homepage: string

protocols:
  implements:           # Protocol versions this provider satisfies
    - name: StorageProtocol
      version: "0.1"

configuration:
  schema:               # Provider-specific configuration
    database_path:
      type: string
      default: "atlas.db"
      description: "Path to SQLite database file"
      required: true
    journal_mode:
      type: string
      default: "wal"
      description: "SQLite journal mode"
      enum: ["wal", "delete", "truncate", "memory"]

  secrets:              # Configuration keys that contain sensitive values
    - api_key
    - database_password

dependencies:
  python:               # Python package dependencies
    - aiosqlite>=0.19.0
  system: []            # System-level dependencies

health_check:
  enabled: true
  interval_seconds: 60
  timeout_seconds: 5

tags:
  - storage
  - sqlite
  - local
```

---

# Validation Rules

## ID Format

IDs must use reverse-domain notation.

Format: `atlas.<kind>.<name>`

Examples:

* `atlas.modules.health`
* `atlas.providers.sqlite`
* `community.modules.pomodoro`

Third-party components should not use the `atlas.` prefix.

## Version Format

Semantic Versioning (semver).

Format: `MAJOR.MINOR.PATCH`

Examples: `0.1.0`, `1.0.0`, `2.3.1`

## Kind

Must be one of: `module`, `provider`, `application`.

## Required Capabilities

If a Module lists a required capability that no registered Provider satisfies, the Module must not load.

The Runtime should report a clear error with resolution guidance.

## Configuration Schema Types

Supported types:

* `string`
* `integer`
* `float`
* `boolean`
* `list`
* `dict`

Each configuration key may include:

* `type` — required
* `default` — optional
* `description` — required
* `required` — optional (defaults to false)
* `enum` — optional (list of valid values)
* `min` / `max` — optional (for numeric types)

---

# Discovery

During startup, the Runtime:

1. Scans known directories for `manifest.yaml` files.
2. Parses each manifest.
3. Validates against this schema.
4. Rejects invalid manifests with clear error messages.
5. Registers valid components in the Registry.

---

# Design Rules

Manifests must:

* Be valid YAML.
* Contain all required fields.
* Use semantic versioning.
* Declare all capabilities, events, and permissions honestly.
* Never include executable code.

Manifests must never:

* Contain secrets or credentials.
* Reference absolute file paths.
* Include Provider-specific implementation details.
