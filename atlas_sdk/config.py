"""
Atlas SDK — Configuration
=========================

SDK-level configuration for Atlas development.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SDKConfig:
    """SDK-level configuration."""
    default_language: str = "python"
    template_dir: Optional[str] = None
    package_output_dir: str = "dist"
    manifest_filename: str = "atlas.yaml"
    manager_filename: str = "atlas.yaml"
    test_runner: str = "pytest"
