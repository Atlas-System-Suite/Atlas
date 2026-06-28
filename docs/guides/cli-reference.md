# Atlas CLI Reference 🛠️

The `atlas` CLI is the official developer interface for the Atlas Software Platform.

---

## Commands

### `atlas new`

Launch the interactive project creation wizard. The wizard guides you through selecting the artifact type, project name, namespace, version, description, and implementation language.

```bash
atlas new
```

**Fast Path:**
You can bypass the wizard by providing the type and name as arguments:

```bash
atlas new <type> <name>
```

| Type | Description |
|------|-------------|
| `worker` | A new Worker with manifest, implementation, tests, and README |
| `model` | A new Model with abstract contract and compliance tests |
| `adapter` | A new Adapter (Translator) with manifest and conversion stub |
| `manager` | A new Manager with composition builder and configuration |

**Examples:**
```bash
atlas new worker my_logger
atlas new model storage_model
atlas new adapter json_to_yaml
atlas new manager notes_app
```

---

### `atlas run`

Run the Atlas application in the current directory.

```bash
atlas run
atlas run --manifest path/to/manifest.yaml
```

---

### `atlas test`

Discover and run all tests using pytest.

```bash
atlas test
atlas test --generate  # Generate test stubs from manifests (Sprint 3)
```

---

### `atlas doctor`

Validate your development environment. Checks:
- Python version (>= 3.13)
- Required dependencies (PyYAML, Pydantic)
- Optional tools (pytest, Atlas SDK, Atlas Runtime)
- Project manifest presence

```bash
atlas doctor
```

---

### `atlas validate`

Validate a Worker or Manager manifest against the Atlas schema.

Checks for:
- Missing required fields
- Invalid execution policies
- Malformed exports/imports
- Circular self-dependencies

```bash
atlas validate
atlas validate --manifest path/to/manifest.yaml
```

---

### `atlas inspect`

Pretty-print a summary of a Worker or Manager.

Shows:
- ID, Name, Version, Language, Roles
- Execution policy
- Exported capabilities
- Required capabilities (imports)
- Translation pairs

```bash
atlas inspect
atlas inspect --manifest path/to/manifest.yaml
```

---

### `atlas build`

Build a deterministic `.atlas` package.

The package is a ZIP archive containing:
- `manifest.yaml`
- `src/` (source code)
- `assets/` (static files)
- `docs/` (documentation)
- `checksums.sha256` (integrity verification)

```bash
atlas build
atlas build --output dist/
```

---

### `atlas info`

Display Atlas SDK version, runtime info, and useful links.

```bash
atlas info
```

---

### `atlas clean`

Remove build artifacts (`dist/`, `__pycache__/`, `.pytest_cache/`, etc.).

```bash
atlas clean
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PYTHONPATH` | Must include the Atlas SDK directory | — |
| `ATLAS_LOG_LEVEL` | Logging verbosity | `INFO` |

---

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Validation error or test failure |
| `2` | Missing file or invalid arguments |
