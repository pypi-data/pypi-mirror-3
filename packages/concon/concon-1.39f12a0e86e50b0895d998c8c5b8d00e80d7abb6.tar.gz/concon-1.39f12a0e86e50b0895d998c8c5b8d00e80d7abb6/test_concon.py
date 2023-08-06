#! /usr/bin/env python

import unittest

# Note, we do not test frozenset.

from concon import ConstraintError, OverwriteError
from concon import frozendict, frozenlist
from concon import appendonlydict, appendonlylist, appendonlyset
from concon import setitem_without_overwrite, update_without_overwrite


class SetItemWithoutOverwriteTests (unittest.TestCase):

    def test__setitem_without_overwrite__no_overwrite(self):
        d = {'a': 'apple'}
        setitem_without_overwrite(d, 'b', 'banana')
        self.assertEqual(d, {'a': 'apple', 'b': 'banana'})

    def test__setitem_without_overwrite__with_overwrite(self):
        d = {'a': 'apple'}
        try:
            setitem_without_overwrite(d, 'a', 'applause')
        except OverwriteError, e:
            self.assertEqual(e.args, ('a', 'applause', 'apple'))
            self.assertEqual(
                str(e),
                "Attempted overwrite of key 'a' with new value 'applause' overwriting old value 'apple'")
        else:
            self.fail('setitem_without_overwrite allowed overwrite: %r' % (d,))

    def test__update_without_overwrite__no_overwrite(self):
        d = {'a': 'apple'}
        update_without_overwrite(d, {'b': 'banana'})
        self.assertEqual(d, {'a': 'apple', 'b': 'banana'})

    def test__update_without_overwrite__with_overwrite(self):
        d = {'a': 'apple'}
        try:
            update_without_overwrite(d, {'a': 'applause'})
        except OverwriteError, e:
            self.assertEqual(e.args, ('a', 'applause', 'apple'))
            self.assertEqual(
                str(e),
                "Attempted overwrite of key 'a' with new value 'applause' overwriting old value 'apple'")
        else:
            self.fail('update_without_overwrite allowed overwrite: %r' % (d,))

    def test__update_without_overwrite__with_NonMappingWithKeysAndGetItem(self):
        class NonMappingWithKeysAndGetItem (object):
            def keys(self):
                return ['a', 'b', 'c']
            def __getitem__(self, key):
                return 42

        d = {}
        update_without_overwrite(d, NonMappingWithKeysAndGetItem())
        self.assertEqual(d, {'a': 42, 'b': 42, 'c': 42})

    def test__update_without_overwrite__with_keyvalue_sequence(self):
        d = {}
        update_without_overwrite(d, [('a', 0), ('b', 1), ('c', 2)])
        self.assertEqual(d, {'a': 0, 'b': 1, 'c': 2})

    def test__update_without_overwrite__with_keywords(self):
        d = {}
        update_without_overwrite(d, a=0, b=1, c=2)
        self.assertEqual(d, {'a': 0, 'b': 1, 'c': 2})


class BlockedMethodsTests (unittest.TestCase):

    def test_frozendict(self):
        self._check_blocked_methods(frozendict({}))

    def test_frozenlist(self):
        self._check_blocked_methods(frozenlist({}))

    # Note, we do not test frozenset.

    def test_appendonlydict(self):
        self._check_blocked_methods(appendonlydict({}))

    def test_appendonlylist(self):
        self._check_blocked_methods(appendonlylist({}))

    def test_appendonlyset(self):
        self._check_blocked_methods(appendonlyset({}))

    def _check_blocked_methods(self, obj):
        for name in obj.get_blocked_method_names():
            method = getattr(obj, name)
            try:
                r = method(42)
            except ConstraintError, e:
                self.assertEqual(e.args, (obj, name, (42,), {}))
                self.assertEqual(
                    str(e),
                    "Attempt to call %r.%s (42,) {} violates constraint." % (obj, name))
            else:
                self.fail('Blocked method %r.%s returned %r' % (obj, name, r))



if __name__ == '__main__':
    unittest.main()
