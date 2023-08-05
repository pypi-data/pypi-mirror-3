# -*- coding: utf-8 -*-
import inspect
import functools
from django.core.cache import get_cache, DEFAULT_CACHE_ALIAS
from cache_utils2.utils import get_func_name, serialize_params
from cache_utils2.exceptions import CacheUtilsException

NO_CACHE = object()

def _get_key(name, params, vary):
    param_str = serialize_params(params, vary)
    return '[CU2]%s(%s)' % (name, param_str,)


def cached(timeout, vary=None, name=None, backend=DEFAULT_CACHE_ALIAS):
    cache = get_cache(backend)
    if isinstance(vary, basestring):
        vary = vary.split()

    def _cached(func):
        cache_name = get_func_name(func) if name is None else name
        get_key = functools.partial(_get_key, cache_name, vary=vary)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            params = inspect.getcallargs(func, *args, **kwargs)
            key = get_key(params)
            value = cache.get(key, NO_CACHE)

            if value is NO_CACHE:
                value = func(*args, **kwargs)
                if value is not NO_CACHE:
                    cache.set(key, value, timeout)
                # XXX: is it ok we are returning NO_CACHE?

            return value

        wrapper._cache_name = cache_name
        return wrapper

    return _cached


def invalidate(func, params, backend=DEFAULT_CACHE_ALIAS):
    if hasattr(func, '_cache_name'):
        name = func._cache_name
    elif isinstance(func, basestring):
        name = func
    else:
        raise CacheUtilsException('invalidate accepts either callble or cached function name')

    vary = params.keys()

    # Add self to params for bound methods.
    # I haven't find a way to make obj.cached_func.invalidate
    # access bound 'self' value for obj.cached_func (decorator is applied to unbound method and
    # descriptors doesn't work with instances) so invalidation is moved to a
    # separate function.

    if hasattr(func, 'im_self'):
        params['self'] = func.im_self

    cache = get_cache(backend)
    key = _get_key(name, params, vary)
    cache.delete(key)

