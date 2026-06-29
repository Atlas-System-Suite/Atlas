# Building Adapters

> The complete guide to creating Atlas Adapters — stateless format translation workers.

---

## What is an Adapter?

An Adapter (also called a Translator) is a specialized Worker that converts data between formats. It performs **zero business logic** — only format conversion. Atlas automatically discovers Adapters and chains them together to find multi-hop translation paths.

For example, if you have an Adapter that converts `python → json` and another that converts `json → msgpack`, Atlas can automatically chain them to translate `python → msgpack`.

---

## Quick Start

### 1. Scaffold

```bash
atlas new
```

Select `adapter`, name it `json_to_msgpack`, and choose `python`.

### 2. Implement

Open `json_to_msgpack/adapter.py` and write your conversion logic.

### 3. Test

```bash
cd json_to_msgpack
atlas test
```

---

## Project Structure

```text
json_to_msgpack/
├── atlas.yaml               # Manifest — declares translation pairs
├── adapter.py               # Implementation — conversion logic
└── test_json_to_msgpack.py  # Tests — validates translations
```

---

## File Reference

### `atlas.yaml` — The Manifest

```yaml
kind: adapter

id: atlas.adapter.json_to_msgpack
name: JsonToMsgpackAdapter
version: 1.0.0
description: Converts JSON to MessagePack format
language: python
roles: [translator]

execution:
  policy: singleton

communication:
  transports: [memory]
  formats: [python]
  default_format: python

imports: []
exports: []

translations:
  - source_format: json
    target_format: msgpack
    cost: 1
```

#### The `translations` Block

This is unique to Adapters. Each entry declares a format conversion pair.

| Field | Required | Description |
|---|---|---|
| `source_format` | ✅ | The input format this Adapter reads. |
| `target_format` | ✅ | The output format this Adapter produces. |
| `cost` | ✅ | A numeric weight for path-finding. Lower cost = preferred route. |

The Runtime uses `cost` to find the cheapest translation path when multiple routes exist.

---

### `adapter.py` — The Implementation

Adapters extend `AdapterBase` from the Atlas SDK and use the `@translation` decorator.

```python
"""
JsonToMsgpackAdapter — An Atlas Adapter

Converts JSON to MessagePack format.
"""
from atlas_sdk import AdapterBase, translation
import json
import msgpack


class JsonToMsgpackAdapter(AdapterBase):
    _adapter_id = "atlas.adapter.json_to_msgpack"
    _adapter_name = "JsonToMsgpackAdapter"
    _adapter_version = "1.0.0"

    @translation(source="json", target="msgpack", cost=1)
    def convert(self, data: bytes) -> bytes:
        """Convert JSON bytes to MessagePack bytes."""
        parsed = json.loads(data)
        return msgpack.packb(parsed)
```

#### Class Attributes

| Attribute | Type | Description |
|---|---|---|
| `_adapter_id` | `str` | Must match `id` in `atlas.yaml`. |
| `_adapter_name` | `str` | Must match `name` in `atlas.yaml`. |
| `_adapter_version` | `str` | Must match `version` in `atlas.yaml`. |

#### Key Differences from WorkerBase

- Adapters extend `AdapterBase`, not `WorkerBase`.
- Adapters use `@translation` instead of `@capability`.
- Adapters must be **stateless**. If your Adapter has `self.state`, reconsider your design.
- Adapters do not use `on_init()`, `on_start()`, or `on_stop()`.

---

### `test_json_to_msgpack.py` — Tests

```python
"""Tests for JsonToMsgpackAdapter."""
from adapter import JsonToMsgpackAdapter


def test_json_to_msgpack_translates():
    adapter = JsonToMsgpackAdapter()
    result = adapter.convert(b'{"key": "value"}')
    assert isinstance(result, bytes)
    assert len(result) > 0


def test_json_to_msgpack_has_translations():
    adapter = JsonToMsgpackAdapter()
    translations = adapter.get_translations()
    assert len(translations) >= 1
    assert translations[0].source_format == "json"
    assert translations[0].target_format == "msgpack"
```

---

## Decorator Reference

### `@translation(source, target, cost)`

Marks a method as a format translation.

```python
@translation(source="json", target="msgpack", cost=1)
def convert(self, data: bytes) -> bytes:
    ...
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `source` | `str` | — | The source format. |
| `target` | `str` | — | The target format. |
| `cost` | `int` | `1` | Weight for the translation graph. Lower = preferred. |

---

## Best Practices

1. **Keep Adapters stateless.** No `__init__`, no `self.state`. Pure input → output.
2. **Set accurate costs.** If your conversion is expensive (e.g., protobuf deserialization), set a higher cost so the Runtime prefers cheaper paths.
3. **One pair per method.** Each `@translation` method should handle exactly one source→target pair.
4. **Handle errors gracefully.** If the input data is malformed, raise a clear exception rather than returning garbage.

---

## What's Next?

- **Build a Worker**: See [Building Workers](workers.md) for business logic workers.
- **Build a Model**: See [Building Models](models.md) for abstract contracts.
- **Compose a Manager**: See [Building Managers](managers.md) to orchestrate an application.
