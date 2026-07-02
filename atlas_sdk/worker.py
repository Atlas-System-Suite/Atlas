"""
Atlas SDK — Worker Base
=======================

The WorkerBase class and associated decorators provide the canonical way
to build Atlas Workers without understanding runtime internals.

Usage:
    from atlas_sdk import WorkerBase, capability, on_invocation, configure

    class MyWorker(WorkerBase):
        @capability("atlas.core.greeter", version="1.0.0")
        def greet(self, name: str) -> str:
            return f"Hello, {name}!"
"""

from abc import ABC
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    TypeVar,
)
from dataclasses import dataclass, field
import functools
import inspect
import yaml
import os


# ---------------------------------------------------------
# Metadata Containers
# ---------------------------------------------------------

@dataclass
class CapabilityMeta:
    """Metadata attached to a method by the @capability decorator."""
    name: str
    version: str = "1.0.0"
    precedence: int = 0


@dataclass
class InvocationMeta:
    """Metadata attached to a method by the @on_invocation decorator."""
    action: str


@dataclass
class ConfigField:
    """Metadata attached by the @configure decorator."""
    key: str
    default: Any = None
    required: bool = False


@dataclass
class WorkerMeta:
    """Aggregated metadata collected from decorators on a WorkerBase subclass."""
    capabilities: List[CapabilityMeta] = field(default_factory=list)
    invocation_handlers: Dict[str, Callable] = field(default_factory=dict)
    config_fields: List[ConfigField] = field(default_factory=list)
    requirements: List[Dict[str, Any]] = field(default_factory=list)


# ---------------------------------------------------------
# Decorators
# ---------------------------------------------------------

def capability(name: str, version: str = "1.0.0", precedence: int = 0):
    """
    Marks a method as an exported Capability.

    Example::

        @capability("atlas.core.greeter", version="1.0.0")
        def greet(self, name: str) -> str:
            return f"Hello, {name}!"
    """
    def decorator(func: Callable) -> Callable:
        func._atlas_capability = CapabilityMeta(
            name=name, version=version, precedence=precedence
        )
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        wrapper._atlas_capability = func._atlas_capability
        return wrapper
    return decorator


def on_invocation(action: str):
    """
    Registers a method as an Invocation handler for a specific action.

    Example::

        @on_invocation("process_order")
        def handle_order(self, payload: dict) -> dict:
            return {"status": "completed"}
    """
    def decorator(func: Callable) -> Callable:
        func._atlas_invocation = InvocationMeta(action=action)
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        wrapper._atlas_invocation = func._atlas_invocation
        return wrapper
    return decorator


def configure(key: str, default: Any = None, required: bool = False):
    """
    Marks a method as a configuration consumer. The SDK injects
    the configuration value before the worker starts.

    Example::

        @configure("DATABASE_URL", required=True)
        def set_db_url(self, value: str):
            self.db_url = value
    """
    def decorator(func: Callable) -> Callable:
        func._atlas_config = ConfigField(key=key, default=default, required=required)
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        wrapper._atlas_config = func._atlas_config
        return wrapper
    return decorator


def require(capability_name: str, version: str = "*", as_alias: Optional[str] = None):
    """
    Declares that a Worker requires a Capability.
    Can be placed on a method (like `on_init`) or on the Worker class itself.
    """
    def decorator(target: Any) -> Any:
        if not hasattr(target, "_atlas_requirements"):
            target._atlas_requirements = []
        target._atlas_requirements.append({
            "capability": capability_name,
            "version": version,
            "as_alias": as_alias or capability_name.split(".")[-1]
        })
        return target
    return decorator


# ---------------------------------------------------------
# WorkerBase
# ---------------------------------------------------------

class WorkerBase(ABC):
    """
    The official base class for all Atlas Workers.

    Subclass this to build a Worker. The SDK automatically discovers
    capabilities, invocation handlers, and config fields via decorators.

    Lifecycle Hooks (override as needed):
        - on_init()          — called after construction
        - on_start()         — called when the worker starts
        - on_stop()          — called when the worker stops
        - on_health_check()  — called periodically by the runtime
    """

    # Class-level metadata cache
    _worker_id: str = ""
    _worker_name: str = ""
    _worker_version: str = "1.0.0"
    _worker_roles: List[str] = []

    def __init_subclass__(cls, **kwargs):
        """Automatically collect metadata from decorators when a subclass is defined."""
        super().__init_subclass__(**kwargs)
        meta = WorkerMeta()

        # Collect class-level requirements
        if hasattr(cls, "_atlas_requirements"):
            meta.requirements.extend(cls._atlas_requirements)

        for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            if hasattr(method, '_atlas_capability'):
                meta.capabilities.append(method._atlas_capability)
            if hasattr(method, '_atlas_invocation'):
                meta.invocation_handlers[method._atlas_invocation.action] = method
            if hasattr(method, '_atlas_config'):
                meta.config_fields.append(method._atlas_config)
            if hasattr(method, '_atlas_requirements'):
                meta.requirements.extend(method._atlas_requirements)

        cls._atlas_meta = meta

    # ---- Lifecycle Hooks (override in subclasses) ----

    def on_init(self) -> None:
        """Called after the worker is constructed. Set up internal state here."""
        pass

    def on_start(self) -> None:
        """Called when the runtime starts this worker."""
        pass

    def on_stop(self) -> None:
        """Called when the runtime stops this worker. Clean up resources here."""
        pass

    def on_health_check(self) -> Dict[str, Any]:
        """Called periodically. Return a health status dict."""
        return {"healthy": True}

    # ---- SDK Utilities ----

    def get_meta(self) -> WorkerMeta:
        """Returns the collected metadata for this worker."""
        cls = self.__class__
        meta = cls._atlas_meta
        if hasattr(cls, "_atlas_requirements"):
            for req in cls._atlas_requirements:
                if req not in meta.requirements:
                    meta.requirements.append(req)
        return meta

    def generate_manifest(self) -> Dict[str, Any]:
        """
        Auto-generates a Worker Manifest dictionary from the class metadata
        and decorators. This can be written to a atlas.yaml file.
        """
        meta = self.get_meta()
        cls = self.__class__

        manifest = {
            "id": cls._worker_id or f"atlas.worker.{cls.__name__.lower()}",
            "name": cls._worker_name or cls.__name__,
            "version": cls._worker_version,
            "language": "python",
            "roles": cls._worker_roles or ["worker"],
            "execution": {"policy": "singleton"},
            "communication": {
                "transports": ["memory"],
                "formats": ["python"],
                "default_format": "python",
            },
            "imports": [
                {
                    "capability": req["capability"],
                    "version": req["version"],
                    "optional": False,
                    "reason": f"Required as {req['as_alias']}"
                }
                for req in meta.requirements
            ],
            "exports": [
                {
                    "capability": cap.name,
                    "version": cap.version,
                    "precedence": cap.precedence,
                }
                for cap in meta.capabilities
            ],
            "translations": [],
        }
        return manifest

    def write_manifest(self, path: str = "atlas.yaml") -> str:
        """Generates and writes the manifest to a YAML file."""
        manifest = self.generate_manifest()
        with open(path, "w") as f:
            yaml.dump(manifest, f, default_flow_style=False, sort_keys=False)
        return path
