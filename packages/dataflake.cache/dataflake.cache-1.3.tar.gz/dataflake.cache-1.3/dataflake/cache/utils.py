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
""" utility functions and constants for dataflake.cache

$Id$
"""

try:
    from functools import wraps
except ImportError:
    ASSIGN = ('__module__', '__name__', '__doc__')
    UPDATE = ('__dict__',)

    def wrap(_wrapped_func, *args, **kw):
        def _wrapped(*moreargs, **morekw):
            return _wrapped_func(*(args+moreargs), **dict(kw, **morekw))
        return _wrapped

    def update_wrapper(wrapper, wrapped, assigned=ASSIGN, updated=UPDATE):
        for attr in assigned:
            setattr(wrapper, attr, getattr(wrapped, attr))
        for attr in updated:
            getattr(wrapper, attr).update(getattr(wrapped, attr))
        return wrapper

    def wraps(wrapped, assigned=ASSIGN, updated=UPDATE):
        return wrap( update_wrapper
                   , wrapped=wrapped
                   , assigned=assigned
                   , updated=updated
                   )

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
