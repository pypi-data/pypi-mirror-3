##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""Setup

$Id: setup.py 127012 2012-06-22 13:18:26Z faassen $
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    text = open(os.path.join(os.path.dirname(__file__), *rnames)).read()
    text = unicode(text, 'utf-8').encode('ascii', 'xmlcharrefreplace')
    return text

tests_require = [
    'zope.testing',
    ]

setup(
    name="hurry.query",
    version='1.1.1',
    author='Infrae',
    author_email='faassen@startifact.com',
    description="Higher level query system for the zope.catalog",
    long_description=read('src','hurry','query','query.txt') +
                     '\n\n' +
                     read('CHANGES.txt'),
    license='ZPL 2.1',
    keywords="zope zope3 catalog index query",
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    url = 'http://pypi.python.org/pypi/hurry.query',
    packages=find_packages('src'),
    package_dir= {'':'src'},

    namespace_packages=['hurry'],
    package_data = {
    '': ['*.txt', '*.zcml'],
    },

    zip_safe=False,
    install_requires=[
        'setuptools',
        'zc.catalog',
        'ZODB3',
        'zope.catalog',
        'zope.component',
        'zope.interface',
        'zope.intid',
        ],
    tests_require = tests_require,
    extras_require = {'test': tests_require},
    )
