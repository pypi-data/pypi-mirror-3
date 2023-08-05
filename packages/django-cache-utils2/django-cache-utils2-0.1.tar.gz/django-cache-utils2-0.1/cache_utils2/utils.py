from hashlib import md5
import inspect
from django.utils.encoding  import smart_unicode
from cache_utils2.exceptions import CacheUtilsException

def get_func_name(func):
    if inspect.isfunction(func):
        return ".".join([func.__module__, func.__name__])

    if inspect.ismethod(func):
        class_name = func.im_class.__name__
        return ".".join([func.__module__, class_name, func.__name__])

    raise CacheUtilsException("Can't decorate %s" % func)


def _filter_params(params, vary):
    for name in vary:
        if name in params:
            yield name, params[name]
        else:
            yield name, eval(name, {'__builtins__': None}, params)


def serialize_params(params, vary=None):
    if vary is not None:
        params = dict(_filter_params(params, vary))
    else:
        # by default 'self' argument is not used for key construction
        # this can be overriden using 'vary' argument
        params.pop('self', None)
    params_str = smart_unicode(params).encode('utf8')
    return md5(params_str).hexdigest()

