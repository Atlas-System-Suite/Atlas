"""
atlas doctor — Validate the development environment.
"""

import sys
import os
import importlib


def handle_doctor(args):
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    
    console = Console()
    
    table = Table(title="Atlas Environment Checks", show_header=True, header_style="bold magenta")
    table.add_column("Component", style="cyan", width=20)
    table.add_column("Status", width=10)
    table.add_column("Details")

    issues = 0

    # 1. Python version
    major, minor = sys.version_info[:2]
    if major >= 3 and minor >= 13:
        table.add_row("Python", "[green]✅ PASS[/green]", f"{major}.{minor} (>= 3.13 required)")
    else:
        table.add_row("Python", "[red]❌ FAIL[/red]", f"{major}.{minor} (>= 3.13 required)")
        issues += 1

    # 2. PyYAML
    try:
        import yaml
        table.add_row("PyYAML", "[green]✅ PASS[/green]", f"v{yaml.__version__}")
    except ImportError:
        table.add_row("PyYAML", "[red]❌ FAIL[/red]", "Not installed (pip install pyyaml)")
        issues += 1

    # 3. Pydantic
    try:
        import pydantic
        table.add_row("Pydantic", "[green]✅ PASS[/green]", f"v{pydantic.__version__}")
    except ImportError:
        table.add_row("Pydantic", "[red]❌ FAIL[/red]", "Not installed (pip install pydantic)")
        issues += 1

    # 4. pytest
    try:
        import pytest
        table.add_row("pytest", "[green]✅ PASS[/green]", f"v{pytest.__version__}")
    except ImportError:
        table.add_row("pytest", "[yellow]⚠️ WARN[/yellow]", "Not installed (pip install pytest)")

    # 5. Atlas SDK
    try:
        import atlas_sdk
        table.add_row("Atlas SDK", "[green]✅ PASS[/green]", getattr(atlas_sdk, "__version__", "Found"))
    except ImportError:
        table.add_row("Atlas SDK", "[yellow]⚠️ WARN[/yellow]", "Not on PYTHONPATH")

    # 6. Atlas Runtime
    try:
        from runtime.atlas.core.runtime import AtlasRuntime
        table.add_row("Atlas Runtime", "[green]✅ PASS[/green]", "Found")
    except ImportError:
        table.add_row("Atlas Runtime", "[yellow]⚠️ WARN[/yellow]", "Not on PYTHONPATH (optional)")

    # 7. Manifest check
    if os.path.exists("atlas.yaml"):
        table.add_row("Manifest", "[green]✅ PASS[/green]", "atlas.yaml found in current directory")
    else:
        table.add_row("Manifest", "[cyan]ℹ️ INFO[/cyan]", "No manifest found (run `atlas new`)")

    console.print(table)
    console.print()

    if issues == 0:
        console.print(Panel("[bold green]🎉 All checks passed! Your environment is ready for Atlas development.[/bold green]", expand=False))
    else:
        console.print(Panel(f"[bold red]⚠️ {issues} issue(s) found. Please fix them before continuing.[/bold red]", expand=False))
