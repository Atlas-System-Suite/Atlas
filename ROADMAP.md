# Atlas Roadmap

Atlas development is structured by platform milestones, not programming language choices.

## Phase 0: Architecture Freeze (Complete)

- [x] Establish Core Architecture
- [x] Define Framework Specifications
- [x] Produce Design ADRs

## Phase 0.5: Worker Architecture Migration (Complete)

- [x] Consolidate Application/Provider into Workers
- [x] Introduce Models and Solon Toolchain
- [x] Strip messaging/data plane responsibilities from Runtime

## Phase 1: Core Foundation

- [ ] Error hierarchy and base exceptions
- [ ] Logger Protocol and default implementation
- [ ] Configuration Manager (YAML loading, validation, merging)
- [ ] Lifecycle Manager (state machine, transitions)
- [ ] Registry (component registration, lookup, validation)

## Phase 2: Solon and Models

- [ ] Define precise Model schema format
- [ ] Implement Solon CLI `validate` command
- [ ] Implement Solon code generation hooks (Mocks, tests)
- [ ] Implement Worker Manifest Parsing

## Phase 3: The Data Plane

- [ ] Design standard RPC / direct invocation protocols for Workers
- [ ] Design direct eventing specifications
- [ ] Create the first concrete Worker (e.g., SQLite Storage)
- [ ] Create a testing Worker that imports the Storage Capability

## Phase 4: Reference Manager

- [ ] Implement a minimal Manager Worker (Role: manager)
- [ ] Validate end-to-end flow: Solon -> Manifests -> Control Plane -> Data Plane -> SQLite
