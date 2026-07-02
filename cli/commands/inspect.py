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

    import zipfile
    if manifest_path.endswith(".atlas"):
        try:
            with zipfile.ZipFile(manifest_path, 'r') as zf:
                if "atlas.yaml" not in zf.namelist():
                    console.print(f"❌ Manifest 'atlas.yaml' not found inside package: {manifest_path}")
                    sys.exit(1)
                manifest_content = zf.read("atlas.yaml").decode("utf-8")
                manifest = yaml.safe_load(manifest_content)
        except Exception as e:
            console.print(f"❌ Failed to read package file: {e}")
            sys.exit(1)
    else:
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = yaml.safe_load(f)
        except Exception as e:
            console.print(f"❌ Failed to parse manifest YAML: {e}")
            sys.exit(1)

    # Resolve root or nested metadata
    meta_src = manifest
    is_manager = "manager" in manifest
    if is_manager and isinstance(manifest["manager"], dict):
        meta_src = manifest["manager"]
    elif "worker" in manifest and isinstance(manifest["worker"], dict):
        meta_src = manifest["worker"]

    console.print("🔎 Atlas Inspector\n")
    console.print(f"   ID:       {meta_src.get('id', 'N/A')}")
    console.print(f"   Name:     {meta_src.get('name', 'N/A')}")
    console.print(f"   Version:  {meta_src.get('version', 'N/A')}")
    console.print(f"   Type:     {'Manager' if is_manager else 'Worker'}")
    
    if not is_manager:
        console.print(f"   Language:  {meta_src.get('language', 'N/A')}")
        console.print(f"   Roles:     {', '.join(meta_src.get('roles', [])) if isinstance(meta_src.get('roles'), list) else 'N/A'}")
        execution = manifest.get("execution", {})
        console.print(f"   Policy:    {execution.get('policy', 'N/A')}")
    else:
        workers = manifest.get("workers", [])
        console.print(f"   Workers:   {len(workers)} in topology")

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
