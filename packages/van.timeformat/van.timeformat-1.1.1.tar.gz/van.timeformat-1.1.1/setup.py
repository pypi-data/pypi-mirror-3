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

import os
from setuptools import setup, find_packages

long_description = (
    '.. contents::\n\n'
    + open(os.path.join('van', 'timeformat', 'README.txt')).read()
    + '\n\n'
    + open(os.path.join('van', 'timeformat', 'zpt.txt')).read()
    + '\n\n'
    + open(os.path.join('CHANGES.txt')).read()
    )

setup(name="van.timeformat",
      version='1.1.1',
      license='ZPL 2.1',
      url='http://pypi.python.org/pypi/van.timeformat',
      author_email='zope-dev@zope.org',
      packages=find_packages(),
      author="Vanguardistas LLC",
      description="Convienience functions for formatting dates/times using zope.i18n and TAL",
      namespace_packages=["van"],
      install_requires = [
          'setuptools',
          'zope.i18n',
          'zope.tales',
          ],
      extras_require = {
          'test': ['van.testing']
      },
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3',
        'Development Status :: 5 - Production/Stable',
        ],
      long_description=long_description,
      include_package_data = True,
      zip_safe = False,
      )
