#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""Decorator"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "LGPL"

# Import Here any required modules for this module.
from warnings import warn

warn(
    "'decorator' module is deprecated. Try decorators instead",
    DeprecationWarning,
    stacklevel=2)

# local submodule requirements
from .decorators import profile

# public variables
__all__ = ['profile', ]
