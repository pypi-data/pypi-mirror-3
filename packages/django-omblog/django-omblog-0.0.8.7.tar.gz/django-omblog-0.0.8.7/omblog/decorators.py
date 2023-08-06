from django.core.cache import cache
from omblog.cache import get_key


def cache_page(fn):
    """If a cached version of the page exists - return that
    unless the kill clearcache parameter is in the get and
    the user is auth'd.  """

    def _cache_page(request, *args, **kwargs):
        if request.user.is_authenticated():
            return fn(request, *args, **kwargs)
        signature = '%s_%s' % (fn.__name__, '_'.join(kwargs.values()))
        key = get_key(signature)
        if 'clearcache' not in request.GET.keys():
            cached = cache.get(key)
            if cached:
                return cached
        out = fn(request, *args, **kwargs)
        cache.set(key, out, 0)
        return out

    return _cache_page
