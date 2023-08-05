##############################################################################
#
# Copyright (c) 2003, 2010 Zope Foundation and Contributors.
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
""" Setup for zope.mkzeoinstance package
"""

import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name='zope.mkzeoinstance',
    version='3.9.5',
    url='http://pypi.python.org/pypi/zope.mkzeoinstance',
    license='ZPL 2.1',
    description='Make standalone ZEO database server instances',
    author='Zope Foundation and Contributors',
    author_email='zope-dev@zope.org',
    long_description=(
        read('README.txt')
        + '\n' +
        read('CHANGES.txt')
        ),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.4",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],

    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['zope',],
    include_package_data=True,
    install_requires=[
        'setuptools',
        'ZODB3 >= 3.9.4',
    ],
    zip_safe=False,
    test_suite='zope.mkzeoinstance.tests.test_suite',
    entry_points = {
        'console_scripts': [
         'mkzeoinstance = zope.mkzeoinstance:main',
         ],
    },
)
