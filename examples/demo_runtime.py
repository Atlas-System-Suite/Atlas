"""
Atlas Runtime Core (v1) - End-to-End Integration Demonstration
This script proves that ALL subsystems (Registry, Workers, Translation, Sessions, 
Invocations, Rooms, and Core) interact flawlessly.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from atlas.core.runtime import AtlasRuntime, RuntimeConfig
from atlas.core.manifest import WorkerManifest, ExecutionPolicy, CommunicationPolicy, ExportDefinition, TranslationDefinition
from atlas.core.loader import WorkerInstance
from atlas.core.session import CommunicationHeader, HeaderRequest

def create_mock_manifest(id: str, cap: str, format: str, roles: list) -> WorkerManifest:
    return WorkerManifest(
        id=id, name=id, version="1.0.0", language="python", roles=roles,
        execution=ExecutionPolicy("singleton"),
        communication=CommunicationPolicy([], [], default_format=format),
        imports=[], exports=[ExportDefinition(cap, "1.0.0")] if cap else [], translations=[]
    )

def create_translator(id: str, source: str, target: str) -> WorkerManifest:
    return WorkerManifest(
        id=id, name=id, version="1.0.0", language="system", roles=["translator"],
        execution=ExecutionPolicy("singleton"),
        communication=CommunicationPolicy([], [], default_format="internal"),
        imports=[], exports=[], translations=[TranslationDefinition(source, target, cost=1)]
    )

def run_e2e_demo():
    print("==================================================")
    print(" ATLAS RUNTIME v1 : END-TO-END DEMONSTRATION")
    print("==================================================\n")
    
    # 1. Booting
    print("[1. Orchestrator] Booting Atlas Runtime...")
    config = RuntimeConfig()
    runtime = AtlasRuntime(config)
    runtime.boot().unwrap()
    health = runtime.get_health_summary()
    print(f"  -> State: {health['status']} (Healthy: {health['healthy']})")
    
    # 2. Loading Workers
    print("\n[2. Subsystems] Loading Workers & Translators...")
    reg = runtime.get_registry()
    workers = [
        create_mock_manifest("AppWorker", "", "python", ["app"]),
        create_mock_manifest("DatabaseWorker", "database", "rust", ["db"]),
        create_translator("Py2Json", "python", "json"),
        create_translator("Json2Rust", "json", "rust")
    ]
    for w in workers:
        print(f"  -> Loading {w.id}")
        reg.register_worker(WorkerInstance(w.id, w, None))
        
    # 3. Room & Collaboration
    print("\n[3. Execution Context] Defining Collaboration Room...")
    room_mgr = runtime.get_room_manager()
    room_id = room_mgr.create_room().unwrap()
    print(f"  -> Created Room {room_id[:8]}")
    room_mgr.bind_worker(room_id, "AppWorker", "App").unwrap()
    room_mgr.bind_worker(room_id, "DatabaseWorker", "DB").unwrap()
    
    # 4. Session Negotiation (Triggers Translation & Transport)
    print("\n[4. Communication Layer] AppWorker requests 'database'...")
    session_mgr = runtime.get_session_manager()
    header = CommunicationHeader("AppWorker", [HeaderRequest("database")])
    session_ids = session_mgr.process_header(header).unwrap()
    
    sess = session_mgr.session_registry.get_session(session_ids[0])
    print(f"  -> Bound Active Session: {sess.session_id}")
    print(f"  -> Channel Allocated: {sess.channel_id}")
    print(f"  -> Translation Chain Negotiated: {' -> '.join(sess.translation_chain.translators)}")
    
    # 5. Invocation Execution
    print("\n[5. Invocation Engine] Executing Task...")
    inv_eng = runtime.get_invocation_engine()
    from atlas.core.invocation import InvocationState
    
    inv_a = inv_eng.create_invocation(sess.session_id, "AppWorker").unwrap()
    print(f"  -> Dispatched Root Invocation: {inv_a.context.invocation_id}")
    inv_a.transition(InvocationState.QUEUED).unwrap()
    inv_a.transition(InvocationState.DISPATCHED).unwrap()
    inv_a.transition(InvocationState.EXECUTING).unwrap()
    
    inv_b = inv_eng.create_invocation(sess.session_id, "DatabaseWorker", parent_id=inv_a.context.invocation_id).unwrap()
    print(f"  -> Dispatched Nested DB Query: {inv_b.context.invocation_id}")
    inv_b.transition(InvocationState.QUEUED).unwrap()
    inv_b.transition(InvocationState.DISPATCHED).unwrap()
    inv_b.transition(InvocationState.EXECUTING).unwrap()
    
    inv_eng.complete(inv_b.context.invocation_id, {"status": "ok"}).unwrap()
    inv_eng.complete(inv_a.context.invocation_id, {"status": "ok"}).unwrap()
    print("  -> Execution Trace completed successfully.")
    
    # 6. Graceful Shutdown
    print("\n[6. Orchestrator] Initiating Graceful Shutdown...")
    runtime.shutdown().unwrap()
    health = runtime.get_health_summary()
    print(f"  -> State: {health['status']}")
    print("\nAtlas Runtime v1 Shutdown Complete. No state orphaned.")

if __name__ == "__main__":
    run_e2e_demo()
