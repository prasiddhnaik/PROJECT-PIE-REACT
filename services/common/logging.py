"""DEPRECATED shim.

This file remains only to satisfy imports like ``from common.logging import ...`` that
exist in older code.  All functionality now lives in :pymod:`common.log_utils`.
Please migrate new code to import from ``common.log_utils`` directly.
"""

from warnings import warn as _warn

_warn(
    "common.logging is deprecated; use common.log_utils instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything from the new module.
from .log_utils import *  # type: ignore F401,F403 