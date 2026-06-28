import os
import threading
import time

from atlas.core.manifest import ManifestLoader
from atlas.core.loader import DynamicLoader
from atlas.core.registry import GlobalRegistry
from atlas.core.worker_manager import WorkerManager, WorkerState
from atlas.core.diagnostics import IllegalStateTransitionError

def test_legal_lifecycle():
    manifest_loader = ManifestLoader()
    worker_dir = os.path.join(os.path.dirname(__file__), "dummy_workers", "valid")
    manifest = manifest_loader.load_file(os.path.join(worker_dir, "worker.yaml")).unwrap()
    
    loader = DynamicLoader()
    registry = GlobalRegistry()
    manager = WorkerManager(loader, registry)
    
    # 1. Request (Transitions to LOADED)
    managed = manager.request_worker(manifest, worker_dir).unwrap()
    assert managed.state == WorkerState.LOADED
    
    # 2. Start (Transitions STARTING -> RUNNING)
    res = manager.start_worker(managed.instance_id)
    assert res.is_ok()
    assert managed.state == WorkerState.RUNNING
    
    # 3. Dispose (Transitions STOPPING -> STOPPED -> DISPOSED)
    res = manager.dispose_worker(managed.instance_id)
    assert res.is_ok()
    assert managed.state == WorkerState.DISPOSED
    
    # Verify memory is freed
    assert len(manager._all_workers) == 0

def test_illegal_lifecycle_jump():
    manifest_loader = ManifestLoader()
    worker_dir = os.path.join(os.path.dirname(__file__), "dummy_workers", "valid")
    manifest = manifest_loader.load_file(os.path.join(worker_dir, "worker.yaml")).unwrap()
    
    loader = DynamicLoader()
    registry = GlobalRegistry()
    manager = WorkerManager(loader, registry)
    
    managed = manager.request_worker(manifest, worker_dir).unwrap()
    assert managed.state == WorkerState.LOADED
    
    # Attempt illegal jump LOADED -> PAUSED
    res = managed.transition(WorkerState.PAUSED)
    assert res.is_err()
    assert isinstance(res.error, IllegalStateTransitionError)
    assert managed.state == WorkerState.LOADED

def test_singleton_concurrency_crush():
    """
    200 threads try to request the SAME singleton worker simultaneously.
    If thread-safety fails, multiple dynamic loads will occur or memory will leak.
    """
    manifest_loader = ManifestLoader()
    worker_dir = os.path.join(os.path.dirname(__file__), "dummy_workers", "valid")
    # Force singleton via hack for test
    manifest = manifest_loader.load_file(os.path.join(worker_dir, "worker.yaml")).unwrap()
    object.__setattr__(manifest.execution, "policy", "singleton")
    
    loader = DynamicLoader()
    registry = GlobalRegistry()
    manager = WorkerManager(loader, registry)
    
    results = []
    
    def request_thread():
        res = manager.request_worker(manifest, worker_dir)
        results.append(res)
        
    threads = []
    for _ in range(200):
        t = threading.Thread(target=request_thread)
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    # Verify
    successes = [r for r in results if r.is_ok()]
    assert len(successes) == 200
    
    # But there should only be ONE instance actually loaded
    instance_ids = set([r.unwrap().instance_id for r in successes])
    assert len(instance_ids) == 1
    assert len(manager._singletons) == 1
    assert len(manager._all_workers) == 1
