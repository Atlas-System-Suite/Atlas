from atlas_sdk.discovery import DiscoveryEngine
import argparse
import sys
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

class StudioCliWorker:
    def __init__(self):
        self.atlas_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        self.engine = DiscoveryEngine(self.atlas_root)

    def _create_parser(self):
        parser = argparse.ArgumentParser(
            prog="atlas studio",
            description="Atlas Studio — Workspace Manager & Development Hub",
        )
        subparsers = parser.add_subparsers(dest="group", help="Command groups")

        # Managers
        managers_parser = subparsers.add_parser("managers", help="Manage installed managers")
        managers_sub = managers_parser.add_subparsers(dest="subcommand")
        managers_sub.add_parser("list", help="List all installed managers")
        managers_sub.add_parser("show", help="Show manager details").add_argument("name")
        managers_sub.add_parser("launch", help="Launch a manager").add_argument("name")

        # Workers
        workers_parser = subparsers.add_parser("workers", help="Manage installed workers")
        workers_sub = workers_parser.add_subparsers(dest="subcommand")
        workers_sub.add_parser("list", help="List all installed workers")
        workers_sub.add_parser("show", help="Show worker details").add_argument("name")
        
        # Projects, Models, Packages, Workspace, Docs, Examples, Settings
        for group in ["projects", "models", "packages", "workspace", "docs", "examples", "settings"]:
            grp = subparsers.add_parser(group, help=f"Manage {group}")
            grp_sub = grp.add_subparsers(dest="subcommand")
            grp_sub.add_parser("list", help=f"List {group}")

        return parser

    def handle_managers(self, args):
        if args.subcommand == "list":
            table = Table(title="Installed Atlas Managers", header_style="bold magenta")
            table.add_column("ID", style="cyan")
            table.add_column("Name")
            table.add_column("Version")
            table.add_column("Description")
            
            for mgr in self.engine.list_managers():
                data = mgr["manifest"]
                table.add_row(
                    data.get("id", "N/A"),
                    data.get("name", "N/A"),
                    str(data.get("version", "N/A")),
                    data.get("description", "")
                )
            console.print(table)
        else:
            console.print(f"[yellow]Command 'managers {args.subcommand}' is under construction.[/yellow]")

    def handle_workers(self, args):
        if args.subcommand == "list":
            table = Table(title="Installed Atlas Workers", header_style="bold green")
            table.add_column("ID", style="cyan")
            table.add_column("Name")
            table.add_column("Version")
            table.add_column("Description")
            
            for wkr in self.engine.list_workers():
                data = wkr["manifest"]
                table.add_row(
                    data.get("id", "N/A"),
                    data.get("name", "N/A"),
                    str(data.get("version", "N/A")),
                    data.get("description", "")
                )
            console.print(table)
        else:
            console.print(f"[yellow]Command 'workers {args.subcommand}' is under construction.[/yellow]")

    def handle_topology(self, args=None):
        import yaml
        from rich.tree import Tree
        manifest_path = os.path.join(os.getcwd(), "atlas.yaml")
        if not os.path.exists(manifest_path):
            console.print("[yellow]No atlas.yaml found in current directory. Run `atlas new` to scaffold one.[/yellow]")
            return
            
        with open(manifest_path, "r") as f:
            manifest = yaml.safe_load(f)
            
        manager_id = manifest.get("id", "Unknown Manager")
        tree = Tree(f"[bold cyan]📦 {manager_id}[/bold cyan] (Workspace)")
        
        workers = manifest.get("workers", [])
        if not workers:
            tree.add("[italic red]No workers found in atlas.yaml[/italic red]")
        else:
            for w in workers:
                worker_id = w.get("id", "Unknown Worker")
                w_node = tree.add(f"[bold green]⚙️ {worker_id}[/bold green]")
                info = self.engine.find_worker(worker_id)
                if info and "manifest" in info:
                    w_manifest = info["manifest"]
                    provides = w_manifest.get("provides", [])
                    requires = w_manifest.get("requires", [])
                    if provides:
                        p_node = w_node.add("[cyan]Provides[/cyan]")
                        for p in provides:
                            p_node.add(f"🔹 {p}")
                    if requires:
                        r_node = w_node.add("[yellow]Requires[/yellow]")
                        for r in requires:
                            r_node.add(f"🔸 {r}")
                else:
                    w_node.add("[dim]Worker not found in local library.[/dim]")
                    
        console.print(tree)

    def handle_marketplace(self, args=None):
        console.print("\n[bold magenta]🛒 Atlas Marketplace (Local Standard Library)[/bold magenta]")
        all_workers = self.engine.list_workers()
        from rich.prompt import Prompt
        from rich.table import Table
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("No.", style="dim")
        table.add_column("Worker ID")
        table.add_column("Description")
        
        for idx, w in enumerate(all_workers, 1):
            manifest = w["manifest"]
            table.add_row(str(idx), manifest.get("id", "unknown"), manifest.get("description", ""))
            
        console.print(table)
        
        choice = Prompt.ask("\n[bold yellow]Enter the number of the Worker to install (or 'q' to cancel)[/bold yellow]")
        if choice.lower() == 'q':
            return
            
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(all_workers):
                worker_to_install = all_workers[idx]["manifest"]["id"]
                import yaml
                manifest_path = os.path.join(os.getcwd(), "atlas.yaml")
                if os.path.exists(manifest_path):
                    with open(manifest_path, "r") as f:
                        manifest = yaml.safe_load(f)
                    
                    workers = manifest.get("workers", [])
                    if any(w.get("id") == worker_to_install for w in workers):
                        console.print(f"[yellow]'{worker_to_install}' is already installed in atlas.yaml![/yellow]")
                    else:
                        workers.append({"id": worker_to_install})
                        manifest["workers"] = workers
                        with open(manifest_path, "w") as f:
                            yaml.dump(manifest, f, default_flow_style=False, sort_keys=False)
                        console.print(f"[bold green]✅ Added '{worker_to_install}' to atlas.yaml![/bold green]")
                else:
                    console.print("[yellow]No atlas.yaml found. Please create a workspace first.[/yellow]")
            else:
                console.print("[red]Invalid selection.[/red]")
        except ValueError:
            console.print("[red]Invalid input.[/red]")

    def handle_diagnostics(self, args=None):
        import yaml
        manifest_path = os.path.join(os.getcwd(), "atlas.yaml")
        if not os.path.exists(manifest_path):
            console.print("[yellow]No atlas.yaml found in current directory.[/yellow]")
            return
            
        with open(manifest_path, "r") as f:
            manifest = yaml.safe_load(f)
            
        console.print("\n[bold cyan]🩺 Running Workspace Diagnostics...[/bold cyan]")
        
        workers = manifest.get("workers", [])
        provided_caps = set()
        required_caps = set()
        
        missing_workers = False
        for w in workers:
            w_id = w.get("id")
            info = self.engine.find_worker(w_id)
            if not info:
                console.print(f"[bold red]❌ Worker '{w_id}' is declared but not installed![/bold red]")
                missing_workers = True
                continue
                
            w_manifest = info["manifest"]
            for p in w_manifest.get("provides", []):
                provided_caps.add(p)
            for r in w_manifest.get("requires", []):
                required_caps.add(r)
                
        if not missing_workers:
            console.print("[green]✅ All declared workers are installed.[/green]")
            
        unmet_requirements = required_caps - provided_caps
        if unmet_requirements:
            console.print("[bold red]❌ Architecture Error: Unmet Requirements![/bold red]")
            for req in unmet_requirements:
                console.print(f"  🔸 No installed worker provides: [bold yellow]{req}[/bold yellow]")
        else:
            console.print("[green]✅ All required capabilities are satisfied by providers.[/green]")
            
        console.print("\n[dim]Diagnostics complete.[/dim]")

    def on_invoke(self, capability: str, args: dict):
        if capability == "studio.cli.execute":
            cli_args = args.get("args", [])
            if not cli_args:
                # Fallback to TUI
                self.on_invoke("studio.tui.launch", {})
                return {"status": "ok"}

            parser = self._create_parser()
            parsed_args = parser.parse_args(cli_args)

            if parsed_args.group == "managers":
                self.handle_managers(parsed_args)
            elif parsed_args.group == "workers":
                self.handle_workers(parsed_args)
            elif parsed_args.group:
                console.print(f"[yellow]Group '{parsed_args.group}' is recognized but under construction.[/yellow]")
            else:
                parser.print_help()

            return {"status": "ok"}
            
        elif capability == "studio.tui.launch":
            from rich.text import Text
            import questionary
            
            logo = "\n[bold white]ATLAS STUDIO[/bold white]\n[dim white]Part of the Atlas Software Suite[/dim white]\n"
            
            def clear_screen():
                os.system('cls' if os.name == 'nt' else 'clear')
                console.clear()
            
            while True:
                clear_screen()
                console.print(logo)
                console.print(Panel(
                    "[bold bright_white]Welcome to Atlas Studio[/bold bright_white]\n"
                    "[italic]The visual workspace manager for modular software.[/italic]",
                    border_style="magenta"
                ))
                
                choice = questionary.select(
                    "Select an action:",
                    choices=[
                        questionary.Choice("🌳 Visual Topology Explorer", "topology"),
                        questionary.Choice("🛒 Browse & Install Packages", "marketplace"),
                        questionary.Choice("🩺 Run Workspace Diagnostics", "diagnostics"),
                        questionary.Choice("📋 List installed Managers", "list_managers"),
                        questionary.Choice("📋 List installed Workers", "list_workers"),
                        questionary.Choice("🔍 Inspect a Worker", "inspect"),
                        questionary.Choice("✨ Scaffold new Workspace", "scaffold"),
                        questionary.Choice("⚙️  Core Settings & Configuration", "settings"),
                        questionary.Separator(),
                        questionary.Choice("❌ Exit", "quit")
                    ],
                    style=questionary.Style([
                        ('qmark', 'fg:cyan bold'),
                        ('question', 'bold'),
                        ('answer', 'fg:magenta bold'),
                        ('pointer', 'fg:cyan bold'),
                        ('highlighted', 'fg:cyan bold'),
                        ('selected', 'fg:cyan'),
                        ('separator', 'fg:black'),
                    ])
                ).ask()
                
                clear_screen()
                
                if not choice or choice == "quit":
                    console.print("[magenta]Exiting Atlas Studio. Goodbye![/magenta]")
                    break
                    
                if choice == "topology":
                    console.print(Panel("🌳 [bold cyan]Topology Explorer[/bold cyan]", border_style="cyan"))
                    self.handle_topology()
                elif choice == "marketplace":
                    self.handle_marketplace()
                elif choice == "diagnostics":
                    console.print(Panel("🩺 [bold cyan]Workspace Diagnostics[/bold cyan]", border_style="cyan"))
                    self.handle_diagnostics()
                elif choice == "list_managers":
                    self.handle_managers(argparse.Namespace(subcommand="list"))
                elif choice == "list_workers":
                    self.handle_workers(argparse.Namespace(subcommand="list"))
                elif choice == "inspect":
                    console.print(Panel("🔍 [bold cyan]Inspect Worker[/bold cyan]", border_style="cyan"))
                    worker_id = questionary.text("Enter Worker ID to inspect:").ask()
                    if worker_id:
                        info = self.engine.find_worker(worker_id)
                        if info:
                            import json
                            console.print(f"\n[bold green]Manifest for {worker_id}:[/bold green]")
                            console.print(json.dumps(info["manifest"], indent=2))
                        else:
                            console.print(f"[red]Worker '{worker_id}' not found.[/red]")
                elif choice == "scaffold":
                    console.print(Panel("✨ [bold cyan]Scaffold New Project[/bold cyan]", border_style="cyan"))
                    from cli.commands.new import handle_new
                    
                    class ScaffoldArgs:
                        type = None
                        name = None
                        namespace = "atlas"
                        language = "python"
                        template = None
                    
                    handle_new(ScaffoldArgs())
                elif choice == "settings":
                    self.handle_settings()
                
                questionary.press_any_key_to_continue("Press any key to return to the Main Menu...").ask()

            return {"status": "ok"}

    def handle_settings(self, args=None):
        import yaml
        import questionary
        from rich.console import Console
        console = Console()
        
        config_dir = os.path.expanduser("~/.atlas")
        config_path = os.path.join(config_dir, "config.yaml")
        
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
            
        config = {}
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                config = yaml.safe_load(f) or {}
                
        console.print("\n[bold cyan]⚙️  Atlas Core Configuration[/bold cyan]")
        
        # Define setting schema
        current_log_level = config.get("log_level", "INFO")
        current_strict_mode = config.get("strict_mode", True)
        current_auto_update = config.get("auto_update", False)
        
        new_log_level = questionary.select(
            "Select Global Log Level:",
            choices=["DEBUG", "INFO", "WARNING", "ERROR"],
            default=current_log_level
        ).ask()
        
        if not new_log_level: return
        
        new_strict_mode = questionary.confirm(
            "Enable Strict Capability Validation?",
            default=current_strict_mode
        ).ask()
        
        if new_strict_mode is None: return
        
        new_auto_update = questionary.confirm(
            "Enable Automatic Standard Library Updates?",
            default=current_auto_update
        ).ask()
        
        if new_auto_update is None: return
        
        config["log_level"] = new_log_level
        config["strict_mode"] = new_strict_mode
        config["auto_update"] = new_auto_update
        
        with open(config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False)
            
        console.print("[bold green]✅ Core settings saved successfully![/bold green]")

# Module-level entry point
_instance = StudioCliWorker()

def on_invoke(capability: str, args: dict):
    return _instance.on_invoke(capability, args)
