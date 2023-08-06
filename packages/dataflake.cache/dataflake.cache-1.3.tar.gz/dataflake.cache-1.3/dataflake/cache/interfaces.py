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
""" Cache implementation interfaces for dataflake.cache

$Id$
"""

from zope.interface import Interface

class ICache(Interface):
    """ Simple cache interface
    """

    def set(key, value):
        """ Store a key/value pair
        """

    def get(key, default=None):
        """ Get value for the given key

        If no value is found or the value is invalid, the default value
        will be returned.
        """

    def invalidate(key=None):
        """ Invalidate the given key, or all key/values if no key is passed.
        """

    def keys():
        """ Return all cache keys
        """

    def values():
        """ Return all cached values
        """

    def items():
        """ Return all cached keys and values

        Returns a sequence of (key, value) tuples.
        """

class ITimeoutCache(ICache):
    """ Simple cache with a timeout

    Only records younger than the configured timeout are returned
    """

    def setTimeout(timeout):
        """ Set a timeout value in seconds
        """

    def getTimeout():
        """ Get the timeout value
        """
