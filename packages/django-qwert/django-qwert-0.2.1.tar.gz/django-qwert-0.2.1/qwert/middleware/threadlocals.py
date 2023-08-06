# vim: set fileencoding=utf-8 :
"""
Middleware to store request instance during request


AUTHOR:
    lambdalisue[Ali su ae] (lambdalisue@hashnote.net)
    
License:
    The MIT License (MIT)

    Copyright (c) 2012 Alisue allright reserved.

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to
    deal in the Software without restriction, including without limitation the
    rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
    sell copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
    IN THE SOFTWARE.

"""
from __future__ import with_statement
try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

__all__ = ['get_request', 'ThreadLocalsMiddleware']
_thread_locals = local()

def get_request():
    """Return stored request instance in current thread"""
    return getattr(_thread_locals, 'request', None)

class ThreadLocalsMiddleware(object):
    """
    Middleware that store current request in thread local storage.
    This middleware should come at the top of the MIDDLEWARE_CLASSES list.
    
    """
    def process_request(self, request):
        # save current request instance
        _thread_locals.request = request

    def process_response(self, request, response):
        # remove saved request instance
        if hasattr(_thread_locals, 'request'):
            delattr(_thread_locals, 'request')
        return response
