from rich.console import Console
console = Console()
import argparse
import sys
import os
import importlib.util

def handle_suite(args: argparse.Namespace) -> None:
    if args.suite_command != "run":
        console.print(f"Unknown suite command: {args.suite_command}")
        sys.exit(1)

    manager = args.manager.lower()
    
    # 1. Path Resolution Magic
    # Determine the atlas framework root directory dynamically.
    # We are in sdk/cli/commands/suite.py. We need to go up 4 levels to reach the root.
    cli_dir = os.path.dirname(os.path.abspath(__file__))
    sdk_dir = os.path.dirname(os.path.dirname(cli_dir))
    atlas_root = os.path.dirname(sdk_dir)
    
    # Verify we found the root by checking if 'suite' directory exists
    suite_dir = os.path.join(atlas_root, "suite")
    if not os.path.isdir(suite_dir):
        console.print(f"❌ Error: Cannot resolve Atlas framework root. Expected suite directory at {suite_dir}")
        sys.exit(1)
        
    manager_dir = os.path.join(suite_dir, manager)
    if not os.path.isdir(manager_dir):
        console.print(f"❌ Error: Atlas manager '{manager}' is not installed or does not exist at {manager_dir}")
        sys.exit(1)

    main_script = os.path.join(manager_dir, "main.py")
    if not os.path.isfile(main_script):
        console.print(f"❌ Error: Entry point '{main_script}' not found for manager '{manager}'")
        sys.exit(1)

    # 2. Inject Atlas into the path so the manager can import `runtime` and `sdk`
    if atlas_root not in sys.path:
        sys.path.insert(0, atlas_root)
        
    console.print(f"🚀 Booting Atlas {manager.capitalize()}...")
    
    # 3. Dynamically load and execute the manager's main.py
    module_name = f"atlas.suite.{manager}.main"
    spec = importlib.util.spec_from_file_location(module_name, main_script)
    if spec is None or spec.loader is None:
        console.print(f"❌ Error: Failed to load module spec for {main_script}")
        sys.exit(1)
        
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    
    try:
        spec.loader.exec_module(module)
        if hasattr(module, "main"):
            module.main()
        else:
            console.print(f"❌ Error: Manager '{manager}' does not have a main() function in its main.py")
            sys.exit(1)
    except KeyboardInterrupt:
        console.print(f"\n👋 Exiting Atlas {manager.capitalize()}...")
        sys.exit(0)
    except Exception as e:
        console.print(f"❌ Error executing Atlas {manager.capitalize()}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
