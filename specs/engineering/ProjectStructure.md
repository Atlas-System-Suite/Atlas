# Project Structure

Status: Draft

Version: 0.1

---

# Purpose

Defines how Atlas source code is organized.

---

# Layering

Atlas consists of:

Core

↓

Runtime

↓

Capabilities

↓

Providers

↓

Modules

↓

Applications

---

# Dependency Rules

Applications may depend on Modules.

Modules may depend on Core.

Providers may depend on Core.

Core depends on nothing.

No reverse dependencies are allowed.

---

# Folder Ownership

Each folder has a single responsibility.

Core

Framework.

Providers

Infrastructure.

Modules

Business logic.

Apps

Products.

SDK

Developer tooling.

---

# Internal APIs

Anything inside an `internal/` package is private.

Modules must never use internal APIs.

---

# Generated Code

Generated code should live inside generated/ directories.

Never edit generated code manually.

---

# Future

The project structure should remain stable as Atlas grows.
