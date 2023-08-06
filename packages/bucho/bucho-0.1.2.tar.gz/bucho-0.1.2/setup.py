# -*- coding:utf-8 -*-

try:
    import setuptools
except ImportError:
    import distribute_setup
    distribute_setup.use_setuptools()

import os
import sys

here = os.path.dirname(__file__)
def _read(name):
    try:
        f = open(os.path.join(here, name))
        return f.read()
    except:
        return ""

version = '0.1.2'
name = 'bucho'
short_description = '`bucho` is a package for exercises.'
readme = _read('README.txt')
history = _read('HISTORY.txt')

long_description = readme + "\n" + history

classifiers = [
    'Development Status :: 2 - Pre-Alpha',
    'License :: OSI Approved :: Python Software Foundation License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.2',
    'Topic :: Utilities',
    ]

extra = {}

if sys.version_info >= (3, 0):
    if not getattr(setuptools, '_distribute', False):
        raise RuntimeError(
                'You must installed `distribute` to setup bucho with Python3')
    extra.update(
        use_2to3=True
    )

setuptools.setup(
    name=name,
    version=version,
    description=short_description,
    long_description=long_description,
    classifiers=classifiers,
    keywords=['practice',],
    author='AE35',
    author_email='alpha.echo.35@gmail.com',
    packages = ['bucho'],
    url='http://bitbucket.org/ae35/bucho/',
    license='PSL',
    entry_points = {
        'console_scripts': [
            'bucho=bucho.command:console',
        ],
        'paste.app_factory': [
            'main=bucho.wsgi:app_factory',
        ],
        'bucho.commands': [
            'sample=bucho.plugins:sample',
        ],
    },
    test_suite="bucho",
    **extra
    )

