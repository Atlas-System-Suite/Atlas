"""
Atlas SDK — Packaging
=====================

Defines the .atlas package format and provides utilities for
building and reading packages.

An .atlas package is a ZIP archive containing:
    atlas.yaml       — The worker/manager manifest
    src/                — Source code
    assets/             — Static assets
    docs/               — Documentation
    checksums.sha256    — Integrity verification
"""

import os
import zipfile
import hashlib
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class PackageSpec:
    """Specification for an Atlas package."""
    name: str
    version: str
    source_dir: str
    manifest_path: str
    assets_dir: Optional[str] = None
    docs_dir: Optional[str] = None
    output_dir: str = "dist"


class PackageBuilder:
    """
    Builds deterministic, reproducible .atlas packages.

    Usage::

        builder = PackageBuilder(PackageSpec(
            name="my-worker",
            version="1.0.0",
            source_dir="src/",
            manifest_path="atlas.yaml",
        ))
        path = builder.build()
    """

    def __init__(self, spec: PackageSpec):
        self.spec = spec

    def build(self) -> str:
        """
        Builds the .atlas package and returns the output path.
        """
        os.makedirs(self.spec.output_dir, exist_ok=True)
        package_name = f"{self.spec.name}-{self.spec.version}.atlas"
        output_path = os.path.join(self.spec.output_dir, package_name)
        checksums: Dict[str, str] = {}

        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # 1. Manifest
            if os.path.exists(self.spec.manifest_path):
                zf.write(self.spec.manifest_path, "atlas.yaml")
                checksums["atlas.yaml"] = self._hash_file(self.spec.manifest_path)

            # 2. Source
            if os.path.isdir(self.spec.source_dir):
                for root, dirs, files in os.walk(self.spec.source_dir):
                    for file in files:
                        filepath = os.path.join(root, file)
                        arcname = os.path.join("src", os.path.relpath(filepath, self.spec.source_dir))
                        zf.write(filepath, arcname)
                        checksums[arcname] = self._hash_file(filepath)

            # 3. Assets
            if self.spec.assets_dir and os.path.isdir(self.spec.assets_dir):
                for root, dirs, files in os.walk(self.spec.assets_dir):
                    for file in files:
                        filepath = os.path.join(root, file)
                        arcname = os.path.join("assets", os.path.relpath(filepath, self.spec.assets_dir))
                        zf.write(filepath, arcname)
                        checksums[arcname] = self._hash_file(filepath)

            # 4. Docs
            if self.spec.docs_dir and os.path.isdir(self.spec.docs_dir):
                for root, dirs, files in os.walk(self.spec.docs_dir):
                    for file in files:
                        filepath = os.path.join(root, file)
                        arcname = os.path.join("docs", os.path.relpath(filepath, self.spec.docs_dir))
                        zf.write(filepath, arcname)
                        checksums[arcname] = self._hash_file(filepath)

            # 5. Checksums
            checksum_content = "\n".join(
                f"{sha}  {name}" for name, sha in sorted(checksums.items())
            )
            zf.writestr("checksums.sha256", checksum_content)

        return output_path

    def _hash_file(self, filepath: str) -> str:
        h = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()


class PackageReader:
    """
    Reads and inspects an .atlas package.

    Usage::

        reader = PackageReader("dist/my-worker-1.0.0.atlas")
        info = reader.info()
    """

    def __init__(self, path: str):
        self.path = path

    def info(self) -> Dict:
        """Returns metadata about the package."""
        with zipfile.ZipFile(self.path, 'r') as zf:
            names = zf.namelist()
            has_manifest = "atlas.yaml" in names
            has_checksums = "checksums.sha256" in names
            src_files = [n for n in names if n.startswith("src/")]
            asset_files = [n for n in names if n.startswith("assets/")]
            doc_files = [n for n in names if n.startswith("docs/")]

            return {
                "path": self.path,
                "has_manifest": has_manifest,
                "has_checksums": has_checksums,
                "source_files": len(src_files),
                "asset_files": len(asset_files),
                "doc_files": len(doc_files),
                "total_files": len(names),
            }

    def extract(self, output_dir: str) -> str:
        """Extracts the package to the given directory."""
        with zipfile.ZipFile(self.path, 'r') as zf:
            zf.extractall(output_dir)
        return output_dir

    def verify_checksums(self) -> bool:
        """Verifies the integrity of all files against checksums.sha256."""
        with zipfile.ZipFile(self.path, 'r') as zf:
            if "checksums.sha256" not in zf.namelist():
                return False

            checksum_data = zf.read("checksums.sha256").decode("utf-8")
            expected = {}
            for line in checksum_data.strip().split("\n"):
                sha, name = line.split("  ", 1)
                expected[name] = sha

            for name, expected_sha in expected.items():
                data = zf.read(name)
                actual_sha = hashlib.sha256(data).hexdigest()
                if actual_sha != expected_sha:
                    return False

        return True
