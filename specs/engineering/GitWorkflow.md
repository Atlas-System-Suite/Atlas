# Git Workflow

Status: Draft

Version: 0.1

---

# Purpose

Defines contribution workflow.

---

# Branches

main

Stable releases.

develop

Active development.

feature/*

New features.

fix/*

Bug fixes.

release/*

Release preparation.

---

# Commits

Use Conventional Commits.

Examples:

feat:

fix:

docs:

refactor:

test:

build:

---

# Pull Requests

Every PR should include:

Description

Motivation

Testing

Breaking Changes

Related Issues

---

# Reviews

Architecture changes require review.

Generated code should not be reviewed manually.

Only source changes.

---

# Releases

Every release should update:

CHANGELOG

Version

Migration notes

Compatibility notes

---

# Design Rule

History should explain why changes happened, not just what changed.
