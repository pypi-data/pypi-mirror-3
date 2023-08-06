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
""" utility functions and constants for dataflake.cache

$Id$
"""

from functools import wraps

def protect_with_lock(decorated):
    """ Decorator function: serialize access to 'decorated' using a lock
    """
    @wraps(decorated)
    def protector(self, *args, **kw):
        """ The function protecting the decorated function
        """
        self.lock.acquire()
        try:
            return decorated(self, *args, **kw)
        finally:
            self.lock.release()

    return protector
