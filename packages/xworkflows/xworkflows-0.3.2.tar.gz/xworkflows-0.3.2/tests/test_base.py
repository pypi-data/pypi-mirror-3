#!/usr/bin/env python
# coding: utf-8

import unittest2

from xworkflows import base


class StateTestCase(unittest2.TestCase):

    def test_definition(self):
        self.assertRaises(ValueError, base.State, 'a--b', 'A--B')

    def test_equality(self):
        self.assertNotEqual(base.State('foo', 'Foo'), base.State('foo', 'Foo'))

    def test_repr(self):
        a = base.State('foo', 'Foo')
        self.assertIn('foo', repr(a))
        self.assertNotIn('Foo', repr(a))


class StateListTestCase(unittest2.TestCase):

    def setUp(self):
        self.foo = base.State('foo', 'Foo')
        self.bar = base.State('bar', 'Bar')
        self.bar2 = base.State('bar', 'Bar')
        self.sl = base.StateList([self.foo, self.bar])

    def test_access(self):
        self.assertEqual(self.foo, self.sl.foo)
        self.assertEqual(self.foo, self.sl['foo'])

        self.assertFalse(hasattr(self.sl, 'baz'))

    def test_contains(self):
        self.assertIn(self.foo, self.sl)
        self.assertIn(self.bar, self.sl)

        self.assertNotIn(self.bar2, self.sl)

    def test_list_methods(self):
        self.assertTrue(self.sl)
        self.assertFalse(base.StateList([]))

        self.assertEqual(2, len(self.sl))


class TransitionListTestCase(unittest2.TestCase):

    def setUp(self):
        self.foo = base.State('foo', 'Foo')
        self.bar = base.State('bar', 'Bar')
        self.baz = base.State('baz', 'Baz')
        self.baz2 = base.State('baz', 'Baz')
        self.foobar = base.Transition('foobar', self.foo, self.bar)
        self.foobar2 = base.Transition('foobar', self.foo, self.bar)
        self.gobaz = base.Transition('gobaz', [self.foo, self.bar], self.baz)
        self.tl = base.TransitionList([self.foobar, self.gobaz])

    def test_access(self):
        self.assertEqual(self.foobar, self.tl.foobar)
        self.assertEqual(self.foobar, self.tl['foobar'])

        self.assertFalse(hasattr(self.tl, 'foobaz'))

    def test_contains(self):
        self.assertIn(self.foobar, self.tl)
        self.assertIn(self.gobaz, self.tl)

        self.assertNotIn(self.foobar2, self.tl)

    def test_list_methods(self):
        self.assertTrue(self.tl)
        self.assertFalse(base.TransitionList([]))

        self.assertEqual(2, len(self.tl))

    def test_available(self):
        self.assertItemsEqual([self.foobar, self.gobaz],
                              list(self.tl.available_from(self.foo)))
        self.assertItemsEqual([self.gobaz],
                              list(self.tl.available_from(self.bar)))
        self.assertEqual([], list(self.tl.available_from(self.baz)))


class StateWrapperTestCase(unittest2.TestCase):

    def setUp(self):
        class MyWorkflow(base.Workflow):
            states = (
                ('foo', "Foo"),
                ('bar', "Bar"),
                ('baz', "Baz"),
            )
            transitions = (
                ('foobar', 'foo', 'bar'),
                ('gobaz', ('foo', 'bar'), 'baz'),
                ('bazbar', 'baz', 'bar'),
            )
            initial_state = 'foo'

        self.foo = base.State('foo', 'Foo')
        self.bar = base.State('bar', 'Bar')
        self.wf = MyWorkflow
        self.sf = base.StateWrapper(self.foo, self.wf)

    def test_comparison(self):
        self.assertEqual(self.sf, self.foo)
        self.assertEqual(self.foo, self.sf)
        self.assertNotEqual(self.sf, self.bar)
        self.assertNotEqual(self.bar, self.sf)
        self.assertEqual(self.sf, 'foo')
        self.assertEqual('foo', self.sf)

    def test_attributes(self):
        self.assertTrue(self.sf.is_foo)
        self.assertFalse(self.sf.is_bar)
        self.assertFalse(hasattr(self.sf, 'foo'))
        self.assertEqual(self.foo.name, self.sf.name)
        self.assertEqual(self.foo.title, self.sf.title)


class ImplementationPropertyTestCase(unittest2.TestCase):

    def setUp(self):
        self.foo = base.State('foo', 'Foo')
        self.bar = base.State('bar', 'Bar')
        self.baz = base.State('baz', 'Baz')
        self.foobar = base.Transition('foobar', self.foo, self.bar)

    def test_creation(self):
        def blah(obj):
            """doc for blah"""
            pass

        implem = base.ImplementationProperty(
            field_name='my_state', transition=self.foobar, workflow=None,
            implementation=blah)

        self.assertIn("'foobar'", repr(implem))
        self.assertIn("blah", repr(implem))
        self.assertIn('my_state', repr(implem))
        self.assertEqual('doc for blah', implem.__doc__)

    def test_using(self):
        def blah(obj):
            pass

        class MyClass(object):
            state = self.foo

        implem = base.ImplementationProperty(
            field_name='my_state', transition=self.foobar, workflow=None,
            implementation=blah)


        MyClass.foobar = implem

        self.assertEqual(implem, MyClass.foobar)

        o = MyClass()

        self.assertRaises(TypeError, getattr, o, 'foobar')


class TransitionWrapperTestCase(unittest2.TestCase):

    def setUp(self):
        self.wrapper = base.TransitionWrapper('foobar')

    def test_txt(self):
        self.assertIn('foobar', repr(self.wrapper))


if __name__ == '__main__':
    unittest2.main()
