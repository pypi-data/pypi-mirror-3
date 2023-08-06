"""
Some Python decorators
"""

# The @synchronized decorator can be used to serialize access to
# shared resources using a lock:
#
# Example:
#
# from threading import Lock
# from haufe.decorator import synchronized
#
# lock = Lock()
# shared_resource = ....
#
# @synchronized(lock)
# def critical_method(...):
#     do_something_with(shared_resource)
#     ....
#
# @synchronized can also be used with classes. In this case you
# need to define a lock as class variable:
#
# Example:
# 
# class Foo(object):
# 
#     lock = Lock
#
#     @syncronized 
#     def critical_method(self,....):
#         do_something_with(shared_resource)
#         ....


def synchronized(lock):
    """ Decorator for method synchronization. """

    def wrapper(f):
        def method(*args, **kw):
            lock.acquire()
            try:
                return f(*args, **kw)
            finally:
                lock.release()
        return method
    return wrapper


# The @tracer decorator allows you to trace a particular function call
# including its parameters without having the need to actually modify
# the method itself. The tracer output goes to the console (stdout).
#
# Example:
#
# from haufe.decorator import tracer
#
# @tracer
# def sum(a, b):
#     return a + b
#
# sum(2, 3)
# sum(1, 7)
#

import sys

def tracer(method):
    """ A simple decorator to trace method calls and its parameters """

    def wrapper(*args, **kw):
        print >>sys.stdout, 'Calling: %s (%s, %s)' % (method.__name__, args, kw)
        return method(*args, **kw)

    return wrapper


# The @memoize decoractor caches the results of method calls by their
# call parameters
#
# Example
#
# from haufe.decorator import memoize
#
# @memoize
# def expensive_method(a, b):
#    return pow(a, b)
#
# expensive_method(2, 3)  # calls actually pow()
# expensive_method(2, 3)  # gets the result from the cache

import cPickle

def memoize(function, limit=None):
    if isinstance(function, int):
        def memoize_wrapper(f):
            return memoize(f, function)

        return memoize_wrapper

    dict = {}
    list = []
    def memoize_wrapper(*args, **kwargs):
        key = cPickle.dumps((args, kwargs))
        try:
            list.append(list.pop(list.index(key)))
        except ValueError:
            dict[key] = function(*args, **kwargs)
            list.append(key)
            if limit is not None and len(list) > limit:
                del dict[list.pop(0)]

        return dict[key]

    memoize_wrapper._memoize_dict = dict
    memoize_wrapper._memoize_list = list
    memoize_wrapper._memoize_limit = limit
    memoize_wrapper._memoize_origfunc = function
    memoize_wrapper.func_name = function.func_name
    return memoize_wrapper

