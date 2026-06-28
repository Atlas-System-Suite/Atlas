import threading
from enum import Enum
from typing import Dict, List, Optional
from collections import deque

from .diagnostics import Result, IllegalStateTransitionError, LoadError
from .manifest import WorkerManifest, RwLock
from .loader import DynamicLoader, WorkerInstance
from .registry import GlobalRegistry, HealthStatus


class WorkerState(Enum):
    INITIALIZED = "Initialized"
    LOADED = "Loaded"
    STARTING = "Starting"
    RUNNING = "Running"
    PAUSED = "Paused"
    STOPPING = "Stopping"
    STOPPED = "Stopped"
    DISPOSED = "Disposed"


# The Strict Transition Matrix
VALID_TRANSITIONS = {
    WorkerState.INITIALIZED: [WorkerState.LOADED, WorkerState.DISPOSED],
    WorkerState.LOADED: [WorkerState.STARTING, WorkerState.DISPOSED],
    WorkerState.STARTING: [WorkerState.RUNNING, WorkerState.STOPPING],
    WorkerState.RUNNING: [WorkerState.PAUSED, WorkerState.STOPPING],
    WorkerState.PAUSED: [WorkerState.RUNNING, WorkerState.STOPPING],
    WorkerState.STOPPING: [WorkerState.STOPPED],
    WorkerState.STOPPED: [WorkerState.STARTING, WorkerState.DISPOSED],
    WorkerState.DISPOSED: []
}

class ManagedWorker:
    """
    Wraps a WorkerInstance with lifecycle tracking.
    Uses a fine-grained lock to protect its own state transitions.
    """
    def __init__(self, instance_id: str, manifest: WorkerManifest):
        self.instance_id = instance_id
        self.manifest = manifest
        self.state = WorkerState.INITIALIZED
        self.worker_instance: Optional[WorkerInstance] = None
        self._lock = threading.Lock()

    def transition(self, new_state: WorkerState) -> Result[None, IllegalStateTransitionError]:
        with self._lock:
            if new_state not in VALID_TRANSITIONS[self.state]:
                err = IllegalStateTransitionError(
                    f"Cannot transition from {self.state.value} to {new_state.value}",
                    context={"worker_id": self.manifest.id, "instance_id": self.instance_id}
                )
                return Result.err(err)
            self.state = new_state
            return Result.ok(None)


class WorkerManager:
    """
    Owns Worker lifecycle, instantiation, and resource pooling.
    Does NOT execute logic, route messages, or resolve capabilities.
    """
    def __init__(self, loader: DynamicLoader, registry: GlobalRegistry):
        self._loader = loader
        self._registry = registry
        
        # Routing tables protected by global RwLock
        self._table_lock = RwLock()
        
        # Singletons: Mapping of worker_id -> ManagedWorker
        self._singletons: Dict[str, ManagedWorker] = {}
        
        # Pools: Mapping of worker_id -> List of ManagedWorkers
        self._pools: Dict[str, List[ManagedWorker]] = {}
        
        # Lookup table for quick reference to any ManagedWorker by its unique instance_id
        self._all_workers: Dict[str, ManagedWorker] = {}
        
        # Instance counter for unique IDs
        self._instance_counter = 0

    def _generate_instance_id(self, worker_id: str) -> str:
        self._instance_counter += 1
        return f"{worker_id}::{self._instance_counter}"

    def request_worker(self, manifest: WorkerManifest, source_path: str) -> Result[ManagedWorker, Exception]:
        """
        Requests a worker according to its sharing policy.
        Will spin up a new one or return an existing one.
        """
        policy = manifest.execution.policy.lower()
        
        if policy == "singleton":
            return self._request_singleton(manifest, source_path)
        elif policy == "pool" or policy == "parallel":
            return self._request_pooled(manifest, source_path)
        elif policy == "exclusive":
            return self._create_new_worker(manifest, source_path)
        else:
            return Result.err(LoadError(f"Unknown execution policy: {policy}"))

    def _request_singleton(self, manifest: WorkerManifest, source_path: str) -> Result[ManagedWorker, Exception]:
        self._table_lock.acquire_read()
        try:
            if manifest.id in self._singletons:
                return Result.ok(self._singletons[manifest.id])
        finally:
            self._table_lock.release_read()

        # If we reach here, we need to create it (requires write lock)
        self._table_lock.acquire_write()
        try:
            # Double check inside the write lock
            if manifest.id in self._singletons:
                return Result.ok(self._singletons[manifest.id])
                
            res = self._create_new_worker_unsafe(manifest, source_path)
            if res.is_err():
                return res
            
            managed = res.unwrap()
            self._singletons[manifest.id] = managed
            return Result.ok(managed)
        finally:
            self._table_lock.release_write()

    def _request_pooled(self, manifest: WorkerManifest, source_path: str) -> Result[ManagedWorker, Exception]:
        # For a basic v1.0 pool implementation, we just spin up a new instance if none are free.
        # Right now we just create a new one to simulate parallel capacity.
        self._table_lock.acquire_write()
        try:
            res = self._create_new_worker_unsafe(manifest, source_path)
            if res.is_err():
                return res
                
            managed = res.unwrap()
            if manifest.id not in self._pools:
                self._pools[manifest.id] = []
            self._pools[manifest.id].append(managed)
            return Result.ok(managed)
        finally:
            self._table_lock.release_write()

    def _create_new_worker(self, manifest: WorkerManifest, source_path: str) -> Result[ManagedWorker, Exception]:
        self._table_lock.acquire_write()
        try:
            return self._create_new_worker_unsafe(manifest, source_path)
        finally:
            self._table_lock.release_write()

    def _create_new_worker_unsafe(self, manifest: WorkerManifest, source_path: str) -> Result[ManagedWorker, Exception]:
        """Internal helper. Assumes table write lock is held."""
        instance_id = self._generate_instance_id(manifest.id)
        managed = ManagedWorker(instance_id, manifest)
        
        self._all_workers[instance_id] = managed
        
        # Load from disk
        load_res = self._loader.load_worker(manifest, source_path)
        if load_res.is_err():
            return Result.err(load_res.error)
            
        managed.worker_instance = load_res.unwrap()
        
        trans_res = managed.transition(WorkerState.LOADED)
        if trans_res.is_err():
            return Result.err(trans_res.error)
            
        # Push to Global Registry
        reg_res = self._registry.register_worker(managed.worker_instance)
        # Note: If registry fails (e.g. ID collision), we should ideally clean up, 
        # but the registry allows singletons, so we skip complex cleanup for v1.0.
        
        return Result.ok(managed)

    # ---------------------------------------------------------
    # Lifecycle Commands
    # ---------------------------------------------------------

    def start_worker(self, instance_id: str) -> Result[None, Exception]:
        self._table_lock.acquire_read()
        try:
            managed = self._all_workers.get(instance_id)
        finally:
            self._table_lock.release_read()
            
        if not managed:
            return Result.err(LoadError(f"Instance {instance_id} not found"))
            
        res = managed.transition(WorkerState.STARTING)
        if res.is_err(): return res
        
        # In a real implementation, we'd trigger the Worker's `on_start()` hook here
        # For now, we simulate success and move to RUNNING
        
        res = managed.transition(WorkerState.RUNNING)
        if res.is_ok():
            self._registry.update_worker_health(managed.manifest.id, HealthStatus.HEALTHY)
            
        return res

    def dispose_worker(self, instance_id: str) -> Result[None, Exception]:
        self._table_lock.acquire_write()
        try:
            managed = self._all_workers.get(instance_id)
            if not managed:
                return Result.err(LoadError(f"Instance {instance_id} not found"))
            
            # Force transition to DISPOSED from whatever state it is in (safely)
            # Typically you must STOP first.
            if managed.state not in [WorkerState.STOPPED, WorkerState.INITIALIZED, WorkerState.LOADED]:
                stop_res = managed.transition(WorkerState.STOPPING)
                if stop_res.is_ok():
                    managed.transition(WorkerState.STOPPED)
            
            res = managed.transition(WorkerState.DISPOSED)
            if res.is_err(): return res
            
            # Unload from memory
            if managed.worker_instance:
                self._loader.unload_worker(managed.manifest.id)
                self._registry.deregister_worker(managed.manifest.id)
            
            # Clean routing tables
            del self._all_workers[instance_id]
            if managed.manifest.id in self._singletons and self._singletons[managed.manifest.id] == managed:
                del self._singletons[managed.manifest.id]
            if managed.manifest.id in self._pools:
                if managed in self._pools[managed.manifest.id]:
                    self._pools[managed.manifest.id].remove(managed)
                    
            return Result.ok(None)
        finally:
            self._table_lock.release_write()
