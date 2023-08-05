import grok

from BTrees.IOBTree import IOBTree
from BTrees.OIBTree import OIBTree

from zope import interface
from zope.site.hooks import getSite

from horae.cache import interfaces

_cache_id = OIBTree()


class CacheBase(object):
    """ An abstract :py:class:`horae.cache.interfaces.ICache`
    """
    grok.implements(interfaces.ICache)
    _storage = None
    _attr = '_v_horae_cache'

    def _id(self, name):
        id = _cache_id.get(name, None)
        if id is None:
            id = len(_cache_id)
            _cache_id[name] = id
        return id

    def set(self, name, value):
        self._storage[self._id(name)] = value

    def get(self, name, default=None):
        return self._storage.get(self._id(name), default)

    def invalidate(self, name):
        id = self._id(name)
        if id in self._storage:
            del self._storage[id]


class Cache(CacheBase, grok.Adapter):
    """ A :py:class:`horae.cache.interfaces.ICache` implementation
        storing its values on the adapted context
    """
    grok.context(interface.Interface)

    def __init__(self, context):
        super(Cache, self).__init__(context)
        if not hasattr(context, self._attr):
            setattr(context, self._attr, IOBTree())
        self._storage = getattr(context, self._attr)


class GlobalCache(CacheBase, grok.GlobalUtility):
    """ A :py:class:`horae.cache.interfaces.ICache` implementation
        storing its values globally
    """
    __storage = None

    def __init__(self):
        pass

    @property
    def _storage(self):
        if self.__storage is None:
            site = getSite()
            if site is None:
                return {}
            if not hasattr(site, self._attr):
                setattr(site, self._attr, IOBTree())
            self.__storage = getattr(site, self._attr)
        return self.__storage
