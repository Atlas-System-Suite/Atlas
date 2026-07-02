"""
Atlas SDK — Worker V2 (Atlas 0.2)
=================================

The radically simplified API for authoring Atlas Workers.
Eliminates boilerplate through metaclasses and type inference.

Usage:
    from atlas_sdk import Worker, action
    from src.workers.storage import StorageWorker

    class NotesWorker(Worker):
        def __init__(self, db: StorageWorker):
            self.db = db

        @action
        async def create_note(self, content: str):
            await self.db.write(content=content)
"""

from abc import ABC
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
import functools
import inspect
import yaml


# ---------------------------------------------------------
# Metadata Containers
# ---------------------------------------------------------

@dataclass
class CapabilityMeta:
    name: str
    version: str = "1.0.0"
    precedence: int = 0

@dataclass
class InvocationMeta:
    action: str

@dataclass
class ConfigField:
    key: str
    default: Any = None
    required: bool = False

@dataclass
class WorkerMeta:
    capabilities: List[CapabilityMeta] = field(default_factory=list)
    invocation_handlers: Dict[str, Callable] = field(default_factory=dict)
    config_fields: List[ConfigField] = field(default_factory=list)
    requirements: List[Dict[str, Any]] = field(default_factory=list)


# ---------------------------------------------------------
# V2 Decorators
# ---------------------------------------------------------

def action(func: Callable) -> Callable:
    """
    Atlas 0.2: The primary decorator for exposing a method to the Runtime.
    This replaces BOTH @capability and @on_invocation.
    The method name becomes the action name.
    """
    action_name = func.__name__
    
    # We store the action marker. The __init_subclass__ will expand it into a Capability.
    func._atlas_action = action_name
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    wrapper._atlas_action = action_name
    return wrapper

def configure(key: str, default: Any = None, required: bool = False):
    """Marks a method as a configuration consumer."""
    def decorator(func: Callable) -> Callable:
        func._atlas_config = ConfigField(key=key, default=default, required=required)
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        wrapper._atlas_config = func._atlas_config
        return wrapper
    return decorator


# ---------------------------------------------------------
# V2 Worker Base
# ---------------------------------------------------------

class Worker(ABC):
    """
    Atlas 0.2 Worker Base.
    - Infers Worker ID from module/class name.
    - Infers Capabilities/Invocations from @action methods.
    - Infers Requirements from __init__ type hints.
    """
    
    _worker_id: Optional[str] = None
    _worker_version: str = "1.0.0"
    _worker_roles: List[str] = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        
        # 1. Infer Worker ID
        if not getattr(cls, "_worker_id", None):
            cls._worker_id = f"{cls.__module__.split('.')[-1]}.{cls.__name__.lower()}"
            
        meta = WorkerMeta()
        
        # 2. Inspect __init__ for Dependency Injection requirements
        init_sig = inspect.signature(cls.__init__)
        for param_name, param in init_sig.parameters.items():
            if param_name in ("self", "args", "kwargs"):
                continue
            
            # Use type hint to infer the target capability
            if param.annotation != inspect.Parameter.empty and hasattr(param.annotation, "_worker_id"):
                target_capability = param.annotation._worker_id
            else:
                # Fallback to the parameter name if no valid type hint exists
                target_capability = param_name
                
            meta.requirements.append({
                "capability": target_capability,
                "version": "*",
                "as_alias": param_name
            })
            
        # 3. Scan methods for @action
        for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            if hasattr(method, '_atlas_action'):
                action_name = method._atlas_action
                
                # Expose a capability mapping to this action
                cap_name = f"{cls._worker_id}.{action_name}"
                meta.capabilities.append(CapabilityMeta(name=cap_name))
                meta.invocation_handlers[action_name] = method
                
            if hasattr(method, '_atlas_config'):
                meta.config_fields.append(method._atlas_config)

        cls._atlas_meta = meta

    def on_init(self) -> None:
        pass

    def on_start(self) -> None:
        pass

    def on_stop(self) -> None:
        pass

    def get_meta(self) -> WorkerMeta:
        return self.__class__._atlas_meta

    def generate_manifest(self) -> Dict[str, Any]:
        meta = self.get_meta()
        cls = self.__class__

        return {
            "id": cls._worker_id,
            "name": cls.__name__,
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
        }

    def write_manifest(self, path: str = "atlas.yaml") -> str:
        with open(path, "w") as f:
            yaml.dump(self.generate_manifest(), f, default_flow_style=False, sort_keys=False)
        return path

# Keep backwards compatibility aliases for now, to not break absolutely everything simultaneously.
WorkerBase = Worker
def capability(*args, **kwargs):
    def decorator(func):
        return action(func)
    return decorator
def on_invocation(*args, **kwargs):
    def decorator(func):
        return action(func)
    return decorator
def require(*args, **kwargs):
    return lambda t: t
