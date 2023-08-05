#coding: utf-8
from django.utils import unittest
from django.core.cache import cache
from cache_utils2 import cached, NO_CACHE, invalidate
from cache_utils2.utils import get_func_name

def foo(a,b):
    pass

class Foo(object):

    def foo(self, a, b):
        pass

    @classmethod
    def bar(cls, x):
        pass

class Store(object):
    """ Class for encoding error test """
    def __unicode__(self):
        return u'Вася'
    def __repr__(self):
        return u'Вася'.encode('utf8')


class FuncInfoTest(unittest.TestCase):

    def assertName(self, obj, name):
        self.assertEqual(get_func_name(obj), name)

    def test_func(self):
        self.assertName(foo, 'cache_utils2.tests.foo')

    def test_method(self):
        self.assertName(Foo.foo, 'cache_utils2.tests.Foo.foo')

    @unittest.expectedFailure
    def test_classmethod(self):
        self.assertName(Foo.bar, 'cache_utils2.tests.Foo.bar')


class BaseClearCacheTest(unittest.TestCase):
    def tearDown(self):
        cache.clear()

    def setUp(self):
        cache.clear()


class InvalidationTestBase(BaseClearCacheTest):

    def test_func_invalidation(self):
        self.call_count = 0

        @cached(60, name='func_invalidation.my_func')
        def my_func(a, b):
            self.call_count += 1
            return self.call_count

        self.assertEqual(my_func(1,2), 1)
        self.assertEqual(my_func(1,2), 1)
        self.assertEqual(my_func(3,2), 2)
        self.assertEqual(my_func(3,2), 2)

        invalidate(my_func, dict(a=3, b=2))

        self.assertEqual(my_func(1,2), 1)
        self.assertEqual(my_func(3,2), 3)
        self.assertEqual(my_func(3,2), 3)

        invalidate('func_invalidation.my_func', {'a': 3, 'b': 2})
        self.assertEqual(my_func(3,2), 4)
        self.assertEqual(my_func(3,2), 4)

        invalidate(my_func, {'a': 3, 'b': 2})
        self.assertEqual(my_func(3,2), 5)

    def test_method_invalidation(self):
        self.call_count = 0
        this = self

        class Foo(object):

            @cached(60, name='invalidation.Foo.bar')
            def bar(self, x):
                this.call_count += 1
                return this.call_count

        foo = Foo()
        self.assertEqual(foo.bar(1), 1)
        self.assertEqual(foo.bar(1), 1)

        foo2 = Foo()
        self.assertEqual(foo2.bar(1), 1)

        invalidate(foo.bar, {'x': 1})
        self.assertEqual(foo.bar(1), 2)
        self.assertEqual(foo.bar(1), 2)

        invalidate(Foo.bar, {'x': 1})
        self.assertEqual(foo.bar(1), 3)
        self.assertEqual(foo.bar(1), 3)


    def test_method_invalidation_binding(self):
        self.call_count = 0
        this = self

        class Bar(object):
            def __init__(self, pk):
                self.pk = pk

            @cached(60, vary='self.pk')
            def bar(self):
                this.call_count += 1
                return "%s %s" % (self.pk, this.call_count)


        bar1 = Bar(1)
        bar2 = Bar(2)

        self.assertEqual(bar1.bar(), '1 1')
        self.assertEqual(bar1.bar(), '1 1')

        self.assertEqual(bar2.bar(), '2 2')
        self.assertEqual(bar2.bar(), '2 2')

        invalidate(bar1.bar, {'self.pk': 1})
        self.assertEqual(bar2.bar(), '2 2')
        self.assertEqual(bar1.bar(), '1 3')



    def test_invalidate_nonexisting(self):
        @cached(60)
        def foo(x):
            return 1
        invalidate(foo, {'x': 5}) # this shouldn't raise exception


class DecoratorTestBase(BaseClearCacheTest):

    def test_decorator(self):
        self._x = 0

        @cached(60)
        def my_func(params=""):
            self._x += 1
            return u"%d%s" % (self._x, params)

        self.assertEqual(my_func(), "1")
        self.assertEqual(my_func(), "1")
        self.assertEqual(my_func(""), "1")

        self.assertEqual(my_func("x"), u"2x")
        self.assertEqual(my_func("x"), u"2x")

        self.assertEqual(my_func(u"Василий"), u"3Василий")
        self.assertEqual(my_func(params=u"Василий"), u"3Василий")

        self.assertEqual(my_func(u"й"*240), u"4"+u"й"*240)
        self.assertEqual(my_func(u"й"*240), u"4"+u"й"*240)

        self.assertEqual(my_func(u"Ы"*500), u"5"+u"Ы"*500)
        self.assertEqual(my_func(u"Ы"*500), u"5"+u"Ы"*500)


    def test_utf8_args(self):
        @cached(60)
        def func(utf8_array, *args):
            return utf8_array
        func([u'Василий'.encode('utf8')], u'Петрович'.encode('utf8'))

    def test_utf8_repr(self):
        @cached(60)
        def func(param):
            return param

        func(Store())

    def test_params_simple(self):

        self._x = 0

        @cached(60, 'y', 'test_params_simple.my_func')
        def my_func(x, y=1):
            self._x += 1
            return u'%d x:%s y:%s' % (self._x, x, y)

        self.assertEqual(my_func(1), "1 x:1 y:1")
        self.assertEqual(my_func(1), "1 x:1 y:1")
        self.assertEqual(my_func(1,1), "1 x:1 y:1")

        self.assertEqual(my_func(1,2), "2 x:1 y:2")
        self.assertEqual(my_func(2,2), "2 x:1 y:2")


    def test_attribute_lookup(self):
        self._x = 0
        this = self

        class Foo(object):
            def __init__(self, pk):
                self.pk = pk

            @cached(60, ['self.pk'], 'Foo.meth')
            def meth(self, x):
                this._x += 1
                return u'%d x:%s' % (this._x, x)

        foo = Foo(5)
        self.assertEqual(foo.meth(1), '1 x:1')
        self.assertEqual(foo.meth(2), '1 x:1')

        foo2 = Foo(2)
        self.assertEqual(foo2.meth(1), '2 x:1')
        self.assertEqual(foo2.meth(2), '2 x:1')


    def test_cache_None(self):
        self._x = 0

        @cached(60, name='test_cache_None.my_func')
        def my_func():
            self._x += 1
            return None

        self.assertEqual(my_func(), None)
        self.assertEqual(my_func(), None)
        self.assertEqual(self._x, 1)

    def test_no_cache(self):
        self._x = 0

        @cached(60, name='test_no_cache.my_func')
        def my_func():
            self._x += 1
            return NO_CACHE

        self.assertEqual(my_func(), NO_CACHE)
        self.assertEqual(my_func(), NO_CACHE)
        self.assertEqual(self._x, 2)

