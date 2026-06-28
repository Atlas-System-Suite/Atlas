from abc import ABC, abstractmethod
from typing import Dict, Optional, Callable
from dataclasses import dataclass
import threading
import queue

from .diagnostics import Result, AtlasError, Severity

class TransportError(AtlasError):
    def __init__(self, message: str, context: Optional[Dict[str, str]] = None):
        super().__init__(code="ERR_TRANSPORT", severity=Severity.RECOVERABLE, message=message, context=context or {})

@dataclass(frozen=True)
class TransportPayload:
    """
    The fundamental unit of the Transport Layer.
    Contains strictly raw bytes. No capability semantics.
    """
    source_id: str
    target_id: str
    data: bytes

class TransportStrategy(ABC):
    """
    Abstract interface for moving bytes between workers.
    """
    @abstractmethod
    def send(self, payload: TransportPayload) -> Result[None, TransportError]:
        pass

    @abstractmethod
    def register_listener(self, worker_id: str, callback: Callable[[TransportPayload], None]) -> None:
        pass
        
    @abstractmethod
    def deregister_listener(self, worker_id: str) -> None:
        pass


class InMemoryTransport(TransportStrategy):
    """
    Thread-safe, non-blocking in-memory transport using Python queues.
    Suitable for workers running in the same process.
    """
    def __init__(self):
        self._listeners: Dict[str, Callable[[TransportPayload], None]] = {}
        self._lock = threading.Lock()
        
        # We use a dedicated thread to dispatch messages so `send()` never blocks the caller
        self._message_queue: queue.Queue = queue.Queue()
        self._running = True
        self._dispatcher = threading.Thread(target=self._dispatch_loop, daemon=True, name="Atlas-InMemoryTransport")
        self._dispatcher.start()

    def send(self, payload: TransportPayload) -> Result[None, TransportError]:
        """Enqueues a payload for delivery. Returns immediately."""
        with self._lock:
            if payload.target_id not in self._listeners:
                return Result.err(TransportError(
                    f"No listener registered for target {payload.target_id}",
                    {"source": payload.source_id, "target": payload.target_id}
                ))
                
        self._message_queue.put(payload)
        return Result.ok(None)

    def register_listener(self, worker_id: str, callback: Callable[[TransportPayload], None]) -> None:
        with self._lock:
            self._listeners[worker_id] = callback

    def deregister_listener(self, worker_id: str) -> None:
        with self._lock:
            if worker_id in self._listeners:
                del self._listeners[worker_id]

    def _dispatch_loop(self):
        while self._running:
            try:
                # Block for 0.1s to allow clean shutdown
                payload = self._message_queue.get(timeout=0.1)
                
                with self._lock:
                    cb = self._listeners.get(payload.target_id)
                
                if cb:
                    try:
                        cb(payload)
                    except Exception as e:
                        # Transport layer should not crash if a worker's listener throws
                        # In a real system, this would trigger an EventBus error
                        pass
                
                self._message_queue.task_done()
            except queue.Empty:
                continue

    def shutdown(self):
        """Cleanly shuts down the dispatcher thread."""
        self._running = False
        self._dispatcher.join(timeout=1.0)
