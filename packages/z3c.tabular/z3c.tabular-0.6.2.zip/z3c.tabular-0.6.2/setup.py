##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
    content = open(os.path.join(os.path.dirname(__file__), *rnames)).read()
    return content + '\n\n'

setup (
    name='z3c.tabular',
    version='0.6.2',
    author = "Roger Ineichen and the Zope Community",
    author_email = "zope-dev@zope.org",
    description = "Table with form support based on z3c.form and z3c.table for Zope3",
    long_description=(
        read('README.txt') +
        '.. contents::\n\n' +
        read('CHANGES.txt') +
        read('src', 'z3c', 'tabular', 'README.txt')
        ),
    license = "ZPL 2.1",
    keywords = "zope3 z3c tabular data form table contents",
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
    url = 'http://pypi.python.org/pypi/z3c.tabular',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['z3c'],
    extras_require = dict(
        test = [
            'z3c.form[test]',
            'z3c.macro',
            'z3c.testing',
            'zope.app.publisher',
            'zope.app.testing',
            'zope.browserpage',
            'zope.publisher',
            'zope.testing',
            ],
        ),
    install_requires = [
        'setuptools',
        'z3c.form',
        'z3c.formui',
        'z3c.table',
        'z3c.template',
        'zope.i18nmessageid',
        'zope.interface',
        ],
    zip_safe = False,
)
