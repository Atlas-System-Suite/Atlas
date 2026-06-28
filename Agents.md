# AGENTS.md

# Atlas AI Engineering Guide

Version: 1.0

---

# Purpose

This document defines how AI coding agents should contribute to Atlas.

The objective is to preserve architectural consistency while maximizing autonomous implementation.

This file is authoritative for implementation behavior.

When conflicts arise:

Architecture Specifications

↓

Engineering Standards

↓

AGENTS.md

↓

Implementation

---

# Mission

Atlas is a modular framework for building Personal Operating Systems.

The first implementation is LifeOS.

Your responsibility is **not to merely generate code.**

Your responsibility is to engineer Atlas.

Every decision should improve:

* Maintainability
* Extensibility
* Readability
* Testability
* Long-term evolution

---

# Core Philosophy

Atlas is:

Framework First

Application Second

Features Third

Never optimize a feature at the expense of the framework.

If a specification can be implemented in 200 lines, do not implement it in 2,000.

Favor simple, obvious implementations that satisfy the architecture.

Optimize only after the architecture has been validated by real applications.

---

# Golden Rules

Never violate the Architecture.

Never bypass Interfaces.

Never introduce hidden dependencies.

Never duplicate business logic.

Never hardcode Providers.

Never tightly couple Modules.

Never prioritize cleverness over readability.

---

# Source of Truth

The following order is authoritative.

1. Architecture Specifications

2. Engineering Standards

3. Existing Runtime

4. Tests

Never invent architecture if specifications already exist.

If specifications are missing:

Stop.

Create a proposal.

Do not silently invent behavior.

---

# How to Work

Before implementing:

Read relevant specifications.

Identify dependencies.

Identify required Interfaces.

Identify Events.

Identify Providers.

Only then begin implementation.

---

# Dependency Rules

Core knows nothing.

Modules know Core.

Providers know Core.

Applications know Modules.

No reverse dependency is allowed.

---

# Modules

Every Module must remain independent.

Modules communicate only through:

Events

Capabilities

Interfaces

Never directly import another Module's implementation.

---

# Providers

Providers implement Capabilities.

Providers never contain business logic.

Providers should be replaceable.

Never expose provider-specific APIs.

---

# Runtime

Runtime coordinates.

Runtime does not decide business behavior.

Avoid placing feature logic inside Runtime.

---

# Events

Events represent completed actions.

Events are immutable.

Subscribers should never modify Events.

Events should remain descriptive.

---

# Interfaces

Program against Interfaces.

Never concrete implementations.

Prefer Protocols.

Keep Interfaces minimal.

---

# Code Quality

Every public API should include:

Typing

Documentation

Tests

Meaningful errors

Avoid unnecessary abstractions.

Avoid premature optimization.

---

# Error Handling

Fail early.

Fail clearly.

Recover whenever possible.

Errors should contain:

Reason

Context

Suggested resolution

Never silently ignore failures.

---

# Testing

Every implementation should include tests.

Every bug fix should include regression tests.

Mock external systems.

Do not mock Atlas Core.

---

# Documentation

If implementation changes architecture:

Update specifications.

If architecture changes:

Create an ADR.

Documentation must never become outdated.

---

# Refactoring

Refactor only when:

Readability improves.

Maintainability improves.

Complexity decreases.

Do not refactor merely for preference.

---

# Performance

Optimize only after correctness.

Measure before optimizing.

Document major optimizations.

---

# Security

Never expose secrets.

Validate external input.

Sanitize configuration.

Use least privilege.

---

# AI Usage

AI should assist deterministic systems.

Business rules must remain deterministic.

Never replace deterministic behavior with probabilistic output.

---

# Generated Code

Generated code should:

Compile.

Pass tests.

Follow standards.

Require minimal manual edits.

---

# Architecture Changes

Major architectural changes require:

Proposal

Reasoning

Alternatives

Trade-offs

Migration strategy

Never introduce breaking architecture silently.

---

# Decision Making

When multiple implementations are valid:

Choose the one that is:

Simpler

More modular

More testable

More extensible

---

# Before Every Commit

Ask:

Does this increase coupling?

Does this violate architecture?

Does this duplicate functionality?

Can another Module reuse this?

Will this still make sense in two years?

If uncertain:

Choose the simpler design.

---

# Long-Term Vision

Atlas should eventually support:

Desktop

Web

Mobile

Cloud

Self-hosting

Third-party modules

Marketplace

Multiple AI providers

Multiple storage providers

Without changing Atlas Core.

Every implementation should move Atlas closer to this vision.

---

# Implementation Mindset

Do not build Atlas.

Build the smallest implementation that proves the architecture works.

For each capability, prove:

Module → Capability → Protocol → Provider → External System → Success.

Then stop. Move to the next capability.

Perfection comes from iteration, not from the first implementation.

---

# Definition of Done

Every feature is complete only when:

* Code compiles and runs.
* Tests pass.
* Documentation exists.
* Specification is updated (if changed).
* Changelog is updated.
* Example exists.
* CI passes.
* No architecture violation.

Incomplete work should not be merged.

---

# Final Principle

Atlas is intended to outlive its first implementation.

Write code that future developers—and future AI agents—can understand without needing historical context.

Prefer clarity over cleverness.

Prefer architecture over shortcuts.

Prefer evolution over reinvention.
