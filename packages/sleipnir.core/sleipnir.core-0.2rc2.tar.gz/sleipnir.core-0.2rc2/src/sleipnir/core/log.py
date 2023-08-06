#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Logging module for sleipnir

log provides extensions to the current logging facility provided by
Python. Use 'log' instance from module to invoke an appropiate log
facility to the module in use.

To use, simply 'import log' and use 'log instance
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__status__  = "alpha"
__version__ = "0.1"
__date__    = "19 January 2010"
__license__ = "See LICENSE file for details"

import os
import sys
import logging
import logging.handlers

__all__ = ['log']


class LoggerColorFormatter(logging.Formatter):
    """Custom colored formatter for logging module"""

    def format(self, record):
        """Format message according to record level name"""

        def color(level=None):
            """
            Returns a string to format log message according to level
            severity
            """

            codes = {\
                None:       (0,   0),
                'DEBUG':    (0,   2),  # grey
                'INFO':     (0,   0),  # normal
                'WARNING':  (1,  34),  # blue
                'ERROR':    (1,  31),  # red
                'CRITICAL': (1, 101),  # black, red
                }
            return (chr(27) + '[%d;%dm') % codes[level]

        retval = logging.Formatter.format(self, record)
        return color(record.levelname) + retval + color()


# pylint: disable-msg=R0903
class LoggerHandler(object):
    """
    Create sleipnir handlers customized for each module

    Based on '__params' privagte class variable, define appropiate
    severity levels for each of the handlers used by sleipnir
    """

    __params = {
        'syslog': {
            'hlevels':
                logging.WARNING,
            },
        'stderr': {
            'hlevels':
                logging.DEBUG,
            },
        None: {
            }
    }
    handlers = {}

    def __init__(self, **kwargs):
        SYSLOG_DEV = '/dev/log'

        hformat = kwargs['hformat'] if 'hformat' in kwargs else None
        handler = kwargs['handler'] if 'handler' in kwargs else None
        hlevels = kwargs['hlevels'] if 'hlevels' in kwargs else None

        if handler in self.handlers:
            return

        if handler in ('file',) and 'logfile' in kwargs:
            hdlr = logging.FileHandler(kwargs['logfile'])

        # This special socket doesn't exists on Maemo5 SDK.
        # Check it existence first
        elif handler in ('syslog', 'unix',):
            if os.path.exists(SYSLOG_DEV):
                hdlr = logging.handlers.SysLogHandler(SYSLOG_DEV)
            else:
                hdlr = logging.StreamHandler(sys.stderr)

        elif handler in ('stderr',):
            hdlr = logging.StreamHandler(sys.stderr)
        elif handler in (None,):
            hdlr = logging.handlers.BufferingHandler(0)
        self.handlers[handler] = hdlr

        if not hformat:
            hformat = 'Slp[%(name)s] (%(module)s) %(levelname)s: %(message)s'
            if handler in ('file', 'stderr',):
                hformat = '%(asctime)s ' + hformat

        datefmt = ''
        if handler in ('stderr',):
            datefmt = '%X'

        formatter = LoggerColorFormatter(hformat, datefmt)
        self.handlers[handler].setFormatter(formatter)
        self.handlers[handler].setLevel(hlevels)

    @classmethod
    def create(cls, handler=None):
        """
        Create and return a valid handler following according to
        'handler' param
        """

        # pylint: disable-msg=W0142
        LoggerHandler(handler=handler, **cls.__params[handler])
        return cls.handlers[handler]


class Logger(logging.Logger):
    """
    Define a set of custom handlers to be used for a concrete module

    Keyword arguments:
    handlers -- An iterable set of valid handlers to be used with this
    logger
    level -- Minimal log level to be used for this logger. Less severe
    log messages will simply be ignored

    """

    def __init__(self, *args, **kwargs):
        hdlrs = (None,)
        if 'handlers' in kwargs:
            hdlrs = kwargs['handlers']
            del kwargs['handlers']
        logging.Logger.__init__(self, *args, **kwargs)

        for hdlr in hdlrs:
            self.addHandler(LoggerHandler.create(handler=hdlr))
        self.setLevel(kwargs['level'])


class _LoggerDict(dict):
    """A Custom dict to allow access to key elements like
    attributes"""

    def __getattr__(self, name):
        if name in self:
            return self[name]
        raise AttributeError(name)


# pylint: disable-msg=C0103
log = _LoggerDict({\
        'components':
            Logger("COMPONENTS",
                   handlers=('syslog', 'stderr',),
                   level=logging.WARNING),
        'console':
            Logger("CONSOLE",
                   handlers=('syslog', 'stderr',),
                   level=logging.WARNING),
        'controller':
            Logger("CONTROLLER",
                   handlers=('syslog', 'stderr',),
                   level=logging.WARNING),
        'core':
            Logger("CORE",
                   handlers=('syslog', 'stderr',),
                   level=logging.WARNING),
        'fremantle':
            Logger("FREMANTLE",
                   handlers=('syslog', 'stderr',),
                   level=logging.WARNING),
        'parser':
            Logger("PARSER",
                   handlers=('syslog', 'stderr',),
                   level=logging.WARNING),
        'plugins':
            Logger("PLUGINS",
                   handlers=('syslog', 'stderr',),
                   level=logging.WARNING),
        'profiles':
            Logger("PROFILES",
                   handlers=('syslog', 'stderr',),
                   level=logging.WARNING),
        'sections':
            Logger("TSP-SECTIONS",
                   handlers=('syslog', 'stderr',),
                   level=logging.WARNING),
        'tsplib':
            Logger("TSPLIB",
                   handlers=('syslog', 'stderr',),
                   level=logging.WARNING),

})
