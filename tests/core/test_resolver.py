import pytest
from atlas.core.resolver import CapabilityResolver, match_version
from atlas.core.diagnostics import AmbiguousResolutionError, CircularDependencyError, ResolutionFailedError
from atlas.core.registry import GlobalRegistry
from atlas.core.loader import WorkerInstance
from atlas.core.manifest import WorkerManifest, ExecutionPolicy, CommunicationPolicy, ImportDefinition, ExportDefinition

# Helpers to build mock workers
def create_manifest(id: str, imports: list, exports: list) -> WorkerManifest:
    return WorkerManifest(
        id=id,
        name=id,
        version="1.0.0",
        language="python",
        roles=[],
        execution=ExecutionPolicy("singleton"),
        communication=CommunicationPolicy([], []),
        imports=imports,
        exports=exports
    )

def register_mock(registry: GlobalRegistry, manifest: WorkerManifest):
    instance = WorkerInstance(id=manifest.id, manifest=manifest, _executable_handle=None)
    registry.register_worker(instance)

# ---------------------------------------------------------
# SemVer Tests
# ---------------------------------------------------------
def test_match_version():
    # Exact
    assert match_version("1.0.0", "1.0.0")
    assert not match_version("1.0.1", "1.0.0")
    
    # Minimum
    assert match_version("1.2.3", ">=1.0.0")
    assert match_version("2.0.0", ">=1.0.0")
    assert not match_version("0.9.0", ">=1.0.0")
    
    # Caret (Compatible)
    assert match_version("1.2.3", "^1.0.0")
    assert match_version("1.9.9", "^1.0.0")
    assert not match_version("2.0.0", "^1.0.0")
    assert match_version("0.2.1", "^0.2.0")
    assert not match_version("0.3.0", "^0.2.0")

# ---------------------------------------------------------
# Graph Resolution Tests
# ---------------------------------------------------------
def test_successful_resolution():
    registry = GlobalRegistry()
    
    storage = create_manifest("atlas.storage", [], [ExportDefinition("cap.storage", "1.0.0", 0)])
    logger = create_manifest("atlas.logger", [], [ExportDefinition("cap.log", "1.2.0", 0)])
    
    app = create_manifest("atlas.app", [
        ImportDefinition("cap.storage", ">=1.0.0", False, ""),
        ImportDefinition("cap.log", "^1.0.0", False, "")
    ], [])
    
    register_mock(registry, storage)
    register_mock(registry, logger)
    register_mock(registry, app)
    
    resolver = CapabilityResolver(registry)
    graph = resolver.resolve(app).unwrap()
    
    assert len(graph.nodes) == 3
    assert "atlas.storage" in graph.nodes
    assert "atlas.logger" in graph.nodes
    assert len(graph.missing_optionals) == 0

def test_missing_required():
    registry = GlobalRegistry()
    app = create_manifest("atlas.app", [ImportDefinition("cap.missing", "1.0.0", False, "")], [])
    register_mock(registry, app)
    
    resolver = CapabilityResolver(registry)
    res = resolver.resolve(app)
    assert res.is_err()
    assert isinstance(res.error, ResolutionFailedError)

def test_missing_optional():
    registry = GlobalRegistry()
    app = create_manifest("atlas.app", [ImportDefinition("cap.missing", "1.0.0", True, "")], [])
    register_mock(registry, app)
    
    resolver = CapabilityResolver(registry)
    graph = resolver.resolve(app).unwrap()
    
    assert len(graph.nodes) == 1
    assert "cap.missing" in graph.missing_optionals

def test_ambiguity_failure():
    registry = GlobalRegistry()
    # Both offer cap.db with priority 0
    db1 = create_manifest("atlas.db1", [], [ExportDefinition("cap.db", "1.0.0", 0)])
    db2 = create_manifest("atlas.db2", [], [ExportDefinition("cap.db", "1.0.0", 0)])
    app = create_manifest("atlas.app", [ImportDefinition("cap.db", "1.0.0", False, "")], [])
    
    register_mock(registry, db1)
    register_mock(registry, db2)
    register_mock(registry, app)
    
    resolver = CapabilityResolver(registry)
    res = resolver.resolve(app)
    assert res.is_err()
    assert isinstance(res.error, AmbiguousResolutionError)

def test_ambiguity_resolved_by_precedence():
    registry = GlobalRegistry()
    # db2 has higher precedence (10 vs 0)
    db1 = create_manifest("atlas.db1", [], [ExportDefinition("cap.db", "1.0.0", 0)])
    db2 = create_manifest("atlas.db2", [], [ExportDefinition("cap.db", "1.0.0", 10)])
    app = create_manifest("atlas.app", [ImportDefinition("cap.db", "1.0.0", False, "")], [])
    
    register_mock(registry, db1)
    register_mock(registry, db2)
    register_mock(registry, app)
    
    resolver = CapabilityResolver(registry)
    graph = resolver.resolve(app).unwrap()
    
    assert "atlas.db2" in graph.nodes
    assert "atlas.db1" not in graph.nodes

def test_circular_dependency():
    registry = GlobalRegistry()
    # A -> cap.b (B)
    # B -> cap.a (A)
    a = create_manifest("worker.A", [ImportDefinition("cap.b", "1.0", False, "")], [ExportDefinition("cap.a", "1.0", 0)])
    b = create_manifest("worker.B", [ImportDefinition("cap.a", "1.0", False, "")], [ExportDefinition("cap.b", "1.0", 0)])
    
    register_mock(registry, a)
    register_mock(registry, b)
    
    resolver = CapabilityResolver(registry)
    res = resolver.resolve(a)
    assert res.is_err()
    assert isinstance(res.error, CircularDependencyError)
