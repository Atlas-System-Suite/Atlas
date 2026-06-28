# Building Managers 🏗️

Welcome to the **Atlas Manager Construction Guide**! If Workers are the musicians in the orchestra, the **Manager** is the conductor. 

A Manager's job is not to play the instruments (execute business logic). Its job is to assemble the musicians, give them the sheet music (configuration), tell them where to sit, and start the show. 

Let's dive into how to build Managers in Atlas!

---

## What is a Manager?

In Atlas, a Manager is an application orchestrator. It uses the `ManagerBuilder` to:
1. Declare which Workers are required for the application to function.
2. Provide configuration values (like API keys, ports, or log levels).
3. Generate a finalized `atlas.yaml` manifest that the Atlas Runtime uses to boot the system.

A Manager **never contains business logic**. If you find yourself writing `if/else` statements about your domain inside a Manager, you've gone astray. Put that logic in a Worker!

---

## 1. Scaffolding a Manager

The easiest way to start is using the Atlas CLI wizard.

```bash
atlas new
```
Then select `manager` when prompted.

Or use the fast-path:
```bash
atlas new manager my_first_app
cd my_first_app
```

This generates a project with a `main.py`, a `README.md`, and an `atlas.yaml`.

---

## 2. Using the ManagerBuilder

Open your `main.py` file. You'll see the `ManagerBuilder` in action. The Builder pattern provides a fluent, chainable API for composing your application.

```python
from atlas_sdk import ManagerBuilder

def build():
    # 1. Initialize the builder with metadata
    manager = ManagerBuilder("my_first_app", version="1.0.0", description="My awesome Atlas app")
    
    # 2. Add required Workers by their IDs
    manager.add_worker("atlas.core.logger")
    manager.add_worker("atlas.core.storage")
    manager.add_worker("atlas.core.clock")
    manager.add_worker("my.custom.ui_worker")
    
    # 3. Inject configuration variables
    manager.configure("LOG_LEVEL", "DEBUG")
    manager.configure("STORAGE_PATH", "/var/lib/atlas/data")
    manager.configure("PORT", "8080")
    
    # 4. Finalize the build
    app_manifest = manager.build()
    
    # 5. Write the finalized manifest to disk
    app_manifest.write("atlas.yaml")
    
    print(f"Manager '{app_manifest.name}' built successfully!")
    return app_manifest

if __name__ == "__main__":
    build()
```

### Breaking it down:
- `ManagerBuilder(name, ...)`: Sets up the identity of your application.
- `.add_worker(worker_id)`: Tells Atlas that this application *requires* these workers. When the runtime boots, it will search the ecosystem for these workers and load them. If it can't find them, it will fail fast.
- `.configure(key, value)`: Injects configuration variables into the global application state. Workers that depend on the `ConfigModel` will be able to read these values.
- `.build()`: Returns a compiled `Manager` object.
- `.write("atlas.yaml")`: Serializes the Manager into the standard Atlas declarative format.

---

## 3. The Generated Manifest (`atlas.yaml`)

When you run your `main.py` script (`python main.py`), it generates an `atlas.yaml` file. This file is the **Source of Truth** for the Atlas Runtime.

It will look something like this:

```yaml
kind: manager
id: atlas.my_first_app
name: MyFirstApp
version: 1.0.0
description: My awesome Atlas app

workers:
  - id: atlas.core.logger
  - id: atlas.core.storage
  - id: atlas.core.clock
  - id: my.custom.ui_worker

config:
  LOG_LEVEL: DEBUG
  STORAGE_PATH: /var/lib/atlas/data
  PORT: "8080"
```

> **Why two steps?** Why use a Python script to generate a YAML file?
> Because Python allows you to dynamically compose your application (e.g., pulling configuration from a `.env` file, environment variables, or a remote secret store during the build phase), while the YAML file ensures the runtime execution remains purely declarative and deterministic.

---

## 4. Running the Manager

Once your `atlas.yaml` is generated, you boot the entire application using the Atlas CLI:

```bash
atlas run
```

The CLI will:
1. Read `atlas.yaml`.
2. Boot the Atlas Runtime.
3. Discover and load `atlas.core.logger`, `atlas.core.storage`, `atlas.core.clock`, and `my.custom.ui_worker`.
4. Inject the `config` block into the `ConfigModel`.
5. Wire all the Capabilities and Invocations together.
6. Start the event loop.

---

## 5. Advanced Configuration (Dynamic Builds)

Because your Manager is a Python script, you aren't limited to hardcoded strings! You can dynamically pull configuration at build time.

```python
import os
from atlas_sdk import ManagerBuilder

def build():
    builder = ManagerBuilder("production_app", version="2.0.0")
    
    # Standard workers
    builder.add_worker("atlas.core.logger")
    
    # Inject secrets from the environment building the manager
    db_password = os.getenv("DB_PASSWORD")
    if not db_password:
        raise ValueError("DB_PASSWORD environment variable is required to build this Manager!")
        
    builder.configure("DB_PASSWORD", db_password)
    
    # Maybe add a debug worker only if we are in debug mode
    if os.getenv("DEBUG_MODE") == "1":
        builder.add_worker("atlas.tools.inspector")
        builder.configure("LOG_LEVEL", "DEBUG")
    else:
        builder.configure("LOG_LEVEL", "INFO")
        
    manager = builder.build()
    manager.write("atlas.yaml")
```

---

## Best Practices 🌟

1. **Keep it declarative**: Use the Python script to *build* the configuration, but don't try to sneak runtime business logic into `main.py`. Once `atlas run` starts, your `main.py` is no longer executing!
2. **Fail fast at build time**: If your app requires a specific environment variable to function, raise an error in `main.py` if it's missing, rather than letting the worker crash at runtime.
3. **Commit the script, ignore the YAML**: If your Manager pulls dynamic secrets (like API keys) from the environment, add `atlas.yaml` to your `.gitignore`. You don't want to accidentally commit secrets to version control! Only commit the `main.py` script.

---

Now that you know how to compose your Workers into a symphony, go build something amazing! 🎵
