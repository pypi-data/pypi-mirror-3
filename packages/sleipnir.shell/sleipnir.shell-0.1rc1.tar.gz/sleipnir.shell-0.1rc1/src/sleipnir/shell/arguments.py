#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Arguments

A Custom argument parser for sleipnir
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules
import sys
from itertools import ifilter
from optparse import OptionParser

__all__ = ['Options']

# Project requirements
from sleipnir.core.singleton import Singleton

# local submodule requirements


#pylint: disable-msg=R0921
class Options(Singleton):
    """
    A custom argument parser container that allow for hierachy child
    arguments
    """

    abstract = True

    def __init__(self, argv=sys.argv):
        self._parser = Parser(root=self)
        self._values = {}
        self._args = argv or []
        self._remain_args = []

    def __iter__(self):
        return iter(self._parser)

    def __getattr__(self, value):
        # try an option
        if value in self._values:
            return self._values[value]

        # if not, try a parser method
        if hasattr(self._parser, value):
            return getattr(self._parser, value)

        # not found? raise esception
        raise AttributeError(value)

    @property
    def options(self):
        """Get current available values"""
        return self._values

    @property
    def args(self):
        """Get arguments to be parsed"""
        return self._args

    @property
    def remain_args(self):
        """Leftover arguments after a call to parse"""
        return self._remain_args

    def parse(self, argv=None, parser=None, recursive=0):
        """Parse command line"""
        parser = self.children.get(parser, self._parser)
        _, argv = parser.parse_arguments(argv or self._args)
        remain = parser.children.values()
        while (recursive != 0 and len(remain) > 0):
            children = []
            recursive -= 1
            for child in remain:
                _, argv = child.parse_arguments(argv)
                children.extend(child.children.itervalues())
            remain = children
            print remain
        self._remain_args = argv

    def find(self, name):
        """Lookup for name into args"""
        raise NotImplementedError

    def find_by_option(self, option):
        """Lookup for option in args"""
        raise NotImplementedError


#pylint: disable-msg=R0904
class Parser(OptionParser):
    """Custom Parser"""

    SHORT, LONG, DEF, HELP, ACTION, DES, RECURSIVE = xrange(7)

    def __init__(self, root):
        OptionParser.__init__(self, add_help_option=False)
        self._root = root
        self._children = {}
        self._recursive_options = []

    @property
    def children(self):
        """Get associated parsers"""
        return self._children

    def add_options(self, opt_table):
        """Parse and aggregate contents of option table"""

        # sugar to add opt table
        for opt in opt_table:
            self.add_option(
                opt[self.SHORT], opt[self.LONG], action=opt[self.ACTION],
                help=opt[self.HELP], dest=opt[self.DES], default=opt[self.DEF])

        ffilter = lambda x: len(x) > self.RECURSIVE and x[self.RECURSIVE]
        for opt in ifilter(ffilter, opt_table):
            self._recursive_options.append(opt)
            for child in self._children.itervalues():
                child.add_options([opt])

    def add_child_options(self, name, opt_table):
        """Add opt table to child named. If not exists, create one"""
        add_recursive_options = name in self._children
        parser = self._children.setdefault(name, Parser(root=self._root))
        if add_recursive_options:
            parser.add_options(self._recursive_options)
        parser.add_options(opt_table)
        return parser

    def parse_arguments(self, argv):
        """validate arguments and estract options from argv"""

        # validate entry
        main, fargv = [argv[0]], [argv[0]]
        for pos, arg in enumerate(argv[1:]):
            if arg[0] != '-':
                fargv.extend(argv[pos + 1:])
                break
            main.append(arg)
        options, _ = self.parse_args(main)
        self._root.options.update(vars(options))
        return main, fargv
