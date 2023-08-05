from zope import interface


class ICache(interface.Interface):
    """ Caching adapter
    """

    def set(name, value):
        """ Sets the cache value for the given name
        """

    def get(name, default=None):
        """ Gets the cache value for the given name returns default
            if no value was previously set
        """

    def invalidate(name):
        """ Invalidates the cache for the given name
        """
