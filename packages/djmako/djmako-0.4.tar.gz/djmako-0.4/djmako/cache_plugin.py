"""
A cache plugin for mako that uses the django cache.
"""
from mako.cache import CacheImpl, register_plugin

_djcache = None

class DjangoCacheImpl(CacheImpl):
    """
    A mako cache plugin that calls the django cache.
    """
    
    def __init__(self, cache):
        super(DjangoCacheImpl, self).__init__(cache)
        global _djcache
        if _djcache is None:
            from django.core.cache import cache as _djcache
        self._djcache = _djcache
    
    def get_or_create(self, key, creation_function, **kw):
        djkey = 'djmako-' + key
        value = self._djcache.get(djkey)
        if value is None:
            value = creation_function()
            self._djcache.set(djkey, value)
        return value

    def set(self, key, value, **kwargs):
        self._djcache.set('djmako-' + key, value)

    def get(self, key, **kwargs):
        return self._djcache.get('djmako-' + key)

    def invalidate(self, key, **kwargs):
        self._djcache.remove('djmako-' + key)


register_plugin('djmakocache', __name__, 'DjangoCacheImpl')
