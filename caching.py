import os
from functools import wraps
from werkzeug.contrib.cache import (RedisCache, SimpleCache,
                                    FileSystemCache, MemcachedCache)
import settings


cache_class_map = {
    "redis": RedisCache,
    "memory": SimpleCache,
    "file": FileSystemCache,
    "memcached": MemcachedCache
}

cache_type_name = settings.get("cache_type").lower()
cache_type = cache_class_map[cache_type_name]

if cache_type_name == "redis":
    cache_options = {
        'default_timeout': int(settings.get("redis_cache_default_timeout")),
        'key_prefix': settings.get("redis_cache_key_prefix"),
        'host': settings.get("redis_host"),
        'port': int(settings.get("redis_port")),
        'password': settings.get("redis_pw"),
        'db': int(settings.get("redis_db")),
    }
    cache_options['password'] = None if not cache_options['password'] \
        else cache_options['password']

elif cache_type_name == "memory":
    cache_options = {}

elif cache_type_name == "file":
    cache_dir = settings.get("file_cache_dir")
    if not os.path.isdir(cache_dir):
        os.mkdir(cache_dir)
    cache_options = {
        'cache_dir': cache_dir,
        'threshold': settings.get("file_cache_threshold"),
        'default_timeout': settings.get("file_cache_default_timeout"),
        'mode': int(settings.get("file_cache_file_mode"))
    }

elif cache_type_name == "memcached":
    servers = (x.strip() for x in settings.get("memcached_servers").split(","))
    cache_options = {
        'servers': servers,
        'default_timeout': settings.get('memcached_default_timeout'),
        'key_prefix': settings.get('memcached_key_prefix')
    }

else:
    raise ValueError("Cache type must be one of file, redis, memcached "
                     "or memory.")

cache = cache_type(**cache_options)


def cached(timeout=None, skip_lookup_if=None, skip_store_if=lambda x: False):
    """Get a decorator to cache func. return values until timeout (s).

    :param timeout: time in seconds to keep value in cache; default if None.
    :param skip_lookup_if: callable that, if returns truthy, skips cache. If
     None, always checks cache. If the cache check is skipped, will still store
     the new value in cache.
    :param skip_store_if: A callable that takes one argument (the `requests`
     Response object) and if returns truthy, does not store result in cache.
     By default, always caches.
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            key = "{}--{}--{}".format(f.__name__, repr(args), repr(kwargs))
            skip = skip_lookup_if() if skip_lookup_if else None
            r = None if skip else cache.get(key)
            if r is None:
                r = f(*args, **kwargs)
                if not skip_store_if(r):
                    cache.set(key, r, timeout)
            return r
        return wrapper
    return decorator
