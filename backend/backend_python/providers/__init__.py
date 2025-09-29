"""Top-level package for provider implementations.

This package aggregates various data provider subpackages (e.g., `crypto`).
Importing `providers` will make subpackages available for convenient access
and ensure static analysis tools treat this directory as a proper Python
package.
"""

from importlib import import_module
from types import ModuleType
from typing import TYPE_CHECKING, Any


# Lazily import subpackages when accessed as attributes to avoid unnecessary
# import overhead and potential circular dependencies.

def __getattr__(name: str) -> ModuleType:  # type: ignore[override]
    if name == "crypto":
        return import_module(f"{__name__}.crypto")
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def __dir__() -> list[str]:
    return sorted(["crypto"]) 