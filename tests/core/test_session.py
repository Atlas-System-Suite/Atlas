import pytest
import threading

from atlas.core.manifest import WorkerManifest, ExecutionPolicy, CommunicationPolicy, ExportDefinition, TranslationDefinition
from atlas.core.registry import GlobalRegistry
from atlas.core.loader import WorkerInstance
from atlas.core.transport import InMemoryTransport
from atlas.core.translation import TranslationResolver
from atlas.core.session import SessionManager, CommunicationHeader, HeaderRequest, SessionState
from atlas.core.diagnostics import SessionStateError, SessionNegotiationError

def create_worker(id: str, cap: str, format: str) -> WorkerManifest:
    return WorkerManifest(
        id=id,
        name=id,
        version="1.0.0",
        language="test",
        roles=["app"],
        execution=ExecutionPolicy("singleton"),
        communication=CommunicationPolicy([], [], default_format=format),
        imports=[],
        exports=[ExportDefinition(cap, "1.0.0")],
        translations=[]
    )
    
def create_translator(id: str, source: str, target: str) -> WorkerManifest:
    return WorkerManifest(
        id=id,
        name=id,
        version="1.0.0",
        language="test",
        roles=["translator"],
        execution=ExecutionPolicy("singleton"),
        communication=CommunicationPolicy([], [], default_format="internal"),
        imports=[],
        exports=[],
        translations=[TranslationDefinition(source, target)]
    )

@pytest.fixture
def manager():
    reg = GlobalRegistry()
    trans_res = TranslationResolver(reg)
    transport = InMemoryTransport()
    
    # Mock Workers
    # Worker A needs "database"
    reg.register_worker(WorkerInstance("workerA", create_worker("workerA", "ui", "python"), None))
    # Worker B provides "database" in rust
    reg.register_worker(WorkerInstance("workerB", create_worker("workerB", "database", "rust"), None))
    # Translator
    reg.register_worker(WorkerInstance("t.py2rust", create_translator("t.py2rust", "python", "rust"), None))
    
    return SessionManager(reg, trans_res, transport)

def test_successful_negotiation(manager):
    header = CommunicationHeader("workerA", [HeaderRequest("database")])
    res = manager.process_header(header)
    
    assert res.is_ok()
    session_ids = res.unwrap()
    assert len(session_ids) == 1
    
    sess = manager.session_registry.get_session(session_ids[0])
    assert sess is not None
    assert sess.state == SessionState.ACTIVE
    assert sess.binding.capability == "database"
    assert sess.binding.source_worker == "workerA"
    assert sess.binding.target_worker == "workerB"
    assert sess.translation_chain is not None
    assert sess.channel_id is not None
    
def test_missing_capability(manager):
    header = CommunicationHeader("workerA", [HeaderRequest("missing_cap")])
    res = manager.process_header(header)
    assert res.is_err()
    assert isinstance(res.error, SessionNegotiationError)
    
def test_missing_translation(manager):
    # Worker C needs database but speaks JSON. No JSON->Rust translator exists.
    reg = manager._global_registry
    reg.register_worker(WorkerInstance("workerC", create_worker("workerC", "none", "json"), None))
    
    header = CommunicationHeader("workerC", [HeaderRequest("database")])
    res = manager.process_header(header)
    assert res.is_err()
    assert isinstance(res.error, SessionNegotiationError)
    assert "Translation failed" in res.error.message

def test_optional_capabilities(manager):
    # Missing capability but marked optional
    header = CommunicationHeader("workerA", [HeaderRequest("missing_cap", optional=True)])
    res = manager.process_header(header)
    assert res.is_ok()
    assert len(res.unwrap()) == 0

def test_session_lifecycle(manager):
    header = CommunicationHeader("workerA", [HeaderRequest("database")])
    session_ids = manager.process_header(header).unwrap()
    sid = session_ids[0]
    
    # Active -> Suspended
    assert manager.suspend_session(sid).is_ok()
    assert manager.session_registry.get_session(sid).state == SessionState.SUSPENDED
    
    # Suspended -> Active
    assert manager.resume_session(sid).is_ok()
    assert manager.session_registry.get_session(sid).state == SessionState.ACTIVE
    
    # Active -> Closing -> Destroyed
    assert manager.close_session(sid).is_ok()
    assert manager.session_registry.get_session(sid) is None

def test_illegal_lifecycle(manager):
    header = CommunicationHeader("workerA", [HeaderRequest("database")])
    sid = manager.process_header(header).unwrap()[0]
    
    # Active -> Destroyed (Illegal, must go through Closing)
    sess = manager.session_registry.get_session(sid)
    res = sess.transition(SessionState.DESTROYED)
    assert res.is_err()
    assert isinstance(res.error, SessionStateError)

def test_concurrent_sessions(manager):
    """Ensure SessionRegistry handles multiple threads creating sessions."""
    def create_batch():
        for _ in range(10):
            header = CommunicationHeader("workerA", [HeaderRequest("database")])
            manager.process_header(header).unwrap()
            
    threads = [threading.Thread(target=create_batch) for _ in range(10)]
    for t in threads: t.start()
    for t in threads: t.join()
    
    # 10 threads * 10 sessions = 100 sessions
    active = manager.session_registry._active_sessions
    assert len(active) == 100
