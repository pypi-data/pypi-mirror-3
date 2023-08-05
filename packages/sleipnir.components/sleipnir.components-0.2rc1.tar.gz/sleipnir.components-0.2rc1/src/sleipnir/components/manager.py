#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Component Manager for Sleipnir

Keeps a pool of active components
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import Here any required modules for this module.

__all__ = ['ComponentManager']

#pylint: disable-msg=E0611
from .exceptions import CoreError
from .metaclass  import ComponentMeta
from .components import AbstractComponent


class ComponentManager(object):
    """The component manager keeps a pool of active components"""

    def __init__(self):
        """Initialize the component manager"""

        self.components = {}
        self.enabled = {}
        if isinstance(self, AbstractComponent):
            self.components[self.__class__] = self

    def __contains__(self, component):
        """
        Return wether the given class is in the list of active
        components
        """

        if isinstance(component, type):
            return component in self.components
        else:
            cls = component.__class__
            return cls in self.components and \
                id(self.components[cls]) == id(component)

    def __getitem__(self, cls):
        """
        Activate the component instance for the given class, or return
        the existing instance if the component has already been
        activated
        """
        if not self.is_enabled(cls):
            return None
        component = self.components.get(cls)
        if not component:
            if not ComponentMeta.registered(cls):
                raise CoreError(
                    'Component "%s" not registered' % cls.__name__)
            try:
                is_manager = issubclass(cls, ComponentManager)
                component = cls() if is_manager else cls(self)
            except TypeError, ex:
                raise CoreError(
                    'Instantiate component %r fail. (%s)' % (cls, ex))

        return component

    def is_enabled(self, cls):
        """Return whether the given component class is enabled"""

        if cls not in self.enabled:
            self.enabled[cls] = self.is_component_enabled(cls)
        return self.enabled[cls]

    def make_private(self, component, new_compmgr=None):
        """
        Make component instance private

        Keyword arguments:
        new_compmgr -- A new ComponentManager for 'component'

        """

        cls = component.__class__
        current = self.components.get(cls, None)

        # If registered, update component manager and remove
        if id(current) == id(component):
            self.components[cls] = None
            component.compmgr = new_compmgr or self.__class__()
            component.compmgr.components[cls] = component

    def disable_component(self, component):
        """
        Force a component to be disabled

        Keyword arguments:
        component -- can be a class or an instance

        """

        if not isinstance(component, type):
            component = component.__class__

        # remove from compmgr
        self.enabled[component] = False
        self.components[component] = None

    def component_activated(self, component):
        """
        Can be overridden by sub-classes so that special
        initialization for components can be provided
        """

    #pylint: disable-msg=W0613,R0201
    def is_component_enabled(self, cls):
        """
        Can be overridden by sub-classes to veto the activation of a
        component

        If this method returns `False`, the component was disabled
        explicitly.  If it returns `None`, the component was neither
        enabled nor disabled explicitly. In both cases, the component
        with the given class will not be available
        """

        return True

    @staticmethod
    def available(interface):
        return ComponentMeta.get_cls(interface)
