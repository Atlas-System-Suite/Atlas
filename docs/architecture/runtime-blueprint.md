# Atlas Runtime Blueprint (v1)

This document is the definitive implementation blueprint for the Atlas Runtime (Phase 1). It translates the frozen v1.0 Execution Model into a concrete, language-agnostic implementation plan.

---

## 1. Build Order & Dependency Graph

To minimize circular dependencies, implementation must follow a strict bottom-up approach.

```text
1. Manifest Loader & Dynamic Loader
   ↓ (Provides structure & code loading)
2. Global Registry
   ↓ (Stores runtime facts)
3. Worker Manager & Capability Resolver
   ↓ (Manages instances & capabilities)
4. Transport Layer & Translation Layer
   ↓ (Manages raw I/O & deserialization)
5. Session Manager
   ↓ (Establishes bindings)
6. Invocation System & Scheduler
   ↓ (Manages execution context)
7. Room Manager
   ↓ (Orchestrates collaboration)
8. Runtime Core
   (Coordinates everything)
```

---

## 2. Milestones

**Phase 1.1: Foundations**
- Manifest Loader, Dynamic Loader, Global Registry.
- *Goal:* Atlas can read `worker.yaml` files and index available capabilities in memory.

**Phase 1.2: Execution Primitives**
- Worker Manager, Capability Resolver.
- *Goal:* Atlas can instantiate Workers and resolve dependency graphs.

**Phase 1.3: The Data Plane**
- Transport Layer, Translation Layer, Session Manager.
- *Goal:* Two Workers can establish a binding and exchange primitive messages.

**Phase 1.4: Invocations & Rooms**
- Invocation System, Scheduler, Room Manager.
- *Goal:* Workers collaborate within isolated Room contexts, executing scheduled Invocations.

**Phase 1.5: The Core Orchestrator**
- Runtime Core integration, CLI entry point.
- *Goal:* End-to-end boot, resolution, room execution, and graceful shutdown.

---

## 3. Subsystem Specifications

*Note: All APIs are defined using language-agnostic interface pseudocode.*

### 3.1 Manifest Loader
**Purpose:** Reads and validates `worker.yaml` files.
**Responsibilities:** Parsing YAML/JSON, schema validation, injecting defaults.
**Public API:** `parse(path: String) -> WorkerManifest`
**Internal APIs:** `_validate_schema(data: Object) -> Result`
**Dependencies:** File I/O, Schema Validator (e.g., JSONSchema).
**Data Structures:** `WorkerManifest`, `ExportDefinition`, `ImportDefinition`.
**Failure Scenarios:** Missing files, invalid schemas (Fail-Fast during boot).

### 3.2 Dynamic Loader
**Purpose:** Loads Worker code into memory.
**Responsibilities:** OS-level dynamic loading (DLL, .so, Python imports), verifying entry points.
**Public API:** `load_worker(path: String, lang: String) -> WorkerInstance`
**Internal APIs:** `_load_python()`, `_load_native()`
**Dependencies:** OS Loader, Manifest Loader.
**Failure Scenarios:** Missing binaries, syntax errors, missing exported symbols.

### 3.3 Global Registry
**Purpose:** The central macro-state repository.
**Responsibilities:** Tracking all discovered Models, Workers, and active Rooms.
**Public API:** 
- `register_worker(manifest: WorkerManifest)`
- `find_workers_by_capability(cap: String) -> List<WorkerId>`
- `get_active_rooms() -> List<RoomId>`
**Dependencies:** Manifest Loader.
**Data Structures:** Thread-safe HashMaps/Dictionaries.
**Concurrency Model:** Must use R/W locks to prevent race conditions during dynamic Worker installation.

### 3.4 Capability Resolver
**Purpose:** Matches Worker requirements to exports.
**Responsibilities:** Topological sorting of dependencies, verifying version constraints.
**Public API:** `resolve_graph(required: List<ImportDefinition>) -> ResolutionGraph`
**Dependencies:** Global Registry.
**State Machines:** `Unresolved -> Resolving -> Satisfied | Failed`.
**Failure Scenarios:** Missing dependencies, circular dependencies, version conflicts.

### 3.5 Worker Manager
**Purpose:** Manages the lifecycle of Worker instances.
**Responsibilities:** Enforcing resource sharing policies (Singleton vs Pool), starting/stopping Workers.
**Public API:** 
- `get_or_create_instance(worker_id: String, room_id: String) -> WorkerRef`
- `pause_worker(worker_id: String)`
**Dependencies:** Dynamic Loader, Global Registry.
**State Machines:** (Worker Lifecycle) `Initialized -> Started -> Paused -> Stopped -> Disposed`.

### 3.6 Transport Layer
**Purpose:** Handles the physical movement of bytes.
**Responsibilities:** Managing TCP sockets, Shared Memory buffers, or Unix Domain Sockets.
**Public API:** 
- `create_channel(transport_type: String) -> (Tx, Rx)`
- `send(tx: Tx, data: Bytes)`
**Dependencies:** OS Networking / IPC.
**Failure Scenarios:** Broken pipes, connection timeouts, OOM on buffer allocation.
**Future Extensions:** WebRTC, Bluetooth, CAN bus.

### 3.7 Translation Layer
**Purpose:** Translates data structures between languages.
**Responsibilities:** Serializing objects into language-agnostic formats (e.g., Protobuf, JSON, Arrow) and back.
**Public API:** `translate(data: Object, format: String) -> Bytes`
**Dependencies:** Serialization libraries.

### 3.8 Session Manager
**Purpose:** Establishes communication Bindings.
**Responsibilities:** Negotiating the Transport and Translation layers between two Workers.
**Public API:** `establish_session(source: WorkerRef, target: WorkerRef, capability: String) -> Binding`
**Dependencies:** Transport Layer, Translation Layer, Worker Manager.
**Data Structures:** `Session`, `Binding`.
**Failure Scenarios:** Target worker refuses connection, incompatible transport mechanisms.

### 3.9 Invocation System
**Purpose:** Represents a single execution request.
**Responsibilities:** Wrapping a Session payload into a trackable, async invocation.
**Public API:** `invoke(binding: Binding, payload: Object) -> Future<Response>`
**Internal APIs:** `_track_promise(id: String)`
**Dependencies:** Session Manager.
**Concurrency Model:** Non-blocking Futures/Promises.

### 3.10 Scheduler
**Purpose:** Routes Invocations to Workers based on policy.
**Responsibilities:** Managing thread pools, async event loops, or queues for Workers.
**Public API:** `enqueue_invocation(worker_id: String, invocation: Invocation)`
**Dependencies:** Invocation System, Worker Manager.
**Concurrency Model:** High-throughput async queues (e.g., MPSC channels).

### 3.11 Room Manager (The Steward)
**Purpose:** Orchestrates collaboration contexts.
**Responsibilities:** Creating Rooms, managing the Room Registry (execution cache), and handling Room-level failures.
**Public API:**
- `create_room(host: WorkerRef) -> RoomId`
- `freeze_room(room_id: String)`
- `destroy_room(room_id: String)`
**Internal APIs:** `_sync_room_registry()`
**Dependencies:** Session Manager, Global Registry, Scheduler.
**Data Structures:** `RoomRegistry`, `RoomState`.
**State Machines:** (Room Lifecycle) `Created -> Resolving -> Active -> Frozen -> Recovering -> Draining -> Destroyed`.
**Failure Scenarios:** Worker crash cascades (triggers `Frozen` state).

### 3.12 Runtime Core
**Purpose:** The ultimate coordinator.
**Responsibilities:** Boot sequence, shutdown sequence, signal handling (SIGINT/SIGTERM).
**Public API:** `boot()`, `shutdown()`
**Dependencies:** ALL subsystems.

---

## 4. Testing Strategy

Atlas testing must be rigorous and strictly decoupled from business logic.

- **Unit Tests:** Every subsystem tested in absolute isolation with mocked dependencies (e.g., testing `CapabilityResolver` against a fake Registry).
- **Integration Tests:** Verifying the handoff between layers (e.g., `Transport` -> `Translation` -> `Session`).
- **Language Compatibility Tests:** (Phase 1.3+) Testing a mock Python Worker binding to a mock Rust Worker over IPC.
- **Room Tests:** Verifying that the Room Steward correctly isolates execution caches and prevents cross-room data leaks.
- **Failure Tests (Chaos):** Simulating Worker segfaults, OOM errors, and broken pipes to guarantee the Room Manager transitions to `Frozen` gracefully without taking down the Global Runtime.
- **Stress & Concurrency Tests:** Flooding the Scheduler with 1,000,000 Invocations to ensure the Global Registry locks do not create a bottleneck.
- **Embedded Tests:** (Future) Running the core on constrained memory profiles to validate zero-allocation paths in the Transport layer.
