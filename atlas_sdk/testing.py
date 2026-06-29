"""
Atlas SDK — Testing Utilities
==============================

Provides MockRuntime, TestHarness, and assertion helpers for
testing Workers without booting the full Atlas Runtime.

Usage:
    from atlas_sdk.testing import MockRuntime, TestHarness

    def test_my_worker():
        runtime = MockRuntime()
        runtime.register(MyWorker)
        result = runtime.invoke("my.worker", "greet", {"name": "Atlas"})
        assert result == "Hello, Atlas!"
"""

from typing import Any, Callable, Dict, List, Optional, Type
from dataclasses import dataclass, field


# ---------------------------------------------------------
# Mock Runtime
# ---------------------------------------------------------

class MockRuntime:
    """
    A lightweight fake runtime for unit testing Workers.

    Does NOT boot Atlas. Instead, it provides a minimal in-memory
    environment where Workers can be instantiated, invoked, and
    their lifecycle hooks can be tested.
    """

    def __init__(self):
        self._workers: Dict[str, Any] = {}
        self._config: Dict[str, Any] = {}
        self._invocation_log: List[Dict[str, Any]] = []
        self._session_log: List[Dict[str, Any]] = []

    def register(self, worker_cls: Type, worker_id: Optional[str] = None) -> Any:
        """
        Instantiates and registers a Worker.

        Example::

            worker = runtime.register(MyWorker)
        """
        instance = worker_cls()
        wid = worker_id or getattr(worker_cls, '_worker_id', None) or worker_cls.__name__
        self._workers[wid] = instance

        # Inject config if the worker has config fields
        meta = getattr(instance, 'get_meta', None)
        if meta:
            worker_meta = meta()
            for cfg in worker_meta.config_fields:
                value = self._config.get(cfg.key, cfg.default)
                if cfg.required and value is None:
                    raise ValueError(f"Required config '{cfg.key}' not set in MockRuntime")

        # Call on_init lifecycle hook
        if hasattr(instance, 'on_init'):
            instance.on_init()

        return instance

    def set_config(self, key: str, value: Any) -> "MockRuntime":
        """Sets a configuration value in the mock environment."""
        self._config[key] = value
        return self

    def invoke(self, worker_id: str, action: str, payload: Optional[Dict[str, Any]] = None) -> Any:
        """
        Simulates an Invocation against a registered Worker.

        Example::

            result = runtime.invoke("MyWorker", "greet", {"name": "Atlas"})
        """
        worker = self._workers.get(worker_id)
        if not worker:
            raise KeyError(f"Worker '{worker_id}' not registered in MockRuntime")

        meta = worker.get_meta() if hasattr(worker, 'get_meta') else None
        handler = None

        if meta and action in meta.invocation_handlers:
            handler = meta.invocation_handlers[action]
        else:
            # Fallback: try calling the method directly
            handler = getattr(worker, action, None)

        if handler is None:
            raise AttributeError(f"Worker '{worker_id}' has no handler for action '{action}'")

        self._invocation_log.append({
            "worker_id": worker_id,
            "action": action,
            "payload": payload,
        })

        if payload:
            return handler(worker, **payload) if meta and action in meta.invocation_handlers else handler(**payload)
        return handler(worker) if meta and action in meta.invocation_handlers else handler()

    def get_invocation_log(self) -> List[Dict[str, Any]]:
        """Returns the complete log of all invocations made."""
        return self._invocation_log


# ---------------------------------------------------------
# Test Harness
# ---------------------------------------------------------

class TestHarness:
    """
    A heavier-weight test environment that boots a real AtlasRuntime
    in an isolated context for integration testing.

    Usage::

        harness = TestHarness()
        harness.boot()
        # ... run integration tests ...
        harness.shutdown()
    """

    def __init__(self):
        self._runtime = None

    def boot(self):
        """Boots a real AtlasRuntime for integration testing."""
        # Lazy import to avoid hard dependency on runtime internals
        from atlas.core.runtime import AtlasRuntime, RuntimeConfig
        self._runtime = AtlasRuntime(RuntimeConfig())
        result = self._runtime.boot()
        if hasattr(result, 'is_err') and result.is_err():
            raise RuntimeError(f"TestHarness boot failed: {result.unwrap_err()}")
        return self._runtime

    def shutdown(self):
        """Shuts down the runtime."""
        if self._runtime:
            self._runtime.shutdown()
            self._runtime = None

    def __enter__(self):
        return self.boot()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()
        return False


# ---------------------------------------------------------
# Assertion Helpers
# ---------------------------------------------------------

def assert_capability_exported(worker_instance, capability_name: str) -> None:
    """Asserts that a worker exports the given capability."""
    meta = worker_instance.get_meta()
    cap_names = [c.name for c in meta.capabilities]
    assert capability_name in cap_names, (
        f"Expected capability '{capability_name}' to be exported, "
        f"but worker only exports: {cap_names}"
    )


def assert_invocation_handled(worker_instance, action: str) -> None:
    """Asserts that a worker has a handler registered for the given action."""
    meta = worker_instance.get_meta()
    assert action in meta.invocation_handlers, (
        f"Expected invocation handler for '{action}', "
        f"but worker only handles: {list(meta.invocation_handlers.keys())}"
    )


def assert_model_compliant(model_cls: Type, implementation_cls: Type) -> None:
    """
    Asserts that an implementation class is fully compliant with a Model.

    Example::

        assert_model_compliant(StorageModel, LocalDiskStorageWorker)
    """
    report = model_cls.check_compliance(implementation_cls)
    assert report["compliant"], (
        f"{implementation_cls.__name__} is NOT compliant with {model_cls.__name__}. "
        f"Missing: {report['missing_methods']}. Mismatched: {report['mismatched_signatures']}"
    )
