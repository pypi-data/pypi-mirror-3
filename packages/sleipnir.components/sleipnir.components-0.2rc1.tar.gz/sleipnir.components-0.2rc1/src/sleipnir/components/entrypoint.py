#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Conectors for Sleipnir component system

As TRAC Sleipnir defines interfaces and entrypoints where Interfaces
are parts of a contract to be implemented by components, and
entrypoints and slots where components's functionality could be
extended.
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__status__  = "alpha"
__version__ = "0.1"
__date__    = "21 January 2010"
__license__ = "See TRAC project for details"

# Import Here any required modules for this module.

__all__ = ['ExtensionPoint', 'Interface']


class Interface(object):
    """Marker base class for extension point interfaces"""


class ExtensionPoint(property):
    """Marker class for extension points in components"""

    def __init__(self, interface, ifilter=lambda x: True):
        """
        Create the extension point

        Keyword arguments:
        interface -- the `Interface` subclass that defines the
            protocol for the extension point
        ifilter -- a callable applied to all components to check if
        satisfies callable condition

        """

        property.__init__(self, self.extensions)
        self.interface = interface
        self.ifilter = ifilter
        self.__doc__ = ("List of components that implement `%s`" %
                        self.interface.__name__)

    def extensions(self, component):
        """
        Return a list of components that declare to implement the
        extension point interface
        """

        from .metaclass import ComponentMeta
        classes = ComponentMeta.get_cls(self.interface)
        components = [component.compmgr[cls] for cls in classes]
        return [c for c in components if self.ifilter(c)]

    def __repr__(self):
        """Return a textual representation of the extension point"""

        return '<ExtensionPoint %s>' % self.interface.__name__
