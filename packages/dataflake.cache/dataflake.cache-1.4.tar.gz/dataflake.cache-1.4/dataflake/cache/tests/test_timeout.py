##############################################################################
#
# Copyright (c) 2009-2010 Jens Vagelpohl and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Tests for the Timeout cache class

$Id$
"""

import time
import unittest

from dataflake.cache.tests.base import CacheTestCase

       
class TestTimeoutCache(CacheTestCase):

    def _getTargetClass(self):
        from dataflake.cache.timeout import TimeoutCache
        return TimeoutCache

    def test_conformance(self):
        from dataflake.cache.interfaces import ITimeoutCache
        from zope.interface.verify import verifyClass
        verifyClass(ITimeoutCache, self._getTargetClass())

    def test_initial_state(self):
        self.assertFalse(self.cache.keys())
        self.assertFalse(self.cache.values())
        self.assertFalse(self.cache.items())

    def test_get_set_clear(self):
        self.assertFalse(self.cache.keys())
        self.assertFalse(self.cache.values())
        self.assertFalse(self.cache.items())

        self.cache.set('key1', 'value1')
        self.assertEqual(self.cache.keys(), ['key1'])
        self.assertEqual(self.cache.values(), ['value1'])
        self.assertEqual(self.cache.items(), [('key1', 'value1')])
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
        self.assertFalse(self.cache.keys())
        self.assertFalse(self.cache.values())
        self.assertFalse(self.cache.items())

    def test_timeout(self):
        # initial state
        self.assertEqual(self.cache.getTimeout(), 600)

        self.cache.setTimeout(0.1)
        self.assertEqual(self.cache.getTimeout(), 0.1)

        self.cache.set('key1', 'value1')
        self.assertEqual(self.cache.keys(), ['key1'])
        self.assertEqual(self.cache.values(), ['value1'])
        self.assertEqual(self.cache.items(), [('key1', 'value1')])
        self.assertEqual(self.cache.get('key1'), 'value1')

        # Wait for the timeout. The key must be gone.
        time.sleep(0.3)
        self.assertFalse(self.cache.keys())
        self.assertFalse(self.cache.values())
        self.assertFalse(self.cache.items())
        self.assertFalse(self.cache.get('key1'))


    def test_instancelevel_sharing(self):
        # Make sure cache values are *not* shared across instances
        cache1 = self._makeOne()
        cache2 = self._makeOne()

        cache1.set('key1', 'value1')
        cache2.set('key2', 'value2')

        self.assertFalse(cache1.get('key2'))
        self.assertFalse(cache2.get('key1'))


class TestLockingTimeoutCache(TestTimeoutCache):

    def _getTargetClass(self):
        from dataflake.cache.timeout import LockingTimeoutCache
        return LockingTimeoutCache


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestTimeoutCache),
        unittest.makeSuite(TestLockingTimeoutCache),
        ))

