#!/usr/bin/env python
from distutils.core import setup

version='0.1'

setup(
    name='django-cache-utils2',
    version=version,
    author='Mikhail Korobov',
    author_email='kmike84@gmail.com',

    packages=['cache_utils2'],

    url='http://bitbucket.org/kmike/django-cache-utils2/',
    download_url = 'http://bitbucket.org/kmike/django-cache-utils2/get/tip.zip',
    license = 'MIT license',
    description = """ Django caching decorator + invalidate function """,

    long_description = open('README.rst').read(),
    requires = ['django (>= 1.3)'],

    classifiers=(
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ),
)
