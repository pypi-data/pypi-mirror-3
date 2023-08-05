#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""Test classes for sleipnir.core.components.loaders"""

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here required modules
import os
import sys

from sleipnir.testing.test import TestCase, create_suite, run_suite
from sleipnir.testing.data import DATA

__all__ = ['TestLoaders', 'TestLoaderManager']

from sleipnir.components import loaders


#pylint:disable-msg=R0904
class Loader(TestCase):
    """Abtract class to derive all Test classes from"""

    #pylint: disable-msg=W0212,C0103
    def setUp(self):
        from sleipnir.components.manager import ComponentManager
        self.compmgr = ComponentManager()

    def __len__(self):
        from sleipnir.components.metaclass import ComponentMeta
        return len(ComponentMeta._registry)


class TestLoaders(Loader):
    """TestCase for Loaders existence"""

    def test_egg_loader_backend(self):
        """check that egg loader is up and running"""
        from sleipnir.components.metaclass import ComponentMeta
        assert ComponentMeta.registered(loaders.EggsLoader)

    def test_python_loader_backend(self):
        """check that python loader is up and running"""
        from sleipnir.components.metaclass import ComponentMeta
        assert ComponentMeta.registered(loaders.PyLoader)


class TestLoaderManager(Loader):
    """TestCase for LoaderManager"""

    #pylint: disable-msg=W0212,C0103
    def setUp(self):
        from sleipnir.components.metaclass import ComponentMeta
        # Make sure we have no external components hanging around in the
        # component registry
        self.old_registry = ComponentMeta._registry
        super(TestLoaderManager, self).setUp()

    def tearDown(self):
        # Restore the original component registry
        from sleipnir.components.metaclass import ComponentMeta
        ComponentMeta._registry = self.old_registry

    def test_manager_registered(self):
        """verify LoaderManager is up and running"""
        from sleipnir.components.metaclass import ComponentMeta
        assert ComponentMeta.registered(loaders.LoaderManager)
        assert ComponentMeta.registered(loaders.EggsLoader)
        assert ComponentMeta.registered(loaders.PyLoader)
        assert len(self) == 3

    def test_load_valid_eggs(self):
        """check that Egg plugin is registered"""
        old_len = len(self)
        loaders.LoaderManager(self.compmgr).load(DATA.PLUGIN_DIRS[0])
        assert len(self) == old_len + 1

    def test_load_valid_py(self):
        """check that Python plugin is registered"""
        old_len = len(self)
        loaders.LoaderManager(self.compmgr).load(DATA.PLUGIN_DIRS[1])
        assert len(self) == old_len + 1


#pylint: disable-msg=C0103
main_suite = create_suite([TestLoaderManager, TestLoaders])

if __name__ == '__main__':
    #pylint: disable-msg=E1120
    run_suite()
