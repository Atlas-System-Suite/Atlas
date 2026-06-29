"""
Atlas SDK — Model Base
======================

The ModelBase class provides the canonical way to define official
Atlas Models. Models are abstract contracts that Workers implement.

Usage:
    from atlas_sdk import ModelBase, model_version

    @model_version("1.0.0")
    class GreeterModel(ModelBase):
        def greet(self, name: str) -> str: ...
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Type
from dataclasses import dataclass, field
import inspect
import textwrap


# ---------------------------------------------------------
# Decorators
# ---------------------------------------------------------

def model_version(version: str):
    """
    Tags a Model class with a semantic version.

    Example::

        @model_version("2.1.0")
        class StorageModel(ModelBase): ...
    """
    def decorator(cls):
        cls._model_version = version
        return cls
    return decorator


# ---------------------------------------------------------
# ModelBase
# ---------------------------------------------------------

class ModelBase(ABC):
    """
    Base class for all official Atlas Models.

    A Model defines the abstract contract that one or more Workers
    implement. Models contain NO business logic — only method signatures.
    Think of them as the USB-C spec: everyone agrees on the shape.

    Features:
        - Auto-introspection of abstract methods
        - Compliance test generation
        - Documentation generation
    """

    _model_version: str = "1.0.0"

    @classmethod
    def get_contract(cls) -> List[Dict[str, Any]]:
        """
        Introspects the Model and returns a list of abstract methods
        with their signatures. Used by Solon for compliance validation.
        """
        contract = []
        for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            if getattr(method, '__isabstractmethod__', False):
                sig = inspect.signature(method)
                params = []
                for pname, param in sig.parameters.items():
                    if pname == 'self':
                        continue
                    params.append({
                        "name": pname,
                        "annotation": str(param.annotation) if param.annotation != inspect.Parameter.empty else "Any",
                        "default": str(param.default) if param.default != inspect.Parameter.empty else None,
                    })
                contract.append({
                    "method": name,
                    "params": params,
                    "return_type": str(sig.return_annotation) if sig.return_annotation != inspect.Signature.empty else "Any",
                })
        return contract

    @classmethod
    def check_compliance(cls, implementation: Type) -> Dict[str, Any]:
        """
        Checks whether a given class correctly implements all abstract
        methods defined by this Model.

        Returns a report dict with pass/fail status and missing methods.

        Example::

            report = StorageModel.check_compliance(LocalDiskStorageWorker)
            assert report["compliant"] is True
        """
        contract = cls.get_contract()
        missing = []
        mismatched = []

        for entry in contract:
            method_name = entry["method"]
            impl_method = getattr(implementation, method_name, None)

            if impl_method is None:
                missing.append(method_name)
                continue

            # Check parameter count matches (excluding self)
            expected_params = entry["params"]
            try:
                impl_sig = inspect.signature(impl_method)
                impl_params = [p for p in impl_sig.parameters if p != "self"]
                expected_names = [p["name"] for p in expected_params]
                if impl_params != expected_names:
                    mismatched.append({
                        "method": method_name,
                        "expected": expected_names,
                        "actual": impl_params,
                    })
            except (ValueError, TypeError):
                pass

        compliant = len(missing) == 0 and len(mismatched) == 0

        return {
            "model": cls.__name__,
            "model_version": cls._model_version,
            "implementation": implementation.__name__,
            "compliant": compliant,
            "missing_methods": missing,
            "mismatched_signatures": mismatched,
        }

    @classmethod
    def generate_docs(cls) -> str:
        """
        Auto-generates Markdown documentation for the Model.

        Returns a string containing the rendered docs.
        """
        contract = cls.get_contract()
        lines = [
            f"# {cls.__name__}",
            "",
            f"**Version:** {cls._model_version}",
            "",
            cls.__doc__.strip() if cls.__doc__ else "_No description provided._",
            "",
            "## Methods",
            "",
        ]

        for entry in contract:
            params_str = ", ".join(
                f"{p['name']}: {p['annotation']}" +
                (f" = {p['default']}" if p['default'] else "")
                for p in entry["params"]
            )
            lines.append(f"### `{entry['method']}({params_str}) -> {entry['return_type']}`")
            lines.append("")

        return "\n".join(lines)
