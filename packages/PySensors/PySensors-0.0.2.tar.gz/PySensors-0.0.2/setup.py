#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup
import sensors

setup(
    name='PySensors',
    version=sensors.__version__,
    author=sensors.__author__,
    author_email=sensors.__contact__,
    packages=['sensors'],
    #scripts=[],
    url='http://pypi.python.org/pypi/PySensors/',
    #download_url='',
    license=sensors.__license__,
    description='Python bindings to libsensors (via ctypes)',
    long_description=open('README.rst').read(),
    keywords=['sensors', 'hardware', 'monitoring'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Topic :: System',
        'Topic :: System :: Hardware',
        'Topic :: System :: Monitoring',
    ]
)
