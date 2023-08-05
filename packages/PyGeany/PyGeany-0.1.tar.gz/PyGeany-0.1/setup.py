# -*- coding: utf-8 -*-

import sys

from setuptools import setup, find_packages


extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

setup(
    name='PyGeany',
    version='0.1',
    description="Provides support for geany's control socket",
    url='https://github.com/EisenSheng/PyGeany',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: Public Domain',
        'Topic :: Software Development :: Libraries'
    ],

    py_modules=['PyGeany'],
    zip_safe=True,
    install_requires=['distribute'],

    author='Arthur S.',
    author_email='arthur.s@redsmile.org',

    long_description=open('README.rst').read(),

    **extra
)
