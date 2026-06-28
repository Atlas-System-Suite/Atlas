"""
Atlas Session Manager Demonstration
Demonstrates the orchestration of Capability Resolution, Translation Chaining,
and Transport Allocation into a unified Session Lifecycle.
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from atlas.core.manifest import WorkerManifest, ExecutionPolicy, CommunicationPolicy, ExportDefinition, TranslationDefinition
from atlas.core.registry import GlobalRegistry
from atlas.core.loader import WorkerInstance
from atlas.core.transport import InMemoryTransport
from atlas.core.translation import TranslationResolver
from atlas.core.session import SessionManager, CommunicationHeader, HeaderRequest, SessionState

def create_worker(id: str, cap: str, format: str) -> WorkerManifest:
    return WorkerManifest(
        id=id,
        name=id,
        version="1.0.0",
        language="python",
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
        language="system",
        roles=["translator"],
        execution=ExecutionPolicy("singleton"),
        communication=CommunicationPolicy([], [], default_format="internal"),
        imports=[],
        exports=[],
        translations=[TranslationDefinition(source, target, cost=1)]
    )

def run_demo():
    print("Initializing Atlas Session Manager and Subsystems...")
    reg = GlobalRegistry()
    trans_res = TranslationResolver(reg)
    transport = InMemoryTransport()
    manager = SessionManager(reg, trans_res, transport)
    
    # 1. Register Mock Workers
    print("\n[Registry] Registering Workers & Translators:")
    workers = [
        create_worker("DashboardWorker", "ui", "python"),          # Wants database
        create_worker("DatabaseWorker", "database", "rust"),       # Provides database
        create_translator("Py2Json", "python", "json"),
        create_translator("Json2Rust", "json", "rust"),
    ]
    for w in workers:
        print(f"  -> {w.id}")
        reg.register_worker(WorkerInstance(w.id, w, None))
        
    # 2. Worker Emits Header Protocol
    print("\n[Protocol] DashboardWorker emits Communication Header:")
    header = CommunicationHeader("DashboardWorker", [HeaderRequest("database")])
    print(f"  -> Requires: 'database'")
    
    # 3. Session Manager Orchestrates Negotiation
    print("\n[Session Manager] Processing Header...")
    res = manager.process_header(header)
    
    if res.is_err():
        print(f"Failed to establish sessions: {res.error}")
        return
        
    session_ids = res.unwrap()
    print(f"Success! Established {len(session_ids)} session(s).")
    
    # 4. Inspect the Resulting Session
    sess = manager.session_registry.get_session(session_ids[0])
    print("\n[Session Details]")
    print(f"  ID: {sess.session_id}")
    print(f"  State: {sess.state.value}")
    print(f"  Source: {sess.binding.source_worker} (python)")
    print(f"  Target: {sess.binding.target_worker} (rust)")
    print(f"  Capability: {sess.binding.capability}")
    print(f"  Channel: {sess.channel_id}")
    
    print("\n[Translation Chain Negotiated]")
    for t_id in sess.translation_chain.translators:
        print(f"  -> {t_id}")
        
    # 5. Teardown
    print("\n[Session Manager] Tearing down Session...")
    manager.close_session(sess.session_id)
    transport.shutdown()
    print("Done. State machine transitioned to DESTROYED.")

if __name__ == "__main__":
    run_demo()
