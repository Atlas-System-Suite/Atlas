# Building Models

> The complete guide to creating Atlas Models — abstract contracts that define capability interfaces.

---

## What is a Model?

A Model is an **abstract contract**. It defines the method signatures that a capability must implement, without containing any business logic. Think of it as a USB-C specification — everyone agrees on the shape, so you can plug in whatever brand you want.

Models enable:
- **Interchangeability**: Any Worker that implements `StorageModel` can be swapped for any other.
- **Compliance Testing**: The SDK can automatically verify that an implementation satisfies the contract.
- **Documentation Generation**: Models can auto-generate API docs from their method signatures.

---

## Quick Start

### 1. Scaffold

```bash
atlas new
```

Select `model`, name it `greeter`, and choose `python`.

### 2. Define

Open `greeter/model.py` and define your abstract methods.

### 3. Test

```bash
cd greeter
atlas test
```

---

## Project Structure

```text
greeter/
├── model.py          # The contract — abstract method signatures
└── test_greeter.py   # Compliance tests — verifies implementations
```

Models do **not** have an `atlas.yaml` manifest. They are pure Python contracts.

---

## File Reference

### `model.py` — The Contract

Models extend `ModelBase` and use `@abstractmethod` to define the interface.

```python
"""
GreeterModel — An Atlas Model

Defines the contract for greeting capabilities.
"""
from abc import abstractmethod
from atlas_sdk import ModelBase, model_version


@model_version("1.0.0")
class GreeterModel(ModelBase):
    """
    Any Worker claiming the 'greeter' capability must implement these methods.
    """

    @abstractmethod
    def greet(self, name: str) -> str:
        """Greet a person by name. Must return a greeting string."""
        ...

    @abstractmethod
    def farewell(self, name: str) -> str:
        """Say goodbye to a person by name."""
        ...
```

#### Class Attributes

| Attribute | Type | Default | Description |
|---|---|---|---|
| `_model_version` | `str` | `"1.0.0"` | Set via the `@model_version()` decorator. |

#### Key Rules

- Every method in a Model must be decorated with `@abstractmethod`.
- Models contain **zero** implementation. Only method signatures.
- Models do not use `@capability`, `@on_invocation`, or any runtime decorators.

---

### `test_greeter.py` — Compliance Tests

```python
"""Compliance tests for GreeterModel."""
from atlas_sdk.testing import assert_model_compliant
from model import GreeterModel


class DummyGreeterImpl(GreeterModel):
    """A dummy implementation for compliance testing."""

    def greet(self, name: str) -> str:
        return f"Hello, {name}!"

    def farewell(self, name: str) -> str:
        return f"Goodbye, {name}!"


def test_dummy_is_compliant():
    assert_model_compliant(GreeterModel, DummyGreeterImpl)


def test_contract_introspection():
    contract = GreeterModel.get_contract()
    method_names = [m["method"] for m in contract]
    assert "greet" in method_names
    assert "farewell" in method_names
```

---

## ModelBase API Reference

### `ModelBase.get_contract()` — Class Method

Introspects the Model and returns a list of abstract methods with their signatures.

```python
contract = GreeterModel.get_contract()
# [
#   {"method": "greet", "params": [{"name": "name", "annotation": "str"}], "return_type": "str"},
#   {"method": "farewell", "params": [{"name": "name", "annotation": "str"}], "return_type": "str"},
# ]
```

### `ModelBase.check_compliance(implementation)` — Class Method

Checks whether a class correctly implements all abstract methods.

```python
report = GreeterModel.check_compliance(MyGreeterWorker)
print(report)
# {
#   "model": "GreeterModel",
#   "model_version": "1.0.0",
#   "implementation": "MyGreeterWorker",
#   "compliant": True,
#   "missing_methods": [],
#   "mismatched_signatures": [],
# }
```

### `ModelBase.generate_docs()` — Class Method

Auto-generates Markdown documentation from the Model's abstract methods.

```python
docs = GreeterModel.generate_docs()
print(docs)
# # GreeterModel
#
# **Version:** 1.0.0
#
# ## Methods
#
# ### `greet(name: str) -> str`
# ### `farewell(name: str) -> str`
```

---

## Decorator Reference

### `@model_version(version)`

Tags a Model class with a semantic version.

```python
@model_version("2.1.0")
class StorageModel(ModelBase):
    ...
```

| Parameter | Type | Description |
|---|---|---|
| `version` | `str` | Semantic version string (e.g., `"1.0.0"`). |

---

## Real-World Example: The LoggerModel

This is the actual `LoggerModel` from the Atlas Standard Library:

### `model.py`

```python
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class LoggerModel(ABC):
    """
    Official Atlas Standard Model for Logging.
    Defines the contract for any worker claiming the 'atlas.core.logger' capability.
    """

    @abstractmethod
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        pass

    @abstractmethod
    def info(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        pass

    @abstractmethod
    def warn(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        pass

    @abstractmethod
    def error(self, message: str, exc_info: Optional[str] = None,
              context: Optional[Dict[str, Any]] = None) -> None:
        pass
```

### A Worker implementing it

```python
import logging
from models.core.logger_model import LoggerModel


class ConsoleLoggerWorker(LoggerModel):
    """Reference Implementation of the LoggerModel."""

    def __init__(self):
        self.logger = logging.getLogger("atlas.stdlib.logger")
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)

    def debug(self, message, context=None):
        self.logger.debug(self._fmt(message, context))

    def info(self, message, context=None):
        self.logger.info(self._fmt(message, context))

    def warn(self, message, context=None):
        self.logger.warning(self._fmt(message, context))

    def error(self, message, exc_info=None, context=None):
        msg = self._fmt(message, context)
        if exc_info:
            msg = f"{msg} | Ex: {exc_info}"
        self.logger.error(msg)

    def _fmt(self, message, context):
        return f"{message} | ctx: {context}" if context else message
```

The Worker implements every abstract method from the Model. If it missed one, `assert_model_compliant(LoggerModel, ConsoleLoggerWorker)` would fail with a clear error message.

---

## Best Practices

1. **Models are interfaces, not implementations.** Never put logic inside a Model. If you're writing `if/else`, it belongs in a Worker.
2. **Use `@abstractmethod` on every method.** This ensures Python itself enforces the contract at class definition time.
3. **Write compliance tests.** Always include a dummy implementation and run `assert_model_compliant()`.
4. **Version your Models.** Use `@model_version()` and bump the version when you add or change methods. This helps Workers know which version of the contract they're implementing.
5. **Keep parameters simple.** Models should use standard Python types (`str`, `bytes`, `dict`, `list`). Avoid complex custom types that would make cross-language implementation difficult.

---

## What's Next?

- **Implement a Model**: See [Building Workers](workers.md) to create a Worker that satisfies a Model contract.
- **Build an Adapter**: See [Building Adapters](adapters.md) for format translation.
- **Compose a Manager**: See [Building Managers](managers.md) to orchestrate an application.
