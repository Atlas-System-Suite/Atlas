import questionary
from rich.console import Console
from rich.panel import Panel
from atlas_sdk.generator import ProjectGenerator
import os
import sys

console = Console()
"""
atlas new — Scaffold a new Atlas project.
"""

# Shared questionary style
ATLAS_STYLE = questionary.Style([
    ('qmark', 'fg:cyan bold'),
    ('question', 'bold'),
    ('answer', 'fg:magenta bold'),
    ('pointer', 'fg:cyan bold'),
    ('highlighted', 'fg:cyan bold'),
    ('selected', 'fg:cyan'),
])


def handle_new(args):
    """
    Handles the `atlas new` command.
    If arguments are provided, it skips the wizard and generates the project directly.
    Otherwise, it launches an interactive wizard using questionary.
    """
    # 1. Fast-path: atlas new worker my_worker [--namespace x] [--language y]
    if getattr(args, "type", None) and getattr(args, "name", None):
        project_type = args.type
        name = args.name
        namespace = getattr(args, "namespace", None) or "atlas"
        language = getattr(args, "language", None) or "python"
        version = "1.0.0"
        description = "An Atlas Project"
    else:
        # 2. Interactive wizard
        os.system('cls' if os.name == 'nt' else 'clear')
        console.print(
            "\n[bold cyan]    ▲[/bold cyan]\n"
            "[bold cyan]   ▲ ▲[/bold cyan]    [bold white]ATLAS[/bold white] [bold cyan]New Project[/bold cyan]\n"
            "[bold cyan]  ▲ ▲ ▲[/bold cyan]   [dim white]Interactive scaffolding wizard[/dim white]\n"
        )

        project_type = questionary.select(
            "What type of artifact do you want to create?",
            choices=[
                questionary.Choice("Worker   — Business logic unit", "worker"),
                questionary.Choice("Manager  — Application orchestrator", "manager"),
                questionary.Choice("Model    — Abstract capability contract", "model"),
                questionary.Choice("Adapter  — Format translator", "adapter"),
            ],
            style=ATLAS_STYLE,
        ).ask()

        if not project_type:
            console.print("[yellow]Aborted.[/yellow]")
            return

        name = questionary.text(
            "Project name:",
            default="my_project",
            validate=lambda val: True if val.strip() else "Name cannot be empty",
            style=ATLAS_STYLE,
        ).ask()

        if not name:
            console.print("[yellow]Aborted.[/yellow]")
            return

        namespace = questionary.text(
            "Identifier namespace:",
            default="atlas",
            style=ATLAS_STYLE,
        ).ask()

        if not namespace:
            console.print("[yellow]Aborted.[/yellow]")
            return

        version = questionary.text(
            "Version:",
            default="1.0.0",
            style=ATLAS_STYLE,
        ).ask()

        if not version:
            console.print("[yellow]Aborted.[/yellow]")
            return

        description = questionary.text(
            "Short description:",
            default=f"A new Atlas {project_type}",
            style=ATLAS_STYLE,
        ).ask()

        if not description:
            console.print("[yellow]Aborted.[/yellow]")
            return

        language = questionary.select(
            "Implementation language:",
            choices=[
                questionary.Choice("Python", "python"),
                questionary.Choice("Rust (coming soon)", "rust"),
                questionary.Choice("Go (coming soon)", "go"),
                questionary.Choice("C++ (coming soon)", "cpp"),
                questionary.Choice("Zig (coming soon)", "zig"),
            ],
            style=ATLAS_STYLE,
        ).ask()

        if not language:
            console.print("[yellow]Aborted.[/yellow]")
            return

        # Summary
        console.print()
        summary = (
            f"[cyan]Type:[/cyan]        {project_type}\n"
            f"[cyan]Name:[/cyan]        {name}\n"
            f"[cyan]Identifier:[/cyan]  {namespace}.{name}\n"
            f"[cyan]Version:[/cyan]     {version}\n"
            f"[cyan]Language:[/cyan]    {language}\n"
            f"[cyan]Description:[/cyan] {description}"
        )
        console.print(Panel(summary, title="[bold cyan]Configuration[/bold cyan]", border_style="cyan"))

        proceed = questionary.confirm(
            "Proceed with generation?",
            default=True,
            style=ATLAS_STYLE,
        ).ask()

        if not proceed:
            console.print("[yellow]Aborted by user.[/yellow]")
            return

    # 3. Setup Configuration Dictionary
    class_name = "".join(word.capitalize() for word in name.replace("-", "_").split("_"))
    if not class_name.endswith(project_type.capitalize()):
        class_name += project_type.capitalize()

    project_dir = name
    config = {
        "type": project_type,
        "name": name,
        "class_name": class_name,
        "namespace": namespace,
        "language": language,
        "version": version,
        "description": description,
        "dest_dir": project_dir
    }

    # 4. Delegate to SDK Generator
    generator = ProjectGenerator()
    try:
        generator.generate(config)
        console.print(f"\n✨ [bold green]Success![/bold green] Created {project_type} [bold]'{name}'[/bold] in [cyan]./{project_dir}/[/cyan]")
        console.print()
        
        # Show next steps
        steps = f"[dim]cd {project_dir}[/dim]\n"
        if project_type in ("worker", "adapter"):
            steps += "[dim]atlas test[/dim]\n"
            steps += "[dim]atlas run[/dim]"
        elif project_type == "manager":
            steps += "[dim]python main.py[/dim]   [dim italic]# Generate atlas.yaml[/dim italic]\n"
            steps += "[dim]atlas run[/dim]         [dim italic]# Boot the runtime[/dim italic]"
        elif project_type == "model":
            steps += "[dim]atlas test[/dim]"
        
        console.print(Panel(steps, title="[bold green]Next Steps[/bold green]", border_style="green"))

    except NotImplementedError as e:
        console.print(f"[bold red]❌ Error:[/bold red] {e}")
    except Exception as e:
        console.print(f"[bold red]❌ Fatal Error generating project:[/bold red] {e}")
