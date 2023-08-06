##############################################################################
#
# Copyright (c) Zope Foundation and Contributors.
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
name, version = 'zc.zkzopeserver', '0.3.2'

install_requires = ['setuptools', 'zc.zk', 'zope.server']
extras_require = dict(
    test=['zope.testing', 'zc.zk [static,test]', 'zc.monitor',
          'zc.zservertracelog', 'mock', 'netifaces']
    )

entry_points = """
[paste.server_runner]
main = zc.zkzopeserver:run
"""

from setuptools import setup

def read(path):
    return open(path).read().strip()

setup(
    author = 'Jim Fulton',
    author_email = 'jim@zope.com',
    license = 'ZPL 2.1',

    name = name, version = version,
    long_description=read('src/zc/zkzopeserver/README.txt'),
    description = read('src/zc/zkzopeserver/README.txt').split('\n')[1],
    packages = [name.split('.')[0], name],
    namespace_packages = [name.split('.')[0]],
    package_dir = {'': 'src'},
    install_requires = install_requires,
    zip_safe = False,
    entry_points=entry_points,
    package_data = {name: ['*.txt', '*.test', '*.html']},
    extras_require = extras_require,
    tests_require = extras_require['test'],
    test_suite = name+'.tests.test_suite',
    )
