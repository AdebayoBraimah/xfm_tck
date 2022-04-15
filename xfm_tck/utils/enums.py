# -*- coding: utf-8 -*-
"""Enums module for ``xfm_tck``.
"""
from enum import (
    Enum,
    unique
)


@unique
class NiiHeaderField(Enum):
    """NIFTI file header field options."""
    descrip:        str = "descrip"
    intent_name:    str = "intent_name"


@unique
class LogLevel(Enum):
    """Log level enumerators."""
    info:       str = "info"
    debug:      str = "debug"
    critical:   str = "critical"
    error:      str = "error"
    warning:    str = "warning"