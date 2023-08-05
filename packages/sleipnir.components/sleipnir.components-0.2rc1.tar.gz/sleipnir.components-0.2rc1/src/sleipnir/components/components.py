#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-


"""Component base classes from pluggins"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import Here any required modules for this module.

__all__ = ['Component', 'implements']


#pylint: disable-msg=R0903
class AbstractComponent(object):
    """
    AbstractBase class for components

    Every component can declare what extension points it provides, as
    well as what extension points of other components it extends
    """

    @staticmethod
    def implements(*interfaces):
        """
        Can be used in the class definition of `Component` subclasses
        to declare the extension points that are extended
        """
        import sys

        #pylint: disable-msg=W0212
        frame = sys._getframe(1)
        locals_ = frame.f_locals

        # Some sanity checks
        assert locals_ is not frame.f_globals and '__module__' in locals_, \
               'implements() can only be used in a class definition'

        locals_.setdefault('_implements', []).extend(interfaces)

    @classmethod
    def query(cls, query_iface):
        """
        Return True if interface is implemented by this component
        """
        ifaces = []
        for cls in cls.__mro__:
            found = (i.__name__ for i in cls.__dict__.get('_implements', ()))
            ifaces.extend(found)
        return query_iface in ifaces


#pylint: disable-msg=C0103
implements = AbstractComponent.implements


#pylint: disable-msg=R0903
class Component(AbstractComponent):
    """Main component"""

    from .metaclass import ComponentMeta
    __metaclass__ = ComponentMeta
