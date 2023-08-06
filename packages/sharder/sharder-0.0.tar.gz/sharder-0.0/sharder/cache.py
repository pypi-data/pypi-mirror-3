"""
Caching configuration.
"""

from retools.cache import CacheRegion, cache_region

EPHEMERAL = 'ephemeral'
SHARDS = 'shards'
CacheRegion.add_region(EPHEMERAL, expires=60)
CacheRegion.add_region(SHARDS, expires=60)
cache_region = cache_region # lint
