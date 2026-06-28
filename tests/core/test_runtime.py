import pytest

from atlas.core.runtime import AtlasRuntime, RuntimeConfig, RuntimeState
from atlas.core.diagnostics import RuntimeStateError

@pytest.fixture
def runtime():
    config = RuntimeConfig(max_rooms=50, max_room_depth=2)
    return AtlasRuntime(config)

def test_boot_sequence(runtime):
    assert runtime.state == RuntimeState.UNINITIALIZED
    
    res = runtime.boot()
    assert res.is_ok()
    assert runtime.state == RuntimeState.READY
    
    # Verify Subsystems are wired
    assert runtime.get_registry() is not None
    assert runtime.get_worker_manager() is not None
    assert runtime.get_session_manager() is not None
    assert runtime.get_invocation_engine() is not None
    assert runtime.get_room_manager() is not None

def test_shutdown_sequence(runtime):
    runtime.boot().unwrap()
    
    # Create some mock state to verify it gets cleared
    registry = runtime.get_registry()
    registry._workers["fake_worker"] = "mock"
    
    res = runtime.shutdown()
    assert res.is_ok()
    assert runtime.state == RuntimeState.SHUTDOWN
    
    # Verify cleanup
    assert len(registry._workers) == 0

def test_health_summary(runtime):
    # Uninitialized
    health = runtime.get_health_summary()
    assert health["status"] == "UNINITIALIZED"
    assert health["healthy"] is False
    
    runtime.boot().unwrap()
    
    # Ready
    health = runtime.get_health_summary()
    assert health["status"] == "READY"
    assert health["healthy"] is True
    assert "metrics" in health
    assert health["metrics"]["active_rooms"] == 0

def test_illegal_lifecycle(runtime):
    # Cannot shutdown before booting
    res = runtime.shutdown()
    assert res.is_err()
    assert isinstance(res.error, RuntimeStateError)
    
    runtime.boot().unwrap()
    
    # Cannot boot twice
    res = runtime.boot()
    assert res.is_err()
    assert isinstance(res.error, RuntimeStateError)
