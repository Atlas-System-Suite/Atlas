"""
atlas info — Show Atlas SDK information.
"""


def handle_info(args):
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text

    console = Console()

    try:
        from atlas_sdk import __version__ as sdk_version
    except ImportError:
        sdk_version = "not installed"

    table = Table(show_header=False, box=None)
    table.add_column("Key", style="bold cyan")
    table.add_column("Value")

    table.add_row("SDK Version", f"[green]{sdk_version}[/green]")
    table.add_row("Runtime", "Atlas Runtime v1 (frozen)")
    table.add_row("Architecture", "v1.0 (frozen)")
    table.add_row("First Language", "Python")
    table.add_row("", "")
    table.add_row("Primitives", "Worker, Room, Session, Registry, Binding, Invocation")
    table.add_row("Studio Suite", "Miron (console), Solon (validator), Varsity (learning)")
    table.add_row("", "")
    table.add_row("📖 Docs", "[link=https://atlas-system-suite.github.io/Atlas/]https://atlas-system-suite.github.io/Atlas/[/link]")
    table.add_row("🐙 Repo", "[link=https://github.com/atlas-system-suite/Atlas]https://github.com/atlas-system-suite/Atlas[/link]")

    panel = Panel(table, title="[bold magenta]ℹ️  Atlas SDK Info[/bold magenta]", expand=False, border_style="cyan")
    console.print(panel)
