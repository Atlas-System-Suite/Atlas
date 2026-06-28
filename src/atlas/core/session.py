from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import uuid
import threading
import time

from .diagnostics import Result, SessionStateError, SessionNegotiationError, LookupError
from .registry import GlobalRegistry
from .translation import TranslationResolver, TranslationChain
from .transport import TransportStrategy
from .manifest import RwLock

# ---------------------------------------------------------
# Header Protocol
# ---------------------------------------------------------
@dataclass(frozen=True)
class HeaderRequest:
    capability: str
    optional: bool = False

@dataclass(frozen=True)
class CommunicationHeader:
    source_worker_id: str
    requests: List[HeaderRequest]

# ---------------------------------------------------------
# Data Structures
# ---------------------------------------------------------
class SessionState(Enum):
    CREATED = "Created"
    NEGOTIATING = "Negotiating"
    ESTABLISHED = "Established"
    ACTIVE = "Active"
    IDLE = "Idle"
    SUSPENDED = "Suspended"
    CLOSING = "Closing"
    DESTROYED = "Destroyed"

class SessionType(Enum):
    DIRECT = "Direct"
    OBSERVER = "Observer"
    BROADCAST = "Broadcast"
    CONTROL = "Control"
    INTERNAL = "Internal"

@dataclass(frozen=True)
class Binding:
    session_id: str
    source_worker: str
    target_worker: str
    capability: str

class ManagedSession:
    """Thread-safe lifecycle manager for a single Session."""
    def __init__(self, session_id: str, binding: Binding, session_type: SessionType):
        self.session_id = session_id
        self.binding = binding
        self.session_type = session_type
        
        self.state = SessionState.CREATED
        self.channel_id: Optional[str] = None
        self.translation_chain: Optional[TranslationChain] = None
        
        self.created_at = time.time()
        self._lock = threading.Lock()

    def transition(self, new_state: SessionState) -> Result[None, Exception]:
        """Strict state machine logic for Session Lifecycle."""
        with self._lock:
            # Valid transitions
            valid_moves = {
                SessionState.CREATED: [SessionState.NEGOTIATING, SessionState.CLOSING],
                SessionState.NEGOTIATING: [SessionState.ESTABLISHED, SessionState.CLOSING],
                SessionState.ESTABLISHED: [SessionState.ACTIVE, SessionState.CLOSING],
                SessionState.ACTIVE: [SessionState.IDLE, SessionState.SUSPENDED, SessionState.CLOSING],
                SessionState.IDLE: [SessionState.ACTIVE, SessionState.SUSPENDED, SessionState.CLOSING],
                SessionState.SUSPENDED: [SessionState.IDLE, SessionState.ACTIVE, SessionState.CLOSING],
                SessionState.CLOSING: [SessionState.DESTROYED],
                SessionState.DESTROYED: []
            }
            
            if new_state not in valid_moves[self.state]:
                return Result.err(SessionStateError(
                    f"Illegal session transition: {self.state.name} -> {new_state.name}"
                ))
            
            self.state = new_state
            return Result.ok(None)

# ---------------------------------------------------------
# Session Registry
# ---------------------------------------------------------
class SessionRegistry:
    """In-memory index of all active and closed sessions."""
    def __init__(self):
        self._active_sessions: Dict[str, ManagedSession] = {}
        self._closed_sessions: Dict[str, ManagedSession] = {}
        
        # Capability bindings: capability -> List[session_id]
        self._bindings: Dict[str, List[str]] = {}
        self._lock = RwLock()

    def register_session(self, session: ManagedSession) -> None:
        self._lock.acquire_write()
        try:
            self._active_sessions[session.session_id] = session
            cap = session.binding.capability
            if cap not in self._bindings:
                self._bindings[cap] = []
            self._bindings[cap].append(session.session_id)
        finally:
            self._lock.release_write()

    def unregister_session(self, session_id: str) -> None:
        self._lock.acquire_write()
        try:
            if session_id in self._active_sessions:
                sess = self._active_sessions[session_id]
                del self._active_sessions[session_id]
                self._closed_sessions[session_id] = sess
                
                cap = sess.binding.capability
                if cap in self._bindings and session_id in self._bindings[cap]:
                    self._bindings[cap].remove(session_id)
        finally:
            self._lock.release_write()

    def get_session(self, session_id: str) -> Optional[ManagedSession]:
        self._lock.acquire_read()
        try:
            return self._active_sessions.get(session_id)
        finally:
            self._lock.release_read()

# ---------------------------------------------------------
# Session Manager
# ---------------------------------------------------------
class SessionManager:
    """
    The orchestrator that bridges Execution Planning, Transport, and Translation.
    Creates and maintains Sessions without running any business logic.
    """
    def __init__(self, global_registry: GlobalRegistry, translation_resolver: TranslationResolver, transport: TransportStrategy):
        self._global_registry = global_registry
        self._translation_resolver = translation_resolver
        self._transport = transport
        self.session_registry = SessionRegistry()

    def process_header(self, header: CommunicationHeader) -> Result[List[str], Exception]:
        """
        Resolves a Header Protocol request into Active Sessions.
        """
        source_worker_id = header.source_worker_id
        source_worker = self._global_registry.get_worker(source_worker_id)
        if not source_worker:
            return Result.err(LookupError(f"Source worker {source_worker_id} not found in Registry."))
            
        source_format = source_worker.manifest.communication.default_format
        created_session_ids = []
        
        for request in header.requests:
            # 1. Capability Discovery
            # We assume ExecutionPlanner previously validated topology, so we just grab the first provider
            # In a full Room implementation, we would query the Room's assigned providers.
            providers = self._global_registry.get_workers_by_capability(request.capability)
            if not providers:
                if request.optional:
                    continue
                return Result.err(SessionNegotiationError(f"No providers found for required capability: {request.capability}"))
                
            target_worker_id = providers[0]
            target_worker = self._global_registry.get_worker(target_worker_id)
            target_format = target_worker.manifest.communication.default_format
            
            # Create Session
            session_id = str(uuid.uuid4())
            binding = Binding(session_id, source_worker_id, target_worker_id, request.capability)
            session = ManagedSession(session_id, binding, SessionType.DIRECT)
            
            # Transition: CREATED -> NEGOTIATING
            session.transition(SessionState.NEGOTIATING).unwrap()
            
            # 2. Translation Negotiation
            trans_res = self._translation_resolver.resolve_translation(source_format, target_format)
            if trans_res.is_err():
                session.transition(SessionState.CLOSING).unwrap()
                session.transition(SessionState.DESTROYED).unwrap()
                if request.optional:
                    continue
                return Result.err(SessionNegotiationError(f"Translation failed for {request.capability}: {trans_res.error.message}"))
                
            session.translation_chain = trans_res.unwrap()
            
            # 3. Transport Allocation
            channel_id = f"chan_{session_id}"
            transp_res = self._transport.create_channel(channel_id)
            if transp_res.is_err():
                return Result.err(transp_res.error)
                
            session.channel_id = channel_id
            
            # 4. Finalize
            session.transition(SessionState.ESTABLISHED).unwrap()
            session.transition(SessionState.ACTIVE).unwrap()
            
            self.session_registry.register_session(session)
            created_session_ids.append(session_id)
            
        return Result.ok(created_session_ids)

    def close_session(self, session_id: str) -> Result[None, Exception]:
        session = self.session_registry.get_session(session_id)
        if not session:
            return Result.err(LookupError(f"Session {session_id} not active"))
            
        res = session.transition(SessionState.CLOSING)
        if res.is_err(): return res
        
        # Cleanup transport channel
        if session.channel_id:
            self._transport.close(session.channel_id)
            
        session.transition(SessionState.DESTROYED).unwrap()
        self.session_registry.unregister_session(session_id)
        return Result.ok(None)

    def suspend_session(self, session_id: str) -> Result[None, Exception]:
        session = self.session_registry.get_session(session_id)
        if not session: return Result.err(LookupError("Session not found"))
        return session.transition(SessionState.SUSPENDED)

    def resume_session(self, session_id: str) -> Result[None, Exception]:
        session = self.session_registry.get_session(session_id)
        if not session: return Result.err(LookupError("Session not found"))
        
        # Can only resume from SUSPENDED
        if session.state != SessionState.SUSPENDED:
            return Result.err(SessionStateError("Can only resume a suspended session"))
            
        return session.transition(SessionState.ACTIVE)
