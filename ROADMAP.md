# Atlas Roadmap

This document outlines the high-level roadmap for the Atlas framework.

---

## Phase 0: Architecture & Specifications (Current)

- [x] Initial repository setup and licensing
- [x] Core architecture specifications
- [x] Engineering standards
- [x] Technology decisions
- [ ] Protocol interface definitions
- [ ] Manifest and configuration schemas
- [ ] Error handling specification
- [ ] Architecture Decision Records
- [ ] Repository restructuring

## Phase 1: Core Foundation

- [ ] Error hierarchy and base exceptions
- [ ] Logger Protocol and default implementation
- [ ] Configuration Manager (YAML loading, validation, merging)
- [ ] Lifecycle Manager (state machine, transitions)
- [ ] Registry (component registration, lookup, validation)

## Phase 2: Core Runtime

- [ ] Event Bus (async pub/sub, error isolation)
- [ ] Capability Registry (registration, resolution, binding)
- [ ] Dependency Resolver (topological sort, circular detection)
- [ ] Module/Provider Loader (manifest reading, lifecycle orchestration)
- [ ] Runtime orchestrator (boot sequence)

## Phase 3: First Capability

- [ ] Storage Protocol definition
- [ ] SQLite Provider implementation
- [ ] End-to-end Capability → Protocol → Provider validation

## Phase 4: First Module

- [ ] Module Protocol definition
- [ ] Module Manager (discovery, lifecycle)
- [ ] Reference Module (health check / ping)

## Phase 5: MVP Providers

- [ ] AI Protocol and first AI Provider (Gemini or OpenAI)
- [ ] Notification Protocol and ConsoleNotification Provider
- [ ] Validate provider architecture generalizes across capability types

## Phase 6: SDK & CLI

- [ ] SDK scaffolding tools (`atlas new module`, `atlas new provider`)
- [ ] CLI application (boots Atlas, loads modules, demonstrates events)

## Phase 7: LifeOS Reference Application

- [ ] Health Module
- [ ] Finance Module
- [ ] Journal Module
- [ ] LifeOS application assembly

---

## Long-Term Vision

- [ ] Desktop application support
- [ ] Web application support
- [ ] Mobile application support
- [ ] Self-hosted deployments
- [ ] Cloud deployments
- [ ] Third-party module marketplace
- [ ] Community extensions
- [ ] Multiple AI provider ecosystem
