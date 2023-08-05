from __future__ import absolute_import
import functools
from .decorators import cached, invalidate

cached_by_pk = functools.partial(cached, vary='self.pk')

def invalidate_pk_queryset(func, qs):
    for pk in qs.values_list('pk', flat=True):
        invalidate(func, {'self.pk': pk})