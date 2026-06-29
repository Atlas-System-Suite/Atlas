"""
atlas validate — Validate Atlas manifests.
"""

import yaml
import os
import sys


REQUIRED_FIELDS = ["id", "name", "version", "language", "roles"]
VALID_POLICIES = ["singleton", "pool", "transient", "on_demand"]


def handle_validate(args):
    manifest_path = args.manifest

    if not os.path.exists(manifest_path):
        print(f"❌ Manifest not found: {manifest_path}")
        sys.exit(1)

    print(f"🔍 Validating {manifest_path}...\n")

    with open(manifest_path, "r") as f:
        manifest = yaml.safe_load(f)

    errors = []
    warnings = []

    # Required fields
    for field in REQUIRED_FIELDS:
        if field not in manifest:
            errors.append(f"Missing required field: '{field}'")

    # Execution policy
    execution = manifest.get("execution", {})
    policy = execution.get("policy", "")
    if policy and policy not in VALID_POLICIES:
        warnings.append(f"Unknown execution policy: '{policy}' (expected one of {VALID_POLICIES})")

    # Exports validation
    exports = manifest.get("exports", [])
    for i, exp in enumerate(exports):
        if isinstance(exp, dict) and "capability" not in exp:
            errors.append(f"Export #{i+1} missing 'capability' field")

    # Imports validation
    imports = manifest.get("imports", [])
    for i, imp in enumerate(imports):
        if isinstance(imp, dict) and "capability" not in imp:
            errors.append(f"Import #{i+1} missing 'capability' field")

    # Circular dependency check (self-import)
    worker_id = manifest.get("id", "")
    export_caps = [e.get("capability", "") for e in exports if isinstance(e, dict)]
    import_caps = [i.get("capability", "") for i in imports if isinstance(i, dict)]
    for cap in import_caps:
        if cap in export_caps:
            errors.append(f"Circular dependency: Worker imports its own export '{cap}'")

    # Report
    if errors:
        print("   ❌ Errors:")
        for e in errors:
            print(f"      - {e}")

    if warnings:
        print("   ⚠️  Warnings:")
        for w in warnings:
            print(f"      - {w}")

    if not errors and not warnings:
        print("   ✅ Manifest is valid!")
    elif errors:
        print(f"\n   {len(errors)} error(s), {len(warnings)} warning(s)")
        sys.exit(1)
    else:
        print(f"\n   {len(warnings)} warning(s), no errors")
