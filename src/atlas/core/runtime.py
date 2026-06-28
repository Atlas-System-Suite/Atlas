import threading
import time
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional

from .diagnostics import Result, RuntimeStateError

# Subsystem Imports
from .registry import GlobalRegistry
from .worker_manager import WorkerManager
from .loader import DynamicLoader
from .resolver import CapabilityResolver
from .planner import ExecutionPlanner
from .transport import InMemoryTransport
from .translation import TranslationResolver
from .session import SessionManager
from .invocation import InvocationEngine
from .room import RoomManager

# ---------------------------------------------------------
# Configuration & State
# ---------------------------------------------------------
class RuntimeState(Enum):
    UNINITIALIZED = "Uninitialized"
    BOOTING = "Booting"
    READY = "Ready"
    SHUTTING_DOWN = "ShuttingDown"
    SHUTDOWN = "Shutdown"
    FAILED = "Failed"

@dataclass(frozen=True)
class RuntimeConfig:
    max_rooms: int = 1000
    max_room_depth: int = 5
    telemetry_enabled: bool = True

class SchedulerStub:
    """A placeholder for the Phase 2 Scheduler."""
    def __init__(self, invocation_engine: InvocationEngine):
        self.engine = invocation_engine
        
    def start(self) -> None:
        pass
        
    def stop(self) -> None:
        pass

# ---------------------------------------------------------
# Atlas Runtime Core
# ---------------------------------------------------------
class AtlasRuntime:
    """
    The Supreme Orchestrator.
    Binds all Atlas execution primitives together.
    Owns absolutely zero business logic.
    """
    def __init__(self, config: RuntimeConfig):
        self.config = config
        self._state = RuntimeState.UNINITIALIZED
        self._lock = threading.Lock()
        
        # Subsystems
        self._registry: Optional[GlobalRegistry] = None
        self._worker_manager: Optional[WorkerManager] = None
        self._capability_resolver: Optional[CapabilityResolver] = None
        self._execution_planner: Optional[ExecutionPlanner] = None
        self._transport: Optional[InMemoryTransport] = None
        self._translation_resolver: Optional[TranslationResolver] = None
        self._session_manager: Optional[SessionManager] = None
        self._invocation_engine: Optional[InvocationEngine] = None
        self._scheduler: Optional[SchedulerStub] = None
        self._room_manager: Optional[RoomManager] = None

    # ---------------------------------------------------------
    # Accessors (Read-Only)
    # ---------------------------------------------------------
    @property
    def state(self) -> RuntimeState:
        return self._state

    def get_registry(self) -> GlobalRegistry:
        self._ensure_ready()
        return self._registry

    def get_worker_manager(self) -> WorkerManager:
        self._ensure_ready()
        return self._worker_manager
        
    def get_session_manager(self) -> SessionManager:
        self._ensure_ready()
        return self._session_manager
        
    def get_invocation_engine(self) -> InvocationEngine:
        self._ensure_ready()
        return self._invocation_engine
        
    def get_room_manager(self) -> RoomManager:
        self._ensure_ready()
        return self._room_manager

    def _ensure_ready(self):
        if self._state != RuntimeState.READY:
            raise RuntimeError(f"Atlas is not ready. Current state: {self._state}")

    # ---------------------------------------------------------
    # Boot Sequence
    # ---------------------------------------------------------
    def boot(self) -> Result[None, Exception]:
        """
        Deterministic, strict initialization sequence.
        Fails fast if any subsystem cannot initialize.
        """
        with self._lock:
            if self._state != RuntimeState.UNINITIALIZED:
                return Result.err(RuntimeStateError(f"Cannot boot from state {self._state.name}"))
                
            self._state = RuntimeState.BOOTING
            
            try:
                # 1. Registry
                self._registry = GlobalRegistry()
                
                # 2. Worker Manager
                self._loader = DynamicLoader()
                self._worker_manager = WorkerManager(self._loader, self._registry)
                
                # 3. Resolution & Planning
                self._capability_resolver = CapabilityResolver(self._registry)
                self._execution_planner = ExecutionPlanner(self._registry)
                
                # 4. Communication Layer
                self._transport = InMemoryTransport()
                self._translation_resolver = TranslationResolver(self._registry)
                
                # 5. Session Manager
                self._session_manager = SessionManager(
                    self._registry, self._translation_resolver, self._transport
                )
                
                # 6. Invocation Engine
                self._invocation_engine = InvocationEngine()
                
                # 7. Scheduler (Phase 2 Stub)
                self._scheduler = SchedulerStub(self._invocation_engine)
                self._scheduler.start()
                
                # 8. Room Manager
                self._room_manager = RoomManager(
                    max_rooms=self.config.max_rooms, 
                    max_depth=self.config.max_room_depth
                )
                
                self._state = RuntimeState.READY
                return Result.ok(None)
                
            except Exception as e:
                self._state = RuntimeState.FAILED
                return Result.err(e)

    # ---------------------------------------------------------
    # Shutdown Sequence
    # ---------------------------------------------------------
    def shutdown(self) -> Result[None, Exception]:
        """
        Graceful teardown sequence ensuring no orphaned state.
        """
        with self._lock:
            if self._state not in (RuntimeState.READY, RuntimeState.FAILED):
                return Result.err(RuntimeStateError("Can only shutdown from READY or FAILED state"))
                
            self._state = RuntimeState.SHUTTING_DOWN
            
            try:
                # 1. Stop Scheduler (stops taking new work)
                if self._scheduler:
                    self._scheduler.stop()
                
                # 2. Drain Rooms
                if self._room_manager:
                    room_ids = list(self._room_manager._rooms.keys())
                    for rid in room_ids:
                        self._room_manager.destroy_room(rid)
                        
                # 3. Close Sessions
                if self._session_manager:
                    sess_ids = list(self._session_manager.session_registry._active_sessions.keys())
                    for sid in sess_ids:
                        self._session_manager.close_session(sid)
                        
                # 4. Shutdown Transport Channel
                if self._transport:
                    self._transport.shutdown()
                
                # 5. Clear Registry
                if self._registry:
                    self._registry._workers.clear()
                    self._registry._capabilities_index.clear()
                    
                self._state = RuntimeState.SHUTDOWN
                return Result.ok(None)
                
            except Exception as e:
                self._state = RuntimeState.FAILED
                return Result.err(e)

    # ---------------------------------------------------------
    # Diagnostics & Health
    # ---------------------------------------------------------
    def get_health_summary(self) -> Dict[str, Any]:
        """Returns a snapshot of the runtime health for external monitoring."""
        if self._state != RuntimeState.READY:
            return {"status": self._state.name, "healthy": False}
            
        return {
            "status": self._state.name,
            "healthy": True,
            "metrics": {
                "active_workers": len(self._registry._workers),
                "active_rooms": len(self._room_manager._rooms),
                "active_sessions": len(self._session_manager.session_registry._active_sessions),
                "active_invocations": len(self._invocation_engine.registry._active_invocations)
            }
        }
