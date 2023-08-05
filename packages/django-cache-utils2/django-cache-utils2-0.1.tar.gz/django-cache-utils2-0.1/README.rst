===================
django-cache-utils2
===================

django-cache-utils2 provides ``cached`` decorator and ``invalidate`` function.

Installation
============

::

    pip install django-cache-utils2

Usage
=====

::

    from cache_utils2 import cached, invalidate

    @cached(60)
    def foo(x, y=0):
        print 'foo is called'
        return x+y

    foo(1, 2) # foo is called
    foo(1, y=2)
    foo(5, 6) # foo is called
    foo(5, 6)
    invalidate(foo, {'x': 1, 'y': 2})
    foo(1, 2) # foo is called
    foo(5, 6)
    foo(x=2) # foo is called
    foo(x=2)

    class Foo(object):
        @cached(60)
        def foo(self, x, y):
            print "foo is called"
            return x+y

    obj = Foo()
    obj.foo(1,2) # foo is called
    obj.foo(1,2)

    invalidate(Foo.foo, {'x': 1, 'y': 2})
    obj.foo(1,2) # foo is called



Django example
--------------

::

    from django.db import models
    from cache_utils2 import cached, invalidate

    class CityManager(models.Manager):

        # cache a method result. 'self' parameter is ignored
        @cached(60*60*24)
        def default(self):
            return self.active()[0]

        # cache a method result. 'self' parameter is ignored, args and
        # kwargs are used to construct the cache key
        @cached(60*60*24)
        def get(self, *args, **kwargs):
            return super(CityManager, self).get(*args, **kwargs)


    class City(models.Model):
        # ... field declarations

        objects = CityManager()

        # cache django model instance method result by instance pk
        @cached(30, vary='self.pk')
        def has_offers(self):
            return self.offer_set.count() > 0

    # invalidation of model methods
    invalidate(City.has_offers, {'self.pk': 1}


Notes
=====

If decorated function returns ``cache_utils2.NO_CACHE`` cache will be bypassed.


Running tests
=============

Get the source code and run ``runtests.py``.
