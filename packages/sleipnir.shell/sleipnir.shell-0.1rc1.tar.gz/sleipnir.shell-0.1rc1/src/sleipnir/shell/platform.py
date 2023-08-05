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

# local submodule requirements


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


class Platform(object):
    """Checks and Returns data about current platform"""

    def __init__(self, target=None):
        self._factory = PlatformFactory.get_instance()
        self._any = self._real = None
        self.targeted = target

    @property
    def name(self):
        """
        Get platform name for selected target if any or real otherwise
        """
        return self.targeted.name if self.targeted else self.real.name

    @property
    def real(self):
        """Sort platforms based on idoneity and priority"""
        if self._real is None:
            for candidate in self._factory:
                self._real = candidate()
                break
        return self._real

    def real_is(self, value):
        """Check if platform name is value"""
        return value in self.real.names

    @property
    def targeted(self):
        """Returns targeted platform"""
        return self._target

    @targeted.setter
    def targeted(self, value):
        """Set targeted platform"""
        self._target = value
        if type(value) in (str, unicode,):
            self._target = PlatformWrapper(value.lower())
            for backend in self.any:
                if value in backend:
                    self._target = backend.__class__()

    def targeted_is(self, value):
        """Check if vaule correspond to targetted paltform"""
        self._target = self._target or self.real
        return value in self._target

    @property
    def any(self):
        """Sort platforms based on idoneity and priority"""
        if self._any is None:
            candidates = [candidate() for candidate in self._factory]
            self._any = candidates
        return self._any

    def any_is(self, value):
        """Check if platform name is in any valid platform"""
        return any(value in (candidate for candidate in self.any))

    def clear(self):
        """Clear cached values for any and real"""
        self._any = self._real = None


class PlatformFactory(AbstractFactory):
    """Checks and Returns data about current platform"""

    def __init__(self):
        super(PlatformFactory, self).__init__()

    def _candidates(self):
        """Peek a list of valid platforms sorted by priority"""
        platforms = self.backends.itervalues()
        candidates = [backend for backend in platforms if backend.match()]
        return sorted(candidates, key=attrgetter('priority'))

    def __iter__(self):
        return iter(self._candidates())


class MetaPlatform(type):
    """Platform register metaclass"""

    def __init__(mcs, name, bases, dct):
        type.__init__(mcs, name, bases, dct)
        factory = PlatformFactory.get_instance()
        factory.register(name, mcs)
        #factory.clear()


class Desktop(PlatformBase):
    """Base class for command objects"""

    __metaclass__ = MetaPlatform

    def __init__(self):
        priority = 1000000
        ptfnames = ("DESKTOP", "desktop", "Desktop",)
        super(Desktop, self).__init__(priority, ptfnames)


class Fremantle(PlatformBase):
    """A Base class for Maemo 5 instances"""

    __metaclass__ = MetaPlatform

    def __init__(self):
        priority = 0
        ptfnames = ("Fremantle", "Fremantle", "fremantle",)
        super(Fremantle, self).__init__(priority, ptfnames)

    #pylint: disable-msg=W0703
    @classmethod
    def match(cls):
        try:
            with open('/etc/issue') as issue:
                if ('Maemo 5' in issue.read()):
                    return True
                return False
        except Exception:
            pass
        try:
            #pylint: disable-msg=E0611
            from hashlib import sha1
            with open('/etc/issue') as issue:
                sha = sha1(issue.read()).hexdigest()
                return sha == 'a8594416e0452316ea87a7f9395bc7cc4b0228a4'
        except Exception:
            return False
