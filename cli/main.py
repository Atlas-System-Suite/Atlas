"""
Atlas CLI — Main Entry Point
=============================

The official command-line interface for Atlas development.

Usage:
    atlas new worker my_worker
    atlas run
    atlas test
    atlas doctor
    atlas validate
    atlas inspect
    atlas info
    atlas clean
"""

import argparse
import sys


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="atlas",
        description="Atlas CLI — The official developer interface for the Atlas Software Platform.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- atlas new ---
    new_parser = subparsers.add_parser("new", help="Scaffold a new Atlas project")
    new_parser.add_argument(
        "type",
        nargs="?",
        choices=["worker", "model", "adapter", "manager"],
        help="Type of project to create",
    )
    new_parser.add_argument("name", nargs="?", help="Name of the project")
    new_parser.add_argument(
        "--namespace", default="atlas", help="Identifier namespace (default: atlas)"
    )
    new_parser.add_argument(
        "--language", default="python", help="Implementation language (default: python)"
    )
    new_parser.add_argument(
        "--template", default=None, help="Template variant to use"
    )

    # --- atlas run ---
    run_parser = subparsers.add_parser("run", help="Run the Atlas application")
    run_parser.add_argument(
        "--manifest", default="atlas.yaml", help="Path to the manifest file"
    )

    # --- atlas test ---
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument(
        "--generate", action="store_true", help="Generate test stubs from manifests"
    )

    # --- atlas doctor ---
    subparsers.add_parser("doctor", help="Validate your development environment")

    # --- atlas validate ---
    validate_parser = subparsers.add_parser("validate", help="Validate manifests")
    validate_parser.add_argument(
        "--manifest", default="atlas.yaml", help="Path to manifest"
    )

    # --- atlas inspect ---
    inspect_parser = subparsers.add_parser("inspect", help="Inspect a Worker or Manager")
    inspect_parser.add_argument(
        "--manifest", default="atlas.yaml", help="Path to manifest"
    )

    # --- atlas info ---
    subparsers.add_parser("info", help="Show Atlas SDK info")

    # --- atlas clean ---
    subparsers.add_parser("clean", help="Clean build artifacts")

    # --- atlas build ---
    build_parser = subparsers.add_parser("build", help="Build an .atlas package")
    build_parser.add_argument(
        "--output", default="dist", help="Output directory"
    )

    return parser


def main():
    parser = create_parser()
    
    # Fast-path for artifact discovery if command isn't a known primitive
    # The known commands from argparse:
    known_commands = {"new", "run", "test", "doctor", "validate", "inspect", "info", "clean", "build"}
    
    # Check if we should print the banner
    if len(sys.argv) == 1 or "-h" in sys.argv or "--help" in sys.argv:
        from rich.console import Console
        from rich.panel import Panel
        from rich.text import Text
        
        console = Console()
        logo = (
            "\n[bold cyan]    ▲[/bold cyan]\n"
            "[bold cyan]   ▲ ▲[/bold cyan]    [bold white]ATLAS[/bold white]\n"
            "[bold cyan]  ▲ ▲ ▲[/bold cyan]   [dim white]The Universal Software Architecture Platform[/dim white]\n"
        )
        
        # Override help formatting
        if len(sys.argv) == 1 or "-h" in sys.argv or "--help" in sys.argv:
            console.print(logo)
        
        from rich.table import Table
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Command", style="bold green", width=20)
        table.add_column("Description", style="dim")
        
        table.add_row("new", "Scaffold a new Atlas project (Worker, Model, Adapter, Manager)")
        table.add_row("run", "Run the Atlas application from atlas.yaml")
        table.add_row("test", "Run tests and generate stubs")
        table.add_row("doctor", "Validate your development environment")
        table.add_row("validate", "Validate manifest files")
        table.add_row("inspect", "Inspect a Worker or Manager's capabilities")
        table.add_row("info", "Show Atlas SDK info")
        table.add_row("clean", "Clean build artifacts")
        table.add_row("build", "Build an .atlas package")
        table.add_row("studio", "Launch the Atlas Studio interactive workspace manager")
        
        console.print("\n[bold cyan]Available Commands:[/bold cyan]")
        console.print(table)
        console.print("\n[dim]Use `atlas <command> --help` for more information on a specific command.[/dim]")
        sys.exit(0)
        
    if len(sys.argv) > 1 and sys.argv[1] not in known_commands and not sys.argv[1].startswith("-"):
        # Treat sys.argv[1] as a manager alias and bypass argparse
        class DummyArgs:
            pass
        args = DummyArgs()
        args.command = sys.argv[1]
    else:
        args = parser.parse_args()

    if getattr(args, "command", None) is None:
        parser.print_help()
        sys.exit(0)

    if args.command == "new":
        from .commands.new import handle_new
        handle_new(args)
    elif args.command == "run":
        from .commands.run import handle_run
        handle_run(args)
    elif args.command == "test":
        from .commands.test import handle_test
        handle_test(args)
    elif args.command == "doctor":
        from .commands.doctor import handle_doctor
        handle_doctor(args)
    elif args.command == "validate":
        from .commands.validate import handle_validate
        handle_validate(args)
    elif args.command == "inspect":
        from .commands.inspect import handle_inspect
        handle_inspect(args)
    elif args.command == "info":
        from .commands.info import handle_info
        handle_info(args)
    elif args.command == "clean":
        from .commands.clean import handle_clean
        handle_clean(args)
    elif args.command == "build":
        from .commands.build import handle_build
        handle_build(args)
    else:
        # Artifact Discovery Fallback
        # The command is not a primitive command. Let's see if it's a manager alias.
        import os
        from atlas_sdk.discovery import DiscoveryEngine
        import importlib.util
        from rich.console import Console
        console = Console()
        
        # We need the atlas root directory to start crawling.
        # sdk/cli/main.py -> sdk/cli -> sdk -> atlas
        atlas_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        engine = DiscoveryEngine(atlas_root)
        
        manager_info = engine.find_manager_by_alias(args.command)
        if not manager_info:
            console.print(f"[bold red]❌ Unknown command or manager:[/bold red] [yellow]{args.command}[/yellow]")
            parser.print_help()
            sys.exit(1)
            
        # We found a manager! Boot it up.
        manager_dir = manager_info["path"]
        main_script = os.path.join(manager_dir, "main.py")
        
        if not os.path.isfile(main_script):
            console.print(f"[bold red]❌ Error:[/bold red] Manager '{args.command}' discovered, but missing main.py entry point at {manager_dir}")
            sys.exit(1)
            
        # Ensure atlas root is in path
        if atlas_root not in sys.path:
            sys.path.insert(0, atlas_root)
            
        console.print(f"[bold cyan]🚀 Launching {manager_info['manifest'].get('name', args.command)}...[/bold cyan]")
        
        # Dynamically load and execute
        module_name = f"atlas.dynamic_manager.{args.command}.main"
        spec = importlib.util.spec_from_file_location(module_name, main_script)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            try:
                spec.loader.exec_module(module)
                if hasattr(module, "main"):
                    # Pass the rest of the arguments to the manager's main function
                    module.main(sys.argv[2:])
                else:
                    console.print(f"[bold red]❌ Error:[/bold red] Manager '{args.command}' missing main() function in {main_script}")
                    sys.exit(1)
            except KeyboardInterrupt:
                console.print(f"\n[bold yellow]👋 Exited {args.command}.[/bold yellow]")
                sys.exit(0)
            except Exception as e:
                console.print(f"[bold red]❌ Error executing manager '{args.command}':[/bold red] {e}")
                from rich.traceback import install
                install(show_locals=False)
                raise
        else:
            console.print(f"[bold red]❌ Error:[/bold red] Failed to load module {main_script}")
            sys.exit(1)


if __name__ == "__main__":
    main()
