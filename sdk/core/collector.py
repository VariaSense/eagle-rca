"""Collector SDK for connector agents."""
from __future__ import annotations

from typing import Any, Dict, Optional, Type
import importlib


CollectorResult = Dict[str, Any]
CollectorConfig = Dict[str, Any]

_REGISTRY: Dict[str, Type["BaseCollector"]] = {}


class BaseCollector:
    """Base class for agent collectors."""

    name: str = "base"

    def __init__(self, config: Optional[CollectorConfig] = None):
        self.config = config or {}

    def collect(self) -> CollectorResult:
        """Return {'metrics': {...}, 'payload': {...}}."""
        return {"metrics": {}, "payload": {}}


def register_collector(name: str):
    """Register a collector class under a name."""

    def decorator(cls: Type[BaseCollector]) -> Type[BaseCollector]:
        cls.name = name
        _REGISTRY[name] = cls
        return cls

    return decorator


def load_collector(spec: Any) -> BaseCollector:
    """Create a collector from a registry name or spec dict."""
    if isinstance(spec, str):
        name = spec
        config = {}
        module_path = None
        class_name = None
    elif isinstance(spec, dict):
        name = spec.get("name")
        config = spec.get("config") or {k: v for k, v in spec.items() if k not in {"name", "module", "class"}}
        module_path = spec.get("module")
        class_name = spec.get("class")
    else:
        raise ValueError("Collector spec must be a name or dict")

    if name in _REGISTRY:
        return _REGISTRY[name](config)

    if module_path and class_name:
        module = importlib.import_module(module_path)
        cls = getattr(module, class_name)
        if not issubclass(cls, BaseCollector):
            raise ValueError(f"Collector {class_name} must extend BaseCollector")
        return cls(config)

    raise ValueError(f"Unknown collector: {name}")


def available_collectors() -> Dict[str, Type[BaseCollector]]:
    return dict(_REGISTRY)
