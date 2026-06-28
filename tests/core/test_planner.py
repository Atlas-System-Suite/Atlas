import pytest
import json

from atlas.core.manifest import WorkerManifest, ExecutionPolicy, CommunicationPolicy, ImportDefinition, ExportDefinition
from atlas.core.registry import GlobalRegistry
from atlas.core.loader import WorkerInstance
from atlas.core.resolver import ResolutionGraph, ResolutionNode, CapabilityResolver
from atlas.core.planner import ExecutionPlanner

def create_manifest(id: str, roles: list, imports: list, exports: list, policy: str = "singleton") -> WorkerManifest:
    return WorkerManifest(
        id=id,
        name=id,
        version="1.0.0",
        language="python",
        roles=roles,
        execution=ExecutionPolicy(policy),
        communication=CommunicationPolicy([], []),
        imports=imports,
        exports=exports
    )

def register_mock(registry: GlobalRegistry, manifest: WorkerManifest):
    instance = WorkerInstance(id=manifest.id, manifest=manifest, _executable_handle=None)
    registry.register_worker(instance)

def test_startup_ordering():
    registry = GlobalRegistry()
    
    # Storage (No deps)
    storage = create_manifest("atlas.storage", ["storage"], [], [ExportDefinition("cap.storage", "1.0", 0)])
    
    # Encryption (Depends on Storage)
    encryption = create_manifest("atlas.crypto", ["crypto"], [ImportDefinition("cap.storage", "1.0", False, "")], [ExportDefinition("cap.crypto", "1.0", 0)])
    
    # App (Depends on Crypto)
    app = create_manifest("atlas.app", ["app"], [ImportDefinition("cap.crypto", "1.0", False, "")], [])
    
    register_mock(registry, storage)
    register_mock(registry, encryption)
    register_mock(registry, app)
    
    resolver = CapabilityResolver(registry)
    graph = resolver.resolve(app).unwrap()
    
    planner = ExecutionPlanner(registry)
    plan = planner.plan(graph).unwrap()
    
    # Startup order should be: storage -> crypto -> app
    assert plan.startup_order == ["atlas.storage", "atlas.crypto", "atlas.app"]
    assert plan.workers["atlas.storage"].startup_index == 0
    assert plan.workers["atlas.app"].startup_index == 2

def test_room_vs_session_planning():
    registry = GlobalRegistry()
    
    # Logger (Single role -> Session)
    logger = create_manifest("atlas.logger", ["logger"], [], [ExportDefinition("cap.log", "1.0", 0)])
    
    # Hub (Multiple roles -> Room)
    hub = create_manifest("atlas.hub", ["router", "monitor"], [], [ExportDefinition("cap.hub", "1.0", 0)])
    
    # App
    app = create_manifest("atlas.app", ["app"], [
        ImportDefinition("cap.log", "1.0", False, ""),
        ImportDefinition("cap.hub", "1.0", False, "")
    ], [])
    
    register_mock(registry, logger)
    register_mock(registry, hub)
    register_mock(registry, app)
    
    resolver = CapabilityResolver(registry)
    graph = resolver.resolve(app).unwrap()
    
    planner = ExecutionPlanner(registry)
    plan = planner.plan(graph).unwrap()
    
    assert len(plan.sessions) == 1
    assert len(plan.rooms) == 1
    
    # Verify the specific plans
    session = list(plan.sessions.values())[0]
    assert session.target_worker == "atlas.logger"
    
    room = list(plan.rooms.values())[0]
    assert "atlas.hub" in room.participants
    assert "atlas.app" in room.participants

def test_explain_and_serialize():
    registry = GlobalRegistry()
    storage = create_manifest("atlas.storage", ["storage"], [], [ExportDefinition("cap.storage", "1.0", 0)])
    app = create_manifest("atlas.app", ["app"], [ImportDefinition("cap.storage", "1.0", False, "")], [])
    
    register_mock(registry, storage)
    register_mock(registry, app)
    
    resolver = CapabilityResolver(registry)
    graph = resolver.resolve(app).unwrap()
    
    planner = ExecutionPlanner(registry)
    plan = planner.plan(graph).unwrap()
    
    # Explain should return a non-empty string
    explanation = planner.explain(plan)
    assert len(explanation) > 10
    assert "STARTUP ORDER" in explanation
    
    # Serialize should produce valid JSON
    serialized = planner.serialize(plan)
    data = json.loads(serialized)
    assert data["root_id"] == "atlas.app"
