from django.core.cache import cache

def fetch(key, val_or_function, *args, **kwargs):
    """
    This function tries to get given key from cache.
    If key is not in cache it returns val_or_funcion value and caches it for next-time use.
    """
    val = cache.get(key)
    if not val:
        cache_time = kwargs.pop('cache_time', None)

        if hasattr(val_or_function, '__call__'):
            val = val_or_function(*args, **kwargs)
        else:
            val = val_or_function

        cache.set(key, val, cache_time)
    return val
