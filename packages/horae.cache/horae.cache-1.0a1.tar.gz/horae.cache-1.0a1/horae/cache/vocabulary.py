""" Decorators and functions to cache vocabularies
"""
from zope import component

from horae.cache import interfaces
from horae.cache import name

_marker = object()


def _find_parent(context, parent):
    try:
        while not parent.providedBy(context):
            context = context.__parent__
    except:
        pass
    return context


class cache(object):
    """ Base decorator implementation to cache a vocabulary
    """

    def __init__(self, func):
        self.func = func
        self.cache = None
        self.__doc__ = func.__doc__

    def __call__(self, context):
        if self.cache is not None:
            key = name(self.func)
            cached = self.cache.get(key, _marker)
            if cached is not _marker:
                return cached
            result = self.func(context)
            self.cache.set(key, result)
            return result
        return self.func(context)


class cache_contextual(cache):
    """ Decorator to cache a vocabulary on the context
    """

    def __init__(self, func, parent=None):
        super(cache_contextual, self).__init__(func)
        self.parent = parent

    def __call__(self, context):
        ccontext = context
        if self.parent is not None:
            ccontext = _find_parent(ccontext, self.parent)
        if ccontext is not None:
            self.cache = interfaces.ICache(ccontext)
        return super(cache_contextual, self).__call__(context)


class cache_contextual_parent(object):
    """ Decorator to cache a vocabulary on the parent of the context
    """

    def __init__(self, parent):
        self.parent = parent

    def __call__(self, func):
        return cache_contextual(func, self.parent)


class cache_global(cache):
    """ Decorator to cache a vocabulary globally
    """

    def __call__(self, context):
        self.cache = component.getUtility(interfaces.ICache)
        return super(cache_global, self).__call__(context)


def invalidate_contextual(context, func):
    """ Function to invalidate the cache of cached vocabularies created by
        :py:func:`cache_contextual` where context is the context and
        func is the vocabulary factory
    """
    interfaces.ICache(context).invalidate(name(func.func))


def invalidate_contextual_parent(context, parent, func):
    """ Function to invalidate the cache of cached vocabularies created by
        :py:func:`cache_contextual_parent` where context is the context,
        parent is an interface to look up the parent and func is the
        vocabulary factory
    """
    invalidate_contextual(_find_parent(context, parent), func)


def invalidate_global(func):
    """ Function to invalidate the cache of cached vocabularies created by
        :py:func:`cache_global` where func is the vocabulary factory
    """
    component.getUtility(interfaces.ICache).invalidate(name(func.func))
