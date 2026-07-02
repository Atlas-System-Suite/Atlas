import os
import sys
import asyncio
import importlib.util
import inspect
from rich.console import Console
from rich.panel import Panel

def handle_dev(args):
    console = Console()
    
    console.print(Panel.fit(
        "[bold cyan]Atlas Native Development Server[/bold cyan]\n[dim]Atlas 0.2 Developer Experience[/dim]", 
        border_style="cyan"
    ))
    
    app_path = os.path.abspath(args.app)
    if not os.path.exists(app_path):
        console.print(f"[bold red]❌ Error:[/bold red] App definition not found at [yellow]{app_path}[/yellow]")
        console.print("[dim]Did you create an App instance in src/manager.py?[/dim]")
        sys.exit(1)
        
    project_root = os.path.dirname(os.path.dirname(app_path))
    app_dir = os.path.dirname(app_path)
    
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    if app_dir not in sys.path:
        sys.path.insert(0, app_dir)
        
    console.print("[dim]Loading App topology...[/dim]")
    try:
        spec = importlib.util.spec_from_file_location("atlas.dev.app", app_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules["atlas.dev.app"] = module
        spec.loader.exec_module(module)
    except Exception as e:
        console.print(f"[bold red]❌ Error loading App:[/bold red] {e}")
        sys.exit(1)
    
    app = getattr(module, "app", None)
    if not app:
        console.print(f"[bold red]❌ Error:[/bold red] No 'app' variable exported in {app_path}")
        sys.exit(1)
        
    console.print(f"[bold green]✔ Loaded App:[/bold green] {app.name} (v{app.version})")
    
    # Instantiate Workers using the new DI injection system
    from atlas_sdk.testing import MockRuntime
    runtime = MockRuntime()
    
    workers = []
    # Sort so entry is last (cheap dependency resolution for dev mode)
    sorted_workers = [w for w in app.workers if w != app.entry]
    if app.entry:
        sorted_workers.append(app.entry)
        
    for w in sorted_workers:
        console.print(f"[dim]  Booting worker:[/dim] {w.__name__}")
        try:
            instance = runtime.register(w)
            workers.append(instance)
        except Exception as e:
            console.print(f"[bold red]❌ Failed to boot {w.__name__}:[/bold red] {e}")
            sys.exit(1)
        
    console.print("[bold green]✔ Runtime initialized.[/bold green]")
    
    entry_instance = next((w for w in workers if isinstance(w, app.entry)), None)
    if not entry_instance:
        console.print("[bold red]❌ Error:[/bold red] Entry point worker not found.")
        sys.exit(1)
        
    async def _run():
        console.print("\n[bold cyan]▶ Starting application loop...[/bold cyan]\n")
        try:
            if hasattr(entry_instance, "on_start"):
                res = entry_instance.on_start()
                if inspect.isawaitable(res):
                    await res
        except KeyboardInterrupt:
            pass
        except Exception as e:
            console.print(f"[bold red]❌ Runtime Error:[/bold red] {e}")
            from rich.traceback import install
            install(show_locals=False)
            raise
            
    try:
        asyncio.run(_run())
        console.print("\n[bold yellow]⏹ Shutting down Atlas Dev Server...[/bold yellow]")
    except KeyboardInterrupt:
        console.print("\n[bold yellow]⏹ Shutting down Atlas Dev Server...[/bold yellow]")
