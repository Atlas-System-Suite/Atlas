# Configuration Schema

Status: Draft

Version: 0.1

---

# Purpose

This document defines the YAML configuration schema for Atlas.

Configuration controls the behavior of the Runtime, Modules, and Providers.

---

# Configuration File

Atlas uses a single primary configuration file.

Default name: `atlas.yaml`

Location: application root or path specified by `ATLAS_CONFIG` environment variable.

---

# Top-Level Schema

```yaml
# atlas.yaml

atlas:
  version: "0.1.0"               # Atlas configuration schema version
  name: "My LifeOS"              # Application display name
  environment: "development"      # development | testing | production

runtime:
  log_level: "info"              # debug | info | warning | error | critical
  log_format: "text"             # text | json
  boot_timeout_seconds: 30       # Maximum time for boot sequence
  shutdown_timeout_seconds: 15   # Maximum time for graceful shutdown
  enable_diagnostics: true       # Enable runtime diagnostics
  enable_scheduler: true         # Enable the built-in scheduler

storage:
  provider: "sqlite"             # Default storage provider ID
  config:                        # Provider-specific configuration
    database_path: "data/atlas.db"
    journal_mode: "wal"

ai:
  enabled: true                  # Enable AI capabilities
  provider: "gemini"             # Default AI provider ID
  config:                        # Provider-specific configuration
    model: "gemini-2.0-flash"
    max_tokens: 4096

notifications:
  enabled: true
  provider: "console"
  config: {}

modules:
  enabled:                       # List of module IDs to load
    - atlas.modules.health
    - atlas.modules.finance
    - atlas.modules.journal
  disabled: []                   # Explicitly disabled modules (overrides enabled)
  config:                        # Per-module configuration overrides
    atlas.modules.health:
      daily_goal: 12000
      tracking_enabled: true
    atlas.modules.finance:
      currency: "USD"

providers:
  additional:                    # Additional providers beyond defaults
    - id: atlas.providers.openai
      config:
        model: "gpt-4o"
  preferred:                     # Capability → preferred provider mapping
    storage: "sqlite"
    ai: "gemini"
    notifications: "console"

feature_flags:                   # Optional feature toggles
  experimental_search: false
  ai_recommendations: true

paths:
  data: "data/"                  # Data storage directory
  logs: "logs/"                  # Log file directory
  backups: "backups/"            # Backup directory
  modules: "modules/"            # Module discovery directory
  providers: "providers/"        # Provider discovery directory
```

---

# Configuration Priority

Configuration values are resolved in priority order (highest → lowest):

1. CLI Arguments
2. Environment Variables
3. Application Configuration (`atlas.yaml`)
4. Module/Provider Defaults (from manifests)
5. Atlas Defaults (built-in)

Higher priority always overrides lower priority.

---

# Environment Variables

Environment variables use the `ATLAS_` prefix.

Nested keys use double underscore as separator.

Examples:

* `ATLAS_ENV=production` → `atlas.environment`
* `ATLAS_RUNTIME__LOG_LEVEL=debug` → `runtime.log_level`
* `ATLAS_STORAGE__PROVIDER=postgres` → `storage.provider`
* `ATLAS_AI__ENABLED=false` → `ai.enabled`

---

# Secrets

Sensitive values must never appear in `atlas.yaml`.

Secrets should be provided through:

* Environment variables
* `.env` file (local development only)
* Secret management systems (future)

Common secrets:

* `ATLAS_AI__API_KEY` — AI provider API key
* `ATLAS_STORAGE__PASSWORD` — Database password
* `ATLAS_NOTIFICATIONS__WEBHOOK_URL` — Notification webhook

---

# Validation

All configuration is validated before Runtime startup.

Validation checks:

* Required fields are present.
* Types match expected types.
* Enum values are valid.
* Numeric values are within range.
* Referenced providers exist.
* Referenced modules exist.
* Version compatibility.

Invalid configuration must prevent startup.

Validation errors must include:

* Field path (e.g., `storage.config.database_path`)
* Expected type
* Actual value
* Suggested fix

---

# Merge Algorithm

Configuration merging follows these rules:

1. Start with Atlas built-in defaults.
2. Deep-merge Module/Provider defaults from manifests.
3. Deep-merge application `atlas.yaml`.
4. Override with environment variables.
5. Override with CLI arguments.

Deep merge rules:

* Dictionaries are merged recursively.
* Lists are replaced entirely (not appended).
* Scalar values are overwritten.
* `null` values remove the key.

---

# Configuration Profiles

Atlas supports multiple configuration profiles through file naming:

* `atlas.yaml` — default
* `atlas.development.yaml` — development overrides
* `atlas.testing.yaml` — testing overrides
* `atlas.production.yaml` — production overrides

The active profile is determined by `atlas.environment` or `ATLAS_ENV`.

Profile files are merged on top of the default `atlas.yaml`.

---

# Design Rules

Configuration should be:

* Human-readable.
* Validated before use.
* Versioned (schema version in `atlas.version`).
* Backward compatible within a major version.
* Provider-independent at the top level.

Configuration must never:

* Contain executable code.
* Contain secrets in plain text.
* Require code changes for common adjustments.
* Include provider-specific types in top-level keys.
