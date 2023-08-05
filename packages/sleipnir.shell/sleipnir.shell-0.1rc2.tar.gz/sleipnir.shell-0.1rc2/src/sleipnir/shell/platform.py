#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Platform detector

Checks and returns platform on which current softwarer is running
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules
from operator import attrgetter

__all__ = ['Platform']

# Project requirements
from sleipnir.core.factory import AbstractFactory
from sleipnir.core.singleton import Singleton
from sleipnir.core.decorators import cached

# local submodule requirements

LAST_PRIORITY = 1000000

class PlatformBase(object):
    """Base class to represent platforms"""

    def __init__(self, priority, names):
        self._priority = priority
        self._names = names

    def __contains__(self, value):
        return value in self._names

    @property
    def priority(self):
        """Returns idoneity (priority) for this platform"""
        return self._priority

    @property
    def names(self):
        """Gets a collection of valid names for platform"""
        return self._names

    @property
    def name(self):
        """Get platform id"""
        return self._names[0].lower()

    @property
    def graphics_system(self):
        """Get valid graphics system for platform"""
        return [None, None]

    @property
    def flavor(self):
        """Get os variants"""
        return None

    @classmethod
    def match(cls):
        """Verify that platform is applicable or not"""
        return True


#pylint: disable-msg=R0903
class PlatformWrapper(object):
    """A method delegator pattern for platfroms"""
    def __init__(self, value):
        if type(value) in (str, unicode,):
            values = (value.lower(), value.upper(), value.capitalize(),)
            value = PlatformBase(-1, values)
        self._value = value

    def __getattr__(self, name):
        return getattr(self._value, name)


class Platform(Singleton):
    """Checks and Returns data about current platform"""

    def __init__(self):
        self._factory = PlatformFactory.get_instance()
        self._target  = None

    @property
    def name(self):
        """Get platform name for target or fallback to real"""
        return self.target.name if self.target else self.real.name

    @property
    def real(self):
        """Sort platforms based on idoneity and priority"""
        return self.any[0]

    @property
    def target(self):
        """Returns target platform"""
        return self._target

    @target.setter
    def target(self, value):
        """Set target platform"""

        self._target = value
        # PlatformWrapper is a catch all class. If we don't support
        # platform yet, PlatformWrapper provides a set of probably
        # broken values

        if type(value) in (str, unicode,):
            self._target = PlatformWrapper(value.lower())

            # Now lookup for a valid platform
            for backend in self.all:
                if value in backend:
                    self._target = backend.__class__()

    @property
    @cached
    def any(self):
        """Sort platforms based on idoneity and priority"""
        return [candidate() for candidate in self._factory]

    @property
    @cached
    def all(self):
        return [platform() for platform in self._factory.all]

    def real_is(self, value):
        """Check if platform name is value"""
        return value in self.real.names

    def target_is(self, value):
        """Check if vaule correspond to target paltform"""
        self._target = self._target or self.real
        return value in self._target

    def any_is(self, value):
        """Check if platform name is in any valid platform"""
        return any(value in (candidate for candidate in self.any))

    def all_is(self, value):
        """Check if platform name is in any valid platform"""
        return any(value in (candidate for candidate in self.all))


class PlatformFactory(AbstractFactory):
    """Checks and Returns data about current platform"""

    def __init__(self):
        super(PlatformFactory, self).__init__()

    @property
    @cached
    def any(self):
        """Peek a list of valid platforms sorted by priority"""
        platforms = self.backends.itervalues()
        candidates = [backend for backend in platforms if backend.match()]
        return sorted(candidates, key=attrgetter('priority'))

    @property
    @cached
    def all(self):
        return list(self.backends.itervalues())

    def __iter__(self):
        return iter(self.any)


class MetaPlatform(type):
    """Platform register metaclass"""

    def __init__(mcs, name, bases, dct):
        type.__init__(mcs, name, bases, dct)
        factory = PlatformFactory.get_instance()
        factory.register(name, mcs)
        #factory.clear()


class QtBase(PlatformBase):
    """Base class for apps that requires PySide"""

    @property
    def graphics_system(self):
        return ["raster", None]


class Desktop(PlatformBase):
    """Base class for command objects"""

    __metaclass__ = MetaPlatform

    def __init__(self):
        names = ("DESKTOP", "desktop", "Desktop",)
        super(Desktop, self).__init__(LAST_PRIORITY, names)


class Simulator(QtBase):
    """A base class for Simpulator instances"""

    __metaclass__ = MetaPlatform

    def __init__(self):
        names = ("SIMULATOR", "simulator", "Simulator",)
        super(Simulator, self).__init__(LAST_PRIORITY - 1, names)

    #pylint: disable-msg=W0703
    @classmethod
    def match(cls):
        # First, check for PySide. If not present, we are not in
        # Simulator
        try:
            __import__ ('PySide')
        except ImportError:
            return False
        # Check for QPrinter. This exists on Maemo :O and desktop but
        # not in simulator
        try:
            __import__('PySide.QtGui.QPrinter')
            return False
        except ImportError:
            return True


class Fremantle(QtBase):
    """A Base class for Harmattan instances"""

    __metaclass__ = MetaPlatform

    def __init__(self):
        names = ("FREMANTLE", "Fremantle", "fremantle",)
        super(Fremantle, self).__init__(0, names)

    @property
    @cached
    def flavor(self):
        from os.path import exists
        if exists('/var/lib/dpkg/info/mp-fremantle-generic-pr.list'):
            return "ssu"
        if exists('/var/lib/dpkg/info/mp-fremantle-community.list'):
            return "cssu" 
        #fallback. Probably used on a fake environment
        return super(QtBase, self).flavor

    @property
    def graphics_system(self):
        return ["raster", None] if self.flavor == "ssu" else ["opengl", None]

    #pylint: disable-msg=W0703
    @classmethod
    def match(cls):
        from os.path import exists
        return exists('/var/lib/dpkg/info/mp-fremantle-generic-pr.list')


class FremantleSSU(PlatformBase):

    __metaclass__ = MetaPlatform

    def __init__(self):
        names = ("FREMANTLE-SSU", "Fremantle-ssu", "fremantle-ssu",)
        super(FremantleSSU, self).__init__(0, names)

    @property
    def flavor(self):
        return "ssu"

    #pylint: disable-msg=W0703
    @classmethod
    def match(cls):
        return False

class FremantleCSSU(PlatformBase):

    __metaclass__ = MetaPlatform

    def __init__(self):
        names = ("FREMANTLE-CSSU", "Fremantle-cssu", "fremantle-cssu",)
        super(FremantleCSSU, self).__init__(0, names)

    @property
    def flavor(self):
        return "cssu"

    #pylint: disable-msg=W0703
    @classmethod
    def match(cls):
        return False


class Harmattan(QtBase):
    """A Base class for Harmattan instances"""

    __metaclass__ = MetaPlatform

    def __init__(self):
        names = ("HARMATTAN", "Harmattan", "harmattan",)
        super(Harmattan, self).__init__(0, names)

    @property
    def graphics_system(self):
        return ["meego", None]

    #pylint: disable-msg=W0703
    @classmethod
    def match(cls):
        try:
            with open('/etc/issue') as issue:
                if ('Harmattan' in issue.read()):
                    return True
                return False
        except Exception:
            return False
