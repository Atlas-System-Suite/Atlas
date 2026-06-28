# Worker Lifecycle State Machine

The Worker Manager enforces a strict state machine to guarantee safety and thread concurrency. 

Every Worker traverses these states:

```mermaid
stateDiagram-v2
    [*] --> INITIALIZED: Discovered & Validated
    INITIALIZED --> LOADED: request_worker()
    INITIALIZED --> DISPOSED: dispose_worker()
    
    LOADED --> STARTING: start_worker()
    LOADED --> DISPOSED: dispose_worker()
    
    STARTING --> RUNNING: on_start() Success
    STARTING --> STOPPING: Shutdown Signal
    
    RUNNING --> PAUSED: Suspend
    RUNNING --> STOPPING: Shutdown Signal
    
    PAUSED --> RUNNING: Resume
    PAUSED --> STOPPING: Shutdown Signal
    
    STOPPING --> STOPPED: on_stop() Success
    
    STOPPED --> STARTING: start_worker()
    STOPPED --> DISPOSED: dispose_worker()
    
    DISPOSED --> [*]: Memory Freed
```

### Safety and Concurrency
Attempting to jump states illegally (e.g., `LOADED` directly to `PAUSED`) returns a `Result.err(IllegalStateTransitionError)` and prevents execution.

Because each `ManagedWorker` holds its own fine-grained lock, State transitions occur in parallel across the system. 
Worker A moving to `RUNNING` never blocks Worker B moving to `STOPPED`.
