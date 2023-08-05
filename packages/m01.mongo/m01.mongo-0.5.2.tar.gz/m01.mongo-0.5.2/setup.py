##############################################################################
#
# Copyright (c) 2008 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id:$
"""

import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup (
    name='m01.mongo',
    version='0.5.2',
    author = "Roger Ineichen, Projekt01 GmbH",
    author_email = "dev@projekt01.ch",
    description = "MongoDB connection pool and container implementation for Zope3",
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('src', 'm01', 'mongo', 'README.txt')
        + '\n\n' +
        read('src', 'm01', 'mongo', 'container.txt')
        + '\n\n' +
        read('src', 'm01', 'mongo', 'storage.txt')
        + '\n\n' +
        read('src', 'm01', 'mongo', 'shared.txt')
        + '\n\n' +
        read('src', 'm01', 'mongo', 'object.txt')
        + '\n\n' +
        read('src', 'm01', 'mongo', 'batching.txt')
        + '\n\n' +
        read('src', 'm01', 'mongo', 'testing.txt')
        + '\n\n' +
        read('src', 'm01', 'mongo', 'advanced.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = "ZPL 2.1",
    keywords = "Zope3 z3c p01 m01 mongo connection pool container",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    url = 'http://cheeseshop.python.org/pypi/m01.mongo',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['m01'],
    extras_require=dict(
        test=[
            'zope.testing',
            'm01.stub',
        ]),
    install_requires = [
        'setuptools',
        'pymongo',
        'zope.component',
        'zope.container',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.lifecycleevent',
        'zope.location',
        'zope.schema',
        'zope.security',
        'zope.securitypolicy',
        ],
    zip_safe = False,
    )
