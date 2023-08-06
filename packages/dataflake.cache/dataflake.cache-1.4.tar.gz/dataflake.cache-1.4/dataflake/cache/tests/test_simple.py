##############################################################################
#
# Copyright (c) 2009-2012 Jens Vagelpohl and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Tests for the Simple cache class

$Id$
"""

import unittest

from dataflake.cache.tests.base import CacheTestCase

try:
    unicode
except NameError: #pragma NO COVER Python3
    unicode = str #pragma NO COVER Python3

       
class TestSimpleCache(CacheTestCase):

    def _getTargetClass(self):
        from dataflake.cache.simple import SimpleCache
        return SimpleCache

    def test_conformance(self):
        from dataflake.cache.interfaces import ICache
        from zope.interface.verify import verifyClass
        verifyClass(ICache, self._getTargetClass())

    def test_initial_state(self):
        self.assertFalse(list(self.cache.keys()))
        self.assertFalse(list(self.cache.values()))
        self.assertFalse(list(self.cache.items()))

    def test_get_set_clear(self):
        self.assertFalse(list(self.cache.keys()))
        self.assertFalse(list(self.cache.values()))
        self.assertFalse(list(self.cache.items()))

        self.cache.set('key1', 'value1')
        self.assertEqual(list(self.cache.keys()), ['key1'])
        self.assertEqual(list(self.cache.values()), ['value1'])
        self.assertEqual(list(self.cache.items()), [('key1', 'value1')])
        self.assertEqual(self.cache.get('key1'), 'value1')

        self.cache.set('key2', 'value2')
        self.assertEqual(set(self.cache.keys()), set(['key1', 'key2']))
        self.assertEqual(set(self.cache.values()), set(['value1', 'value2']))
        self.assertEqual( set(self.cache.items())
                         , set([('key1', 'value1'), ('key2', 'value2')])
                         )
        self.assertEqual(self.cache.get('key2'), 'value2')

        self.cache.set('key3', 'value3')
        self.cache.invalidate('key1')
        self.assertEqual(set(self.cache.keys()), set(['key2', 'key3']))
        self.assertEqual(set(self.cache.values()), set(['value2', 'value3']))
        self.assertEqual( set(self.cache.items())
                         , set([('key2', 'value2'), ('key3', 'value3')])
                         )
        self.assertFalse(self.cache.get('key1'))

        self.cache.set('key3', 'NEW')
        self.assertEqual(self.cache.get('key3'), 'NEW')

        self.cache.invalidate('UNKNOWN')
        self.assertEqual(set(self.cache.keys()), set(['key2', 'key3']))
        self.assertEqual(set(self.cache.values()), set(['value2', 'NEW']))
        self.assertEqual( set(self.cache.items())
                         , set([('key2', 'value2'), ('key3', 'NEW')])
                         )

        self.cache.invalidate()
        self.assertFalse(list(self.cache.keys()))
        self.assertFalse(list(self.cache.values()))
        self.assertFalse(list(self.cache.items()))

    def test_get_set_clear_unicode(self):
        self.cache.set(unicode('key1'), unicode('value1'))
        self.assertEqual(list(self.cache.keys()), [unicode('key1')])
        self.assertEqual(list(self.cache.values()), [unicode('value1')])
        self.assertEqual( list(self.cache.items())
                        , [(unicode('key1'), unicode('value1'))]
                        )
        self.assertEqual(self.cache.get(unicode('key1')), unicode('value1'))

        self.cache.set(unicode('key2'), unicode('value2'))
        self.assertEqual( set(self.cache.keys())
                        , set([unicode('key1'), unicode('key2')])
                        )
        self.assertEqual( set(self.cache.values())
                        , set([unicode('value1'), unicode('value2')])
                        )
        self.assertEqual( set(self.cache.items())
                         , set([ (unicode('key1'), unicode('value1'))
                               , (unicode('key2'), unicode('value2'))
                               ])
                         )
        self.assertEqual(self.cache.get(unicode('key2')), unicode('value2'))

        self.cache.set(unicode('key3'), unicode('value3'))
        self.cache.invalidate(unicode('key1'))
        self.assertEqual( set(self.cache.keys())
                        , set([unicode('key2'), unicode('key3')])
                        )
        self.assertEqual( set(self.cache.values())
                        , set([unicode('value2'), unicode('value3')])
                        )
        self.assertEqual( set(self.cache.items())
                         , set([ (unicode('key2'), unicode('value2'))
                               , (unicode('key3'), unicode('value3'))
                               ])
                         )
        self.assertFalse(self.cache.get(unicode('key1')))

        self.cache.set(unicode('key3'), unicode('NEW'))
        self.assertEqual(self.cache.get(unicode('key3')), unicode('NEW'))

        self.cache.invalidate(unicode('UNKNOWN'))
        self.assertEqual( set(self.cache.keys())
                        , set([unicode('key2'), unicode('key3')])
                        )
        self.assertEqual( set(self.cache.values())
                        , set([unicode('value2'), unicode('NEW')])
                        )
        self.assertEqual( set(self.cache.items())
                         , set([ (unicode('key2'), unicode('value2'))
                               , (unicode('key3'), unicode('NEW'))
                               ])
                         )

        self.cache.invalidate()
        self.assertFalse(list(self.cache.keys()))
        self.assertFalse(list(self.cache.values()))
        self.assertFalse(list(self.cache.items()))

    def test_get_set_clear_nonascii(self):
        key1 = 'schl\xc3\xbcssel1'
        value1 = '\xc3\xa4\xc3\xb6\xc3\xbc\xc3\x9f1'
        key2 = 'schl\xc3\xbcssel2'
        value2 = '\xc3\xa4\xc3\xb6\xc3\xbc\xc3\x9f2'
        key3 = 'schl\xc3\xbcssel3'
        value3 = '\xc3\xa4\xc3\xb6\xc3\xbc\xc3\x9f3'
        self.cache.set(key1, value1)
        self.assertEqual(list(self.cache.keys()), [key1])
        self.assertEqual(list(self.cache.values()), [value1])
        self.assertEqual(list(self.cache.items()), [(key1, value1)])
        self.assertEqual(self.cache.get(key1), value1)

        self.cache.set(key2, value2)
        self.assertEqual(set(self.cache.keys()), set([key1, key2]))
        self.assertEqual(set(self.cache.values()), set([value1, value2]))
        self.assertEqual( set(self.cache.items())
                         , set([(key1, value1), (key2, value2)])
                         )
        self.assertEqual(self.cache.get(key2), value2)

        self.cache.set(key3, value3)
        self.cache.invalidate(key1)
        self.assertEqual(set(self.cache.keys()), set([key2, key3]))
        self.assertEqual(set(self.cache.values()), set([value2, value3]))
        self.assertEqual( set(self.cache.items())
                         , set([(key2, value2), (key3, value3)])
                         )
        self.assertFalse(self.cache.get(key1))

        self.cache.set(key3, 'NEW')
        self.assertEqual(self.cache.get(key3), 'NEW')

        self.cache.invalidate('UNKNOWN')
        self.assertEqual(set(self.cache.keys()), set([key2, key3]))
        self.assertEqual(set(self.cache.values()), set([value2, 'NEW']))
        self.assertEqual( set(self.cache.items())
                         , set([(key2, value2), (key3, 'NEW')])
                         )

        self.cache.invalidate()
        self.assertFalse(list(self.cache.keys()))
        self.assertFalse(list(self.cache.values()))
        self.assertFalse(list(self.cache.items()))

    def test_instancelevel_sharing(self):
        # Make sure cache values are *not* shared across instances
        cache1 = self._makeOne()
        cache2 = self._makeOne()

        cache1.set('key1', 'value1')
        cache2.set('key2', 'value2')

        self.assertFalse(cache1.get('key2'))
        self.assertFalse(cache2.get('key1'))


class TestLockingSimpleCache(TestSimpleCache):

    def _getTargetClass(self):
        from dataflake.cache.simple import LockingSimpleCache
        return LockingSimpleCache


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestSimpleCache),
        unittest.makeSuite(TestLockingSimpleCache),
        ))

