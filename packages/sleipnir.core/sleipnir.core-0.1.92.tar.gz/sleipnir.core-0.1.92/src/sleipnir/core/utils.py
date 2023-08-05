#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
utils

A set of useful utils
"""

from __future__ import absolute_import

__author__  = "Ask Solem"
__license__ = "BSD, See LICENSE file for details"

# Import here any required modules.
from uuid import UUID, uuid4 as _uuid4, _uuid_generate_random

import sys
import ctypes


def uuid():
    """
    Generate a unique id, having - hopefully - a very small chance of
    collission. For now this is provided by :func:`uuid.uuid4`.
    """
    def uuid4():
        # Workaround for http://bugs.python.org/issue4607
        if ctypes and _uuid_generate_random:
            buffer = ctypes.create_string_buffer(16)
            _uuid_generate_random(buffer)
            return UUID(bytes=buffer.raw)
        return _uuid4()

    return str(uuid4())


if sys.version_info >= (3, 0):

    def kwdict(kwargs):
        return kwargs
else:
    def kwdict(kwargs):  # noqa
        """
        Make sure keyword arguments are not in unicode.

        This should be fixed in newer Python versions,
        see: http://bugs.python.org/issue4978.

        """
        return dict((key.encode("utf-8"), value)
                    for key, value in kwargs.items())


def maybe_list(v):
    if v is None:
        return []
    if hasattr(v, "__iter__"):
        return v
    return [v]
