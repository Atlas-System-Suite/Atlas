"""
Atlas SDK — Adapter Base
=========================

The AdapterBase class provides the canonical way to build Translation
Workers (Adapters). Adapters convert data between formats without
performing any business logic.

Usage:
    from atlas_sdk import AdapterBase, translation

    class JsonToMsgpackAdapter(AdapterBase):
        @translation(source="json", target="msgpack", cost=1)
        def convert(self, data: bytes) -> bytes:
            ...
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List
from dataclasses import dataclass, field
import functools
import inspect
import yaml


# ---------------------------------------------------------
# Metadata
# ---------------------------------------------------------

@dataclass
class TranslationMeta:
    """Metadata attached to a method by the @translation decorator."""
    source_format: str
    target_format: str
    cost: int = 1


# ---------------------------------------------------------
# Decorator
# ---------------------------------------------------------

def translation(source: str, target: str, cost: int = 1):
    """
    Marks a method as a format translation.

    Example::

        @translation(source="json", target="msgpack", cost=1)
        def convert(self, data: bytes) -> bytes:
            ...
    """
    def decorator(func: Callable) -> Callable:
        func._atlas_translation = TranslationMeta(
            source_format=source, target_format=target, cost=cost
        )
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        wrapper._atlas_translation = func._atlas_translation
        return wrapper
    return decorator


# ---------------------------------------------------------
# AdapterBase
# ---------------------------------------------------------

class AdapterBase(ABC):
    """
    Base class for all Atlas Adapters (Translation Workers).

    Adapters are stateless. They convert Format A into Format B.
    Atlas automatically chains them to find multi-hop translation paths.

    Subclass this and use the @translation decorator on your methods.
    """

    _adapter_id: str = ""
    _adapter_name: str = ""
    _adapter_version: str = "1.0.0"

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        translations = []
        for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            if hasattr(method, '_atlas_translation'):
                translations.append({
                    "method": name,
                    "meta": method._atlas_translation,
                })
        cls._atlas_translations = translations

    def get_translations(self) -> List[TranslationMeta]:
        """Returns all registered translation pairs."""
        return [t["meta"] for t in self.__class__._atlas_translations]

    def generate_manifest(self) -> Dict[str, Any]:
        """Auto-generates a manifest for this Adapter."""
        cls = self.__class__
        return {
            "id": cls._adapter_id or f"atlas.adapter.{cls.__name__.lower()}",
            "name": cls._adapter_name or cls.__name__,
            "version": cls._adapter_version,
            "language": "python",
            "roles": ["translator"],
            "execution": {"policy": "singleton"},
            "communication": {
                "transports": ["memory"],
                "formats": ["python"],
                "default_format": "python",
            },
            "imports": [],
            "exports": [],
            "translations": [
                {
                    "source_format": t.source_format,
                    "target_format": t.target_format,
                    "cost": t.cost,
                }
                for t in self.get_translations()
            ],
        }
