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
"""Setup for the Acquisition egg package
"""
import os
from setuptools import setup, find_packages

setup(name='zLOG',
      version = '2.12.0',
      url='http://cheeseshop.python.org/pypi/zLOG',
      license='ZPL 2.1',
      description='A general logging facility',
      author='Zope Foundation and Contributors',
      author_email='zope-dev@zope.org',
      long_description="""
This package provides a general logging facility that, at this point,
is just a small shim over Python's logging module.  Therefore, unless
you need to support a legacy package from the Zope 2 world, you're
probably better off using Python's logging module.""",
      
      packages=find_packages('src'),
      package_dir={'': 'src'},

      install_requires=['ZConfig >= 2.9.2'],
      include_package_data=True,
      zip_safe=False,
      )
