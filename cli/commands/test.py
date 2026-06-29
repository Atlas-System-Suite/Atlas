"""
atlas test — Run tests for an Atlas project.
"""

import subprocess
import sys


def handle_test(args):
    if args.generate:
        print("🔧 Generating test stubs from manifest...")
        print("   ℹ️  Test generation coming in Sprint 3.")
        return

    print("🧪 Running Atlas tests...")
    print()

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-v"],
        cwd=".",
    )

    if result.returncode == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Tests failed with exit code {result.returncode}")
        sys.exit(result.returncode)
