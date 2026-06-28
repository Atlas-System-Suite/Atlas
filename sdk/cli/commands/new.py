from rich.console import Console
from rich.prompt import Prompt, Confirm
from sdk.atlas_sdk.generator import ProjectGenerator
import os

console = Console()
"""
atlas new — Scaffold a new Atlas project.
"""

def handle_new(args):
    """
    Handles the `atlas new` command.
    If arguments are provided, it skips the wizard and generates the project directly.
    Otherwise, it launches an interactive wizard.
    """
    # 1. Wizard vs Argument fast-path
    if getattr(args, "type", None) and getattr(args, "name", None):
        project_type = args.type
        name = args.name
        namespace = getattr(args, "namespace", "atlas")
        language = getattr(args, "language", "python")
        version = "1.0.0"
        description = "An Atlas Project"
    else:
        # Launch Interactive Wizard
        console.print("[bold cyan]✨ Welcome to the Atlas Project Wizard ✨[/bold cyan]\n")
        
        project_type = Prompt.ask(
            "What type of artifact do you want to create?", 
            choices=["worker", "manager", "model", "adapter"], 
            default="worker"
        )
        
        name = Prompt.ask("Enter the project name (e.g. 'my-worker')", default="my-project")
        
        namespace = Prompt.ask("Enter the identifier namespace", default="atlas")
        
        version = Prompt.ask("Enter the version", default="1.0.0")
        
        description = Prompt.ask("Enter a short description", default=f"A new Atlas {project_type}")
        
        language_choice = Prompt.ask(
            "Select the implementation language", 
            choices=["python", "rust", "cpp", "go", "zig", "custom"], 
            default="python"
        )
        
        if language_choice == "custom":
            language = Prompt.ask("Enter custom language name")
        else:
            language = language_choice
        
        console.print("\n[bold]Configuration Overview:[/bold]")
        console.print(f"  [cyan]Type:[/cyan]       {project_type}")
        console.print(f"  [cyan]Name:[/cyan]       {name}")
        console.print(f"  [cyan]Identifier:[/cyan] {namespace}.{name}")
        console.print(f"  [cyan]Language:[/cyan]   {language}")
        
        if not Confirm.ask("\nProceed with generation?", default=True):
            console.print("[yellow]Aborted by user.[/yellow]")
            return

    # 2. Setup Configuration Dictionary
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

    # 3. Delegate to SDK Generator
    generator = ProjectGenerator()
    try:
        generator.generate(config)
        console.print(f"\n✨ [bold green]Success![/bold green] Created {project_type} '{name}' in ./{project_dir}/")
        console.print(f"   [dim]cd {project_dir}[/dim]")
        
        if project_type in ("worker", "adapter"):
            console.print(f"   [dim]atlas test[/dim]")
        elif project_type == "manager":
            console.print(f"   [dim]atlas run[/dim]")
            
    except NotImplementedError as e:
        console.print(f"[bold red]❌ Error:[/bold red] {e}")
    except Exception as e:
        console.print(f"[bold red]❌ Fatal Error generating project:[/bold red] {e}")
