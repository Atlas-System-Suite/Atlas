"""
Atlas SDK — Project Generator
==============================

Generates boilerplate for Workers, Managers, Models, and Adapters.
"""

import os
import textwrap

# ---------------------------------------------------------
# Templates (embedded for zero-dependency operation)
# ---------------------------------------------------------

WORKER_MANIFEST = textwrap.dedent("""\
    kind: worker
    id: {namespace}.{name}
    name: {class_name}
    version: {version}
    description: {description}
    language: {language}
    roles: [worker]

    execution:
      policy: singleton

    communication:
      transports: [memory]
      formats: [{language}]
      default_format: {language}

    imports: []

    exports:
      - capability: {namespace}.{name}
        version: {version}

    translations: []
""")

WORKER_PY = textwrap.dedent('''\
    """
    {class_name} — An Atlas Worker
    
    {description}
    """
    from atlas_sdk import WorkerBase, capability, on_invocation


    class {class_name}(WorkerBase):
        _worker_id = "{namespace}.{name}"
        _worker_name = "{class_name}"
        _worker_version = "{version}"
        _worker_roles = ["worker"]

        def on_init(self):
            """Called after construction. Set up your state here."""
            pass

        def on_start(self):
            """Called when the runtime starts this worker."""
            pass

        def on_stop(self):
            """Called on shutdown. Clean up resources here."""
            pass

        @capability("{namespace}.{name}.hello", version="{version}")
        @on_invocation("hello")
        def hello(self, name: str = "World") -> str:
            """A simple hello capability. Replace me with real logic!"""
            return f"Hello, {{name}}! From {class_name}."
''')

WORKER_TEST = textwrap.dedent('''\
    """Tests for {class_name}."""
    from atlas_sdk.testing import MockRuntime, assert_capability_exported
    from {module_path} import {class_name}


    def test_{safe_name}_exports_capability():
        worker = {class_name}()
        assert_capability_exported(worker, "{namespace}.{name}.hello")


    def test_{safe_name}_hello():
        runtime = MockRuntime()
        runtime.register({class_name}, "{namespace}.{name}")
        result = runtime.invoke("{namespace}.{name}", "hello", {{"name": "Atlas"}})
        assert "Hello" in result
''')

WORKER_README = textwrap.dedent("""\
    # {class_name}

    {description}

    ## Capabilities

    - `{namespace}.{name}.hello` — Greets you by name.

    ## Usage

    ```python
    from {module_path} import {class_name}

    worker = {class_name}()
    console.print(worker.hello("Atlas"))
    ```

    ## Testing

    ```bash
    atlas test
    ```
""")

MODEL_PY = textwrap.dedent('''\
    """
    {class_name} — An Atlas Model
    
    {description}
    """
    from abc import abstractmethod
    from atlas_sdk import ModelBase, model_version


    @model_version("{version}")
    class {class_name}(ModelBase):
        """
        Define the abstract contract for {name}.
        Workers that implement this model must provide all methods below.
        """

        @abstractmethod
        def process(self, data: str) -> str:
            """Process the input data. Replace with your real contract."""
            ...
''')

MODEL_TEST = textwrap.dedent('''\
    """Compliance tests for {class_name}."""
    from atlas_sdk.testing import assert_model_compliant
    from {module_path} import {class_name}


    class Dummy{class_name}Impl({class_name}):
        """A dummy implementation for compliance testing."""
        def process(self, data: str) -> str:
            return data.upper()


    def test_dummy_is_compliant():
        assert_model_compliant({class_name}, Dummy{class_name}Impl)


    def test_contract_introspection():
        contract = {class_name}.get_contract()
        method_names = [m["method"] for m in contract]
        assert "process" in method_names
''')

ADAPTER_MANIFEST = textwrap.dedent("""\
    kind: adapter
    id: {namespace}.adapter.{name}
    name: {class_name}
    version: {version}
    description: {description}
    language: {language}
    roles: [translator]

    execution:
      policy: singleton

    communication:
      transports: [memory]
      formats: [{language}]
      default_format: {language}

    imports: []
    exports: []

    translations:
      - source_format: source
        target_format: target
        cost: 1
""")

ADAPTER_PY = textwrap.dedent('''\
    """
    {class_name} — An Atlas Adapter
    
    {description}
    """
    from atlas_sdk import AdapterBase, translation


    class {class_name}(AdapterBase):
        _adapter_id = "{namespace}.adapter.{name}"
        _adapter_name = "{class_name}"
        _adapter_version = "{version}"

        @translation(source="source_format", target="target_format", cost=1)
        def convert(self, data: bytes) -> bytes:
            """Convert data from source to target format. Replace me!"""
            return data
''')

ADAPTER_TEST = textwrap.dedent('''\
    """Tests for {class_name}."""
    from {module_path} import {class_name}


    def test_{safe_name}_translates():
        adapter = {class_name}()
        result = adapter.convert(b"hello")
        assert result == b"hello"


    def test_{safe_name}_has_translations():
        adapter = {class_name}()
        translations = adapter.get_translations()
        assert len(translations) >= 1
''')

PRODUCT_YAML = textwrap.dedent("""\
    kind: manager
    id: {namespace}.{name}
    name: {class_name}
    version: {version}
    description: {description}

    workers:
      - id: atlas.core.logger
      - id: atlas.core.config
      - id: atlas.core.storage

    config:
      LOG_LEVEL: INFO
""")

PRODUCT_MAIN = textwrap.dedent('''\
    """
    {class_name} — An Atlas Manager
    
    {description}
    """
    from atlas_sdk import ManagerBuilder


    def build():
        manager = (
            ManagerBuilder("{name}", version="{version}", description="{description}")
            .add_worker("atlas.core.logger")
            .add_worker("atlas.core.config")
            .add_worker("atlas.core.storage")
            .configure("LOG_LEVEL", "INFO")
            .build()
        )
        manager.write("atlas.yaml")
        print(f"Manager '{{manager.name}}' built successfully!")
        return manager


    if __name__ == "__main__":
        build()
''')

PRODUCT_README = textwrap.dedent("""\
    # {class_name}

    {description}

    ## Workers

    - `atlas.core.logger`
    - `atlas.core.config`
    - `atlas.core.storage`

    ## Running

    ```bash
    atlas run
    ```
""")

class ProjectGenerator:
    """
    Handles generation of Atlas projects.
    """

    def generate(self, config: dict):
        """
        Generates a project from a config dict containing:
        - type: 'worker', 'manager', 'model', or 'adapter'
        - name: The project name
        - class_name: The camel cased class name
        - namespace: The prefix (e.g. 'atlas')
        - language: The programming language
        - version: Version string
        - description: Project description
        - dest_dir: Destination directory path
        """
        os.makedirs(config["dest_dir"], exist_ok=True)
        
        # We also need module_path for Python imports
        config["module_path"] = "worker" if config["type"] == "worker" else "model" if config["type"] == "model" else "adapter"
        config["safe_name"] = config["name"].replace("-", "_")
        
        if config["language"].lower() != "python":
            raise NotImplementedError(f"Language support for '{config['language']}' is coming soon! (Atlas currently focuses on its Python SDK).")

        if config["type"] == "worker":
            self._write(config["dest_dir"], "atlas.yaml", WORKER_MANIFEST.format(**config))
            self._write(config["dest_dir"], "worker.py", WORKER_PY.format(**config))
            self._write(config["dest_dir"], f"test_{config['name']}.py", WORKER_TEST.format(**config))
            self._write(config["dest_dir"], "README.md", WORKER_README.format(**config))

        elif config["type"] == "model":
            self._write(config["dest_dir"], "model.py", MODEL_PY.format(**config))
            self._write(config["dest_dir"], f"test_{config['name']}.py", MODEL_TEST.format(**config))

        elif config["type"] == "adapter":
            self._write(config["dest_dir"], "atlas.yaml", ADAPTER_MANIFEST.format(**config))
            self._write(config["dest_dir"], "adapter.py", ADAPTER_PY.format(**config))
            self._write(config["dest_dir"], f"test_{config['name']}.py", ADAPTER_TEST.format(**config))

        elif config["type"] == "manager":
            self._write(config["dest_dir"], "atlas.yaml", PRODUCT_YAML.format(**config))
            self._write(config["dest_dir"], "main.py", PRODUCT_MAIN.format(**config))
            self._write(config["dest_dir"], "README.md", PRODUCT_README.format(**config))

    def _write(self, directory: str, filename: str, content: str):
        path = os.path.join(directory, filename)
        with open(path, "w") as f:
            f.write(content)
