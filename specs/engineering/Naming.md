# Naming

Status: Draft

Version: 0.1

---

# Purpose

Defines naming conventions throughout Atlas.

---

# General

Names should be:

* Short
* Descriptive
* Consistent

Avoid abbreviations.

---

# Classes

PascalCase

Example:

StorageProvider

HealthModule

RuntimeManager

---

# Functions

snake_case

Example:

load_module()

publish_event()

resolve_provider()

---

# Variables

snake_case

---

# Constants

UPPER_SNAKE_CASE

---

# Files

Use PascalCase for specification documents.

Use snake_case for Python files.

Examples:

Runtime.md

storage_provider.py

event_bus.py

---

# Events

Domain.Action

Examples:

Health.WorkoutCompleted

Finance.ExpenseAdded

---

# IDs

Use globally unique identifiers.

Avoid sequential identifiers where possible.

---

# Design Rule

Names should communicate intent immediately.
