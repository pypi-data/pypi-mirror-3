#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

# Copyright (C)2005-2009 Edgewall Software
# Copyright (C) 2005 Christopher Lenz <cmlenz@gmx.de>
# All rights reserved.

"""Test classes for sleipnir.core.components"""

__author__  = "Christopher Lenz <cmlenz@gmx.de>"
__license__ = "See http://trac.edgewall.org/wiki/TracLicense for details"

# Import here required modules
import os
import sys

from sleipnir.testing.test import TestCase, create_suite, run_suite

__all__ = ['TestMetaClass', 'TestComponent', 'TestLoaderManager']

from sleipnir.components.exceptions import CoreError
from sleipnir.components.components import Component, implements
from sleipnir.components.entrypoint import Interface, ExtensionPoint


#pylint: disable-msg=R0923
class ITest(Interface):
    """Dummy ITest"""
    def test(self):
        """Dummy function"""


class IOtherTest(Interface):
    """Dummy IOhterTest"""
    def other_test(self):
        """Other dummy function"""


#pylint: disable-msg=R0903,R0904,C0103
class TestCaseComponent(TestCase):
    """Base class for this TestSuite"""

    #pylint: disable-msg=C0103,W0212
    def setUp(self):
        from sleipnir.components.manager import ComponentManager
        from sleipnir.components.metaclass import ComponentMeta
        self.compmgr = ComponentManager()

        # Make sure we have no external components hanging around in the
        # component registry
        self.old_registry = ComponentMeta._registry
        ComponentMeta._registry = {}

    def tearDown(self):
        # Restore the original component registry
        from sleipnir.components.metaclass import ComponentMeta
        ComponentMeta._registry = self.old_registry


class TestMetaClass(TestCaseComponent):
    """Test Case to check metaclass behaviour"""

    def test_base_class_not_registered(self):
        """
        Make sure that the Component base class does not appear in the
        component registry
        """
        from sleipnir.components.metaclass import ComponentMeta
        assert not ComponentMeta.registered(Component)
        self.assertRaises(CoreError, self.compmgr.__getitem__, Component)

    def test_abstract_not_registered(self):
        """
        Make sure that a Component class marked as abstract does not
        appear in the component registry
        """
        from sleipnir.components.metaclass import ComponentMeta

        class AbstractComponent(Component):
            """Dummy Abstract Component"""
            abstract = True

        assert not ComponentMeta.registered(AbstractComponent)
        self.assertRaises(CoreError, self.compmgr.__getitem__,
                          AbstractComponent)


class TestComponent(TestCaseComponent):
    """Main TestCase. Check for component behaviour"""

    def test_component_registration(self):
        """
        Verify that classes derived from `Component` are managed by the
        component manager.
        """
        class ComponentA(Component):
            """Dummy Component"""

        assert self.compmgr[ComponentA]
        assert ComponentA(self.compmgr)

    def test_component_identity(self):
        """
        Make sure instantiating a component multiple times just returns the
        same instance again.
        """
        class ComponentA(Component):
            """Dummy Component"""

        inst1 = ComponentA(self.compmgr)
        inst2 = ComponentA(self.compmgr)
        assert inst1 is inst2, 'Expected same component instance'
        inst2 = self.compmgr[ComponentA]
        assert inst1 is inst2, 'Expected same component instance'

    def test_component_initializer(self):
        """
        Makes sure that a components' `__init__` method gets called.
        """
        class ComponentA(Component):
            """Dummy Component"""

            def __init__(self):
                super(ComponentA, self).__init__()
                self.data = 'test'

        self.assertEqual('test', ComponentA(self.compmgr).data)
        ComponentA(self.compmgr).data = 'newtest'
        self.assertEqual('newtest', ComponentA(self.compmgr).data)

    def test_inherited_component_init(self):
        """
        Makes sure that a the `__init__` method of a components' super-class
        gets called if the component doesn't override it.
        """
        class ComponentA(Component):
            """Dummy Component"""

            def __init__(self):
                super(ComponentA, self).__init__()
                self.data = 'test1'

        class ComponentB(ComponentA):
            """Dummy Component"""

            def __init__(self):
                super(ComponentA, self).__init__()
                self.data = 'test2'

        class ComponentC(ComponentB):
            """Dummy Component"""

        self.assertEqual('test2', ComponentC(self.compmgr).data)
        ComponentC(self.compmgr).data = 'baz'
        self.assertEqual('baz', ComponentC(self.compmgr).data)

    def test_implements_called_outside_classdef(self):
        """
        Verify that calling implements() outside a class definition raises an
        `AssertionError`.
        """
        try:
            implements()
        except AssertionError:
            pass
        else:
            self.fail('Expected AssertionError')

    def test_implements_multiple(self):
        """
        Verify that a component "implementing" an interface more than once
        (e.g. through inheritance) is not called more than once from an
        extension point.
        """
        log = []

        class Parent(Component):
            """Dummy Component"""
            abstract = True
            implements(ITest)

        #pylint:disable-msg=W0612
        class Child(Parent):
            """Dummy Component"""
            implements(ITest)

            #pylint: disable-msg=R0201
            def test(self):
                """Dummy method"""
                log.append("call")

        class Other(Component):
            """Dummy Component"""
            tests = ExtensionPoint(ITest)
        for test in Other(self.compmgr).tests:
            test.test()
        self.assertEqual(["call"], log)

    def test_attribute_access(self):
        """
        Verify that accessing undefined attributes on components raises an
        `AttributeError`.
        """
        class ComponentA(Component):
            """Dummy Component"""

        comp = ComponentA(self.compmgr)
        try:
            #pylint:disable-msg=W0104,E1101
            comp.test1
            self.fail('Expected AttributeError')
        except AttributeError:
            pass

    def test_nonconforming_extender(self):
        """
        Verify that accessing a method of a declared extension point interface
        raises a normal `AttributeError` if the component does not implement
        the method.
        """
        class ComponentA(Component):
            """Dummy Component"""
            tests = ExtensionPoint(ITest)

        #pylint:disable-msg=W0612
        class ComponentB(Component):
            """Dummy Component"""
            implements(ITest)
        tests = iter(ComponentA(self.compmgr).tests)
        try:
            tests.next().test()
            self.fail('Expected AttributeError')
        except AttributeError:
            pass

    def test_extension_point_with_no_extension(self):
        """
        Verify that accessing an extension point with no extenders returns an
        empty list.
        """
        class ComponentA(Component):
            """Dummy Component"""
            tests = ExtensionPoint(ITest)
        tests = iter(ComponentA(self.compmgr).tests)
        self.assertRaises(StopIteration, tests.next)

    def test_extension_point_with_one_extension(self):
        """
        Verify that a single component extending an extension point can be
        accessed through the extension point attribute of the declaring
        component.
        """
        class ComponentA(Component):
            """Dummy Component"""
            tests = ExtensionPoint(ITest)

        #pylint:disable-msg=W0612
        class ComponentB(Component):
            """Dummy Component"""
            implements(ITest)

            #pylint:disable-msg=R0201
            def test(self):
                """Dummy method"""
                return 'x'
        tests = iter(ComponentA(self.compmgr).tests)
        self.assertEquals('x', tests.next().test())
        self.assertRaises(StopIteration, tests.next)

    def test_extension_point_with_two_extensions(self):
        """
        Verify that two components extending an extension point can be accessed
        through the extension point attribute of the declaring component.
        """
        class ComponentA(Component):
            """Dummy Component"""
            tests = ExtensionPoint(ITest)

        #pylint: disable-msg=W0612
        class ComponentB(Component):
            """Dummy Component"""
            implements(ITest)

            #pylint: disable-msg=R0201
            def test(self):
                """Dummy method"""
                return 'x'

        class ComponentC(Component):
            """Dummy Component"""
            implements(ITest)

            #pylint: disable-msg=R0201
            def test(self):
                """Dummy method"""
                return 'y'
        results = [test.test() for test in ComponentA(self.compmgr).tests]
        self.assertEquals(['x', 'y'], sorted(results))

    def test_inherited_extension_point(self):
        """
        Verify that extension points are inherited to sub-classes.
        """
        class BaseComponent(Component):
            """Dummy Component"""
            tests = ExtensionPoint(ITest)

        class ConcreteComponent(BaseComponent):
            """Dummy Component"""

        #pylint: disable-msg=W0612
        class ExtendingComponent(Component):
            """Dummy Component"""
            implements(ITest)

            #pylint: disable-msg=R0201
            def test(self):
                """Dummy method"""
                return 'x'
        tests = iter(ConcreteComponent(self.compmgr).tests)
        self.assertEquals('x', tests.next().test())
        self.assertRaises(StopIteration, tests.next)

    #pylint: disable-msg=R0201
    def test_inherited_implements(self):
        """
        Verify that a component with a super-class implementing an extension
        point interface is also registered as implementing that interface.
        """
        class BaseComponent(Component):
            """Dummy Component"""
            implements(ITest)
            abstract = True

        class ConcreteComponent(BaseComponent):
            """Dummy Component"""

        from sleipnir.components.metaclass import ComponentMeta
        assert ConcreteComponent in ComponentMeta.get_cls(ITest)

    def test_inherited_implements_multilevel(self):
        """
        Verify that extension point interfaces are inherited for more than
        one level of inheritance.
        """
        class BaseComponent(Component):
            """Dummy Component"""
            implements(ITest)
            abstract = True

        class ChildComponent(BaseComponent):
            """Dummy Component"""
            implements(IOtherTest)
            abstract = True

        class ConcreteComponent(ChildComponent):
            """Dummy Component"""

        from sleipnir.components.metaclass import ComponentMeta
        assert ConcreteComponent in ComponentMeta.get_cls(ITest)
        assert ConcreteComponent in ComponentMeta.get_cls(IOtherTest)


class TestComponentManager(TestCaseComponent):
    """Verify behaviour of ComponentManager instances"""

    def test_unregistered_component(self):
        """
        Make sure the component manager refuses to manage classes not derived
        from `Component`.
        """
        class NoComponent(object):
            """Dummy Component"""

        self.assertRaises(CoreError, self.compmgr.__getitem__, NoComponent)

    def test_component_manager_component(self):
        """
        Verify that a component manager can itself be a component with its own
        extension points.
        """
        from sleipnir.components.manager import ComponentManager

        class ManagerComponent(ComponentManager, Component):
            """Dummy Component"""
            tests = ExtensionPoint(ITest, lambda x: x)

            def __init__(self, test1, test2):
                super(ManagerComponent, self).__init__()
                self.test1, self.test2 = test1, test2

        #pylint: disable-msg=W0612
        class Extender(Component):
            """Dummy Component"""
            implements(ITest)

            #pylint: disable-msg=R0201
            def test(self):
                """Dummy method"""
                return 'x'

        mgr = ManagerComponent('Test', 42)
        assert id(mgr) == id(mgr[ManagerComponent])
        assert ManagerComponent in mgr

        tests = iter(mgr.tests)
        self.assertEqual('x', tests.next().test())
        self.assertRaises(StopIteration, tests.next)

    def test_instantiation_doesnt_enable(self):
        """
        Make sure that a component disabled by the ComponentManager is not
        implicitly enabled by instantiating it directly.
        """
        from sleipnir.components.manager import ComponentManager

        class DisablingComponentManager(ComponentManager):
            """Dummy Component"""

            def is_component_enabled(self, cls):
                """Dummy method"""
                return False

        class ComponentA(Component):
            """Dummy Component"""

        mgr = DisablingComponentManager()
        ComponentA(mgr)
        self.assertEqual(None, mgr[ComponentA])
        assert ComponentA in mgr
        self.assertEqual(None, mgr[DisablingComponentManager])
        assert DisablingComponentManager not in mgr

    def test_disable_and_make_private_components(self):
        """
        Check that a component disabled doesn't appear in a ComponentManager
        """
        from sleipnir.components.manager import ComponentManager

        class ComponentA(Component):
            """Dummy Component"""

        # Check that component private is in Manager
        mgr = ComponentManager()
        private = ComponentA(mgr)
        self.assertEqual(private, mgr[ComponentA])
        assert ComponentA in mgr

        # now make component private
        mgr.make_private(private)
        assert private not in mgr
        # pylint: disable-msg=E1101
        assert private in private.compmgr
        self.assertNotEqual(id(private), id(mgr[ComponentA]))
        self.assertNotEqual(None, mgr[ComponentA])

        # create a new component
        instance = ComponentA(mgr)
        assert ComponentA in mgr
        self.assertEqual(instance, mgr[ComponentA])
        self.assertNotEqual(id(instance), id(private))

        # now disable component
        mgr.disable_component(instance)
        assert ComponentA in mgr
        self.assertEqual(None, mgr[ComponentA])
        assert not mgr.is_enabled(ComponentA)


main_suite = create_suite([TestMetaClass, TestComponent, TestComponentManager])

if __name__ == '__main__':
    #pylint: disable-msg=E1120
    run_suite()
