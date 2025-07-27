"""
Shared utilities for microservices architecture.

This package contains common functionality used across all microservices:
- Authentication and security
- Caching utilities
- Rate limiting
- Configuration management
- Logging
- HTTP client utilities
"""

__version__ = "1.0.0"

from .auth import *
from .cache import *
from .config import *
from .http_client import *
from .log_utils import *
from .rate_limiter import *

# Backward-compatibility alias: allow `from common.logging import …` to work
import importlib, sys as _sys
_sys.modules[f"{__name__}.logging"] = importlib.import_module(f"{__name__}.log_utils")

__all__ = [
    "auth",
    "cache", 
    "config",
    "http_client",
    "log_utils",
    "rate_limiter"
] 