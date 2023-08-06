"""
Mako templates for django >= 1.2.
"""

from .loader import MakoLoader

try:
    import djmako.cache_plugin
except ImportError:
    print "cannot import cache plugin"
    pass
