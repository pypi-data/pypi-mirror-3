""" Decorator to cache method and function output on the request
"""
from persistent import Persistent

from zope import security
from zope.publisher.interfaces import IRequest

from horae.cache import interfaces
from horae.cache import name

_marker = object()


def getRequest():
    try:
        i = security.management.getInteraction() # raises NoInteraction
        for p in i.participations:
            if IRequest.providedBy(p):
                return p
    except:
        pass
    return None


class cache(object):
    """ Decorator to cache method and function output on the request
    """

    def __init__(self, args=None, kwargs=None):
        self.args = args
        self.kwargs = kwargs

    def __call__(self, func):
        def request_getter(*args, **kwargs):
            request = getRequest()
            cache = interfaces.ICache(request) if request is not None else None
            if cache is not None:
                key = [name(func), ]
                if self.args is None:
                    key.append(args[0].__class__)
                    if isinstance(args[0], Persistent):
                        key.append(args[0]._p_oid)
                    key.extend(args[1:])
                else:
                    for i in self.args:
                        key.append(args[i])
                if self.kwargs is None:
                    key.extend(kwargs.values())
                else:
                    for i in self.kwargs:
                        key.append(kwargs[i])
                cached = cache.get(tuple(key), _marker)
                if cached is not _marker:
                    return cached
                result = func(*args, **kwargs)
                cache.set(tuple(key), result)
                return result
            return func(*args, **kwargs)
        request_getter.__doc__ = func.__doc__
        return request_getter
