"""
Atlas SDK
=========

The official developer interface for the Atlas Software Platform.

Quick Start::

    from atlas_sdk import WorkerBase, capability, on_invocation

    class GreeterWorker(WorkerBase):
        _worker_id = "my.greeter"
        _worker_name = "Greeter"
        _worker_roles = ["app"]

        @capability("my.greeter.greet", version="1.0.0")
        @on_invocation("greet")
        def greet(self, name: str = "World") -> str:
            return f"Hello, {name}!"
"""

# Worker SDK
from .worker import (
    WorkerBase,
    capability,
    on_invocation,
    configure,
    WorkerMeta,
    CapabilityMeta,
    InvocationMeta,
    ConfigField,
)

# Model SDK
from .model import (
    ModelBase,
    model_version,
)

# Adapter SDK
from .adapter import (
    AdapterBase,
    translation,
    TranslationMeta,
)

# Manager SDK
from .manager import (
    ManagerBuilder,
    ManagerManifest,
    WorkerRef,
)

# Testing
from .testing import (
    MockRuntime,
    TestHarness,
    assert_capability_exported,
    assert_invocation_handled,
    assert_model_compliant,
)

# Packaging
from .packaging import (
    PackageBuilder,
    PackageReader,
    PackageSpec,
)

# Config
from .config import SDKConfig

__version__ = "1.0.0"

__all__ = [
    # Worker
    "WorkerBase", "capability", "on_invocation", "configure",
    "WorkerMeta", "CapabilityMeta", "InvocationMeta", "ConfigField",
    # Model
    "ModelBase", "model_version",
    # Adapter
    "AdapterBase", "translation", "TranslationMeta",
    # Manager
    "ManagerBuilder", "ManagerManifest", "WorkerRef",
    # Testing
    "MockRuntime", "TestHarness",
    "assert_capability_exported", "assert_invocation_handled", "assert_model_compliant",
    # Packaging
    "PackageBuilder", "PackageReader", "PackageSpec",
    # Config
    "SDKConfig",
]
