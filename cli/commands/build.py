"""
atlas build — Build an .atlas package.
"""

import yaml
import os
import sys


def handle_build(args):
    from atlas_sdk.packaging import PackageBuilder, PackageSpec

    manifest_path = "atlas.yaml"
    if not os.path.exists(manifest_path):
        print(f"❌ No atlas.yaml found in current directory.")
        sys.exit(1)

    with open(manifest_path, "r") as f:
        manifest = yaml.safe_load(f)

    name = manifest.get("id", "unknown").replace(".", "-")
    version = manifest.get("version", "0.0.0")

    spec = PackageSpec(
        name=name,
        version=version,
        source_dir=".",
        manifest_path=manifest_path,
        output_dir=args.output,
    )

    builder = PackageBuilder(spec)
    output_path = builder.build()

    print(f"📦 Built package: {output_path}")
    print(f"   Name:    {name}")
    print(f"   Version: {version}")
