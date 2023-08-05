#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
AbstractFactory

Implementation of the AbstractFactory Pattern (GOF94) idiom in Python
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules.
from itertools import ifilter

__all__ = ['AbstractFactory']

# local submodule requirements
from .singleton import Singleton
from .decorators import deprecated


class AbstractFactoryError(Exception):
    """AbstractFactory error"""


class NamedAbstractFactory(Singleton):
    """
    Allows to internally build a valid abstract for args passsed to
    'can_handle' method of declared abstracts

    As a contract, Something smells like a Abstract sii:
      o It's registered into AbstractFactory
      o Implements a class method called 'can_handle'
    """

    ignore_subsequents = True

    def __init__(self, error=AbstractFactoryError):
        super(NamedAbstractFactory, self).__init__()
        self._ex_error = error
        self._backends = {}

    def __contains__(self, key):
        return key in self.backends

    def __iter__(self):
        return self._backends.iteritems()

    @property
    def backends(self):
        """Get registered backends"""
        return self._backends

    def create(self, *args, **kwargs):
        """Build a valid abstract"""
        has_handle = lambda x: hasattr(x, 'can_handle')
        for backend in ifilter(has_handle, self._backends.itervalues()):
            if not backend.can_handle(*args, **kwargs):
                continue
            creator = backend.new  if hasattr(backend, 'new') else backend
            return creator(*args, **kwargs)
        else:
            raise self._ex_error(args)

    def register(self, name, backend):
        """Registry a class implementations as a candidate abstract"""
        if name in self._backends:
            raise TypeError('Already defined %s: %s' % (name, backend))
        self._backends[name] = backend


class AbstractFactory(Singleton):
    """
    Allows to internally build a valid abstract for args passed to
    'can_handle' method of declared abstracts

    As a contract, Something smells like a Abstract sii:
      o It's registered into AbstractFactory
      o Implements a class method called 'can_handle'
    """

    ignore_subsequents = True

    def __init__(self, ex_type=AbstractFactoryError):
        super(AbstractFactory, self).__init__()
        self._backends = []
        self._ex_type = ex_type

    @deprecated('0.2', 'Use NamedAbstractFactory class instead')
    def create(self, *args, **kwargs):
        """Build a valid abstract"""

        for _, backend in self._backends:
            try:
                if backend.can_handle(*args, **kwargs):
                    return backend.new(*args, **kwargs) \
                        if hasattr(backend, 'new')      \
                        else backend(*args, **kwargs)
            except TypeError:
                pass
        raise self._ex_type(args)

    @deprecated('0.2', 'Use register method instead')
    def registry(self, backend):
        """Registry a class implementations as a candidate abstract"""

        self._backends.append(backend)

    @deprecated('0.2', 'Use register method instead')
    def register(self, name, backend):
        """Registry a class implementations as a candidate abstract"""
        self._backends.append((name, backend))
