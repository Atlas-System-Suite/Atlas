from rich.console import Console
console = Console()
"""
atlas inspect — Inspect an Atlas Worker or Manager.
"""

import yaml
import os
import sys


def handle_inspect(args):
    manifest_path = args.manifest

    if not os.path.exists(manifest_path):
        console.print(f"❌ Manifest not found: {manifest_path}")
        sys.exit(1)

    with open(manifest_path, "r") as f:
        manifest = yaml.safe_load(f)

    console.print("🔎 Atlas Inspector\n")
    console.print(f"   ID:       {manifest.get('id', 'N/A')}")
    console.print(f"   Name:     {manifest.get('name', 'N/A')}")
    console.print(f"   Version:  {manifest.get('version', 'N/A')}")
    console.print(f"   Language:  {manifest.get('language', 'N/A')}")
    console.print(f"   Roles:     {', '.join(manifest.get('roles', []))}")

    execution = manifest.get("execution", {})
    console.print(f"   Policy:    {execution.get('policy', 'N/A')}")
    console.print()

    exports = manifest.get("exports", [])
    if exports:
        console.print("   📤 Exported Capabilities:")
        for e in exports:
            if isinstance(e, dict):
                console.print(f"      - {e.get('capability', '?')} v{e.get('version', '?')}")
            else:
                console.print(f"      - {e}")

    imports = manifest.get("imports", [])
    if imports:
        console.print("   📥 Required Capabilities:")
        for i in imports:
            if isinstance(i, dict):
                console.print(f"      - {i.get('capability', '?')}")
            else:
                console.print(f"      - {i}")

    translations = manifest.get("translations", [])
    if translations:
        console.print("   🔄 Translations:")
        for t in translations:
            if isinstance(t, dict):
                console.print(f"      - {t.get('source_format', '?')} → {t.get('target_format', '?')} (cost: {t.get('cost', '?')})")

    if not exports and not imports and not translations:
        console.print("   ℹ️  No capabilities, imports, or translations declared.")
