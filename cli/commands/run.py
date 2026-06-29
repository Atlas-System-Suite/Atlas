from rich.console import Console
console = Console()
"""
atlas run — Run an Atlas application.
"""

import yaml
import os
import sys


def handle_run(args):
    manifest_path = args.manifest

    if not os.path.exists(manifest_path):
        console.print(f"[bold red]❌ Manifest not found:[/bold red] {manifest_path}")
        console.print("   Are you in an Atlas project directory?")
        sys.exit(1)

    with open(manifest_path, "r") as f:
        manifest = yaml.safe_load(f)

    worker_name = manifest.get("name", manifest.get("id", "Unknown"))
    
    from rich.panel import Panel
    from rich.text import Text
    
    details = f"[cyan]Manifest:[/cyan] {manifest_path}\n"
    details += f"[cyan]Language:[/cyan] {manifest.get('language', 'python')}\n"
    details += f"[cyan]Policy:[/cyan]   {manifest.get('execution', {}).get('policy', 'singleton')}\n\n"

    exports = manifest.get("exports", [])
    imports = manifest.get("imports", [])

    if exports:
        details += "[bold magenta]📤 Exports:[/bold magenta]\n"
        for e in exports:
            cap = e.get("capability", e) if isinstance(e, dict) else e
            details += f"  - {cap}\n"

    if imports:
        details += "[bold magenta]📥 Imports:[/bold magenta]\n"
        for i in imports:
            cap = i.get("capability", i) if isinstance(i, dict) else i
            details += f"  - {cap}\n"
            
    details += "\n[green]✅ Worker loaded successfully.[/green]\n"
    details += "[yellow]ℹ️  Full runtime integration coming in Phase 2.[/yellow]"

    panel = Panel(details, title=f"[bold cyan]🚀 Atlas Runtime — Starting '{worker_name}'[/bold cyan]", expand=False, border_style="blue")
    console.print(panel)
