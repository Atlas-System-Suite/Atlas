# Coding Standards

Status: Draft

Version: 0.1

---

# Purpose

Defines coding standards for Atlas.

These rules apply to all packages, modules, providers, applications, and tooling.

---

# General Principles

Code should be:

* Readable
* Predictable
* Typed
* Modular
* Testable

Write code for humans first.

---

# Style

Python version:

3.13+

Formatter:

Ruff Format

Linter:

Ruff

Type Checker:

BasedPyright

---

# Typing

Every public function must include type hints.

Avoid `Any` whenever possible.

Prefer Protocols over inheritance.

Prefer composition over inheritance.

---

# Functions

Functions should:

* Do one thing.
* Have descriptive names.
* Return predictable values.
* Avoid side effects.

---

# Classes

Classes should have one responsibility.

Avoid large "manager" classes.

Prefer dependency injection.

---

# Logging

Never print.

Always use Atlas Logger.

---

# Errors

Raise meaningful exceptions.

Never silently ignore failures.

---

# Documentation

Every public class and function should include docstrings.

Complex algorithms require comments.

---

# Design Rules

Prefer explicitness.

Avoid global state.

Avoid circular dependencies.

Keep Core framework-independent.