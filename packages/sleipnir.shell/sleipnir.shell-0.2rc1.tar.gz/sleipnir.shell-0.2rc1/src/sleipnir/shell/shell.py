#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Shell

Main Shell instance
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules

__all__ = ['Shell']

# Project requirements
from sleipnir.core.singleton import Singleton

# local submodule requirements
from .signals import Signal


class ShellError(Exception):
    """Shell Main exception"""


#pylint: disable-msg=E1101,R0921
class Shell(Singleton):
    """ Main Shell"""

    # Quit notifier
    leave = Signal()

    # Signals
    value_changed = Signal()
    value_removed = Signal()

    @property
    def name(self):
        """Shell application unique name"""
        return self._name

    @property
    def values(self):
        """Get an iterable over available values"""
        return (value for value in self._values.itervalues)

    @property
    def objects(self):
        """Get registered objects"""
        return self._known_objects

    def insert(self, name, value):
        """
        Sets a value in the shell with the given name. Any previous
        value will be overridden. "value_changed" signal will be
        emitted. Objects connecting to this signal can then update
        their data according to the new value.
        """
        if name in self._known_objects:
            self._known_objects[name] = value
        else:
            self._values[name] = value
            self.value_changed.emit(name, value)

    def remove(self, name):
        """
        Removes name from values. If not exists, raise a
        ShellError. Previously to remove data, a value_removed is
        fired
        """
        if name not in self._values:
            raise ShellError("'%s' value not found")
        self.value_removed.emit(name)
        del self._values[name]

    def register(self, name, value):
        """
        Register a value as a known object. Changes aren't propagated
        for this kind of values
        """
        self._known_objects.setdefault(name, value)

    def run(self, args, options=None):
        """Starts Application"""
        raise NotImplementedError

    def quit(self):
        """Quits shell"""
        self.leave.emit()

    def __init__(self, name, args=None):
        self._name = name
        self._args = args
        # value subsystem
        self._values = {}
        self._known_objects = {}

    def __getattr__(self, name):
        if name in self._values:
            return self._values[name]
        # Not Found? Raise an error
        raise ShellError("Unknown value '%s'", name)
