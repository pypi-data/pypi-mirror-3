#!/usr/bin/env python

import os

from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
        name='django_factory',
        version='0.1',
        description=('Generic factory for creating instances of Django '
                     'models in tests.'),
        author='James Westby',
        author_email='james.westby@canonical.com',
        url='https://launchpad.net/django_factory',
        packages=['django_factory'],
        install_requires=['django>=1.1'],
        test_requires=['testtools'],
        license="Apache-2",
        long_description=read('README'),
)
