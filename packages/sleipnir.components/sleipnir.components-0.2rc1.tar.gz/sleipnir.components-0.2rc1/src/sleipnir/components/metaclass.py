#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""Metaclass for Components"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__status__  = "alpha"
__version__ = "0.1"
__date__    = "25 January 2010"
__license__ = "See LICENSE file for details"

# Import Here any required modules for this module.

__all__ = ['ComponentMeta']

#pylint: disable-msg=E0611
try:
    from sleipnir.core.log import log
except ImportError:
    from ._log import dummy as log


class ComponentMeta(type):
    """
    Metaclass used by Component class

    Take care of component and extension point registration for
    Stateful Components
    """

    _registry = {}
    _components = []

    def __new__(mcs, name, bases, dct):
        """Create the component class."""
        new_class = type.__new__(mcs, name, bases, dct)
        # Don't put the Component base class in the registry
        # Don't put abstract component classes in the registry
        if name not in ('Component', ) and 'abstract' not in dct:
            ComponentMeta.__register_component__(new_class)
        return new_class

    def __register_component__(new_class):
        """ Register new_class into component system"""
        ComponentMeta._components.append(new_class)
        if __debug__:
            class_api = set(dir(new_class))
        for cls in new_class.__mro__:
            for interface in cls.__dict__.get('_implements', ()):
                if __debug__:
                    # Check Component implements interfaces
                    iface_api = set(dir(interface))
                    if not iface_api.issubset(class_api):
                        log.components.debug(
                            "Missing methods from %s for %s : %r" %
                            (interface.__name__, cls.__name__, \
                             list(iface_api - class_api)))

                classes = ComponentMeta._registry.setdefault(interface, [])
                if new_class not in classes:
                    classes.append(new_class)

    def __call__(mcs, *args, **kwargs):
        """
        Return an existing instance of the component if it has already
        been activated, otherwise create a new instance.
        """

        from .manager import ComponentManager
        # If this component is also the component manager, just invoke that
        if issubclass(mcs, ComponentManager):
            self = mcs.__new__(mcs)
            self.compmgr = self
            self.__init__(*args, **kwargs)
            return self

        # The normal case where the component is not also the component manager
        compmgr = args[0]
        self = compmgr.components.get(mcs)

        # Note that this check is racy, we intentionally don't use a
        # lock in order to keep things simple and avoid the risk of
        # deadlocks, as the impact of having temporarily two (or more)
        # instances for a given `cls` is negligible.
        if self is None:
            self = mcs.__new__(mcs)
            self.compmgr = compmgr
            compmgr.component_activated(self)
            self.__init__()
            # Only register the instance once it is fully initialized (#9418)
            compmgr.components[mcs] = self
        return self

    @classmethod
    def registered(cls, value):
        """Check in class is registered yet"""

        return value in cls._components

    @classmethod
    def get_cls(cls, interface):
        """Get a copy of valid class registered"""
        if type(interface) not in (str, unicode,):
            classes = cls._registry.get(interface, [])
            return classes[:]
        for key, value in cls._registry.iteritems():
            if key.__name__ == interface:
                return value[:]
