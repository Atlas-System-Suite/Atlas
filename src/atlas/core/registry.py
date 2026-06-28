from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass

from .diagnostics import Result, IdCollisionError, LookupError
from .loader import WorkerInstance
from .manifest import RwLock

class HealthStatus(Enum):
    STARTING = "Starting"
    HEALTHY = "Healthy"
    DEGRADED = "Degraded"
    DEAD = "Dead"

@dataclass
class WorkerMetrics:
    status: HealthStatus
    uptime_ms: int = 0
    active_invocations: int = 0


class GlobalRegistry:
    def __init__(self):
        # The core storage tables (O(1) HashMaps)
        self._workers: Dict[str, WorkerInstance] = {}
        
        # Indices
        self._capabilities_index: Dict[str, List[str]] = {}
        self._roles_index: Dict[str, List[str]] = {}
        self._translation_index: Dict[str, List[str]] = {}  # source_format -> List[worker_id]
        
        # Generation counters for cache invalidation
        self.translation_generation = 0
        
        # Health Tracking
        self._metrics: Dict[str, WorkerMetrics] = {}
        
        # Concurrency Protection
        self._lock = RwLock()

    # ---------------------------------------------------------
    # Mutators (Write Locks)
    # ---------------------------------------------------------

    def register_worker(self, instance: WorkerInstance) -> Result[None, Exception]:
        self._lock.acquire_write()
        try:
            worker_id = instance.manifest.id
            if worker_id in self._workers:
                return Result.err(IdCollisionError(f"Worker '{worker_id}' is already registered"))

            # Register core instance
            self._workers[worker_id] = instance
            self._metrics[worker_id] = WorkerMetrics(status=HealthStatus.STARTING)

            # Build Capability Index
            for export in instance.manifest.exports:
                cap_name = export.capability_name
                if cap_name not in self._capabilities_index:
                    self._capabilities_index[cap_name] = []
                if worker_id not in self._capabilities_index[cap_name]:
                    self._capabilities_index[cap_name].append(worker_id)

            # Build Role Index
            for role in instance.manifest.roles:
                if role not in self._roles_index:
                    self._roles_index[role] = []
                if worker_id not in self._roles_index[role]:
                    self._roles_index[role].append(worker_id)
                    
            # Build Translation Index
            if instance.manifest.translations:
                for trans in instance.manifest.translations:
                    if trans.source_format not in self._translation_index:
                        self._translation_index[trans.source_format] = []
                    if worker_id not in self._translation_index[trans.source_format]:
                        self._translation_index[trans.source_format].append(worker_id)
                self.translation_generation += 1

            return Result.ok(None)
        finally:
            self._lock.release_write()

    def deregister_worker(self, worker_id: str) -> Result[None, Exception]:
        self._lock.acquire_write()
        try:
            if worker_id not in self._workers:
                return Result.ok(None) # Already gone

            instance = self._workers[worker_id]

            # Prune Capability Index
            for export in instance.manifest.exports:
                cap_name = export.capability_name
                if cap_name in self._capabilities_index:
                    if worker_id in self._capabilities_index[cap_name]:
                        self._capabilities_index[cap_name].remove(worker_id)
                    # Clean up empty lists to prevent memory leaks over time
                    if not self._capabilities_index[cap_name]:
                        del self._capabilities_index[cap_name]

            # Prune Role Index
            for role in instance.manifest.roles:
                if role in self._roles_index and worker_id in self._roles_index[role]:
                    self._roles_index[role].remove(worker_id)
                    if not self._roles_index[role]:
                        del self._roles_index[role]
                        
            if instance.manifest.translations:
                for trans in instance.manifest.translations:
                    if trans.source_format in self._translation_index and worker_id in self._translation_index[trans.source_format]:
                        self._translation_index[trans.source_format].remove(worker_id)
                        if not self._translation_index[trans.source_format]:
                            del self._translation_index[trans.source_format]
                self.translation_generation += 1

            del self._workers[worker_id]
            del self._metrics[worker_id]
            
            return Result.ok(None)
        finally:
            self._lock.release_write()

    def update_worker_health(self, worker_id: str, status: HealthStatus) -> Result[None, Exception]:
        # Health updates are frequent, so we optimize with a targeted write lock if possible,
        # but for simplicity in v1.0, we use the global write lock.
        self._lock.acquire_write()
        try:
            if worker_id in self._metrics:
                self._metrics[worker_id].status = status
            return Result.ok(None)
        finally:
            self._lock.release_write()

    # ---------------------------------------------------------
    # Accessors (Read Locks)
    # ---------------------------------------------------------

    def get_metrics(self, worker_id: str) -> Optional[WorkerMetrics]:
        self._lock.acquire_read()
        try:
            return self._metrics.get(worker_id)
        finally:
            self._lock.release_read()
            
    def get_workers_by_capability(self, capability: str) -> List[str]:
        self._lock.acquire_read()
        try:
            return list(self._capabilities_index.get(capability, []))
        finally:
            self._lock.release_read()

    def get_worker(self, worker_id: str) -> Optional[WorkerInstance]: # using python Optional typing concept
        self._lock.acquire_read()
        try:
            return self._workers.get(worker_id)
        finally:
            self._lock.release_read()

    def get_workers_by_role(self, role: str) -> List[WorkerInstance]:
        self._lock.acquire_read()
        try:
            worker_ids = self._roles_index.get(role, [])
            return [self._workers[w_id] for w_id in worker_ids if w_id in self._workers]
        finally:
            self._lock.release_read()

    def find_providers_for_capability(self, capability: str) -> Result[List[str], Exception]:
        self._lock.acquire_read()
        try:
            providers = self._capabilities_index.get(capability, [])
            if not providers:
                return Result.err(LookupError(f"No providers found for capability: {capability}"))
            return Result.ok(list(providers)) # Return a copy to prevent external mutation
        finally:
            self._lock.release_read()
