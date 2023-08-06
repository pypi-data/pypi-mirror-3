#!/usr/bin/env python

"""
setup.py script

Made with mkpkg.py_.

.. _mkpkg.py: http://www.tummy.com/journals/entries/jafo_20100302_003614
"""

__docformat__ = "restructuredtext en"

import os
import sys

from setuptools import setup

import info

setup(name = info.package,
      author = info.author,
      author_email = info.email,
      url = info.url,
      version = info.release,
      license = 'LICENSE.txt',
      description = info.description,
      long_description = open('README.txt').read(),
      classifiers = [
            'Development Status :: 4 - Beta',
            'Environment :: MacOS X :: Aqua',
            'Intended Audience :: Developers',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Natural Language :: English',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Topic :: Scientific/Engineering :: Visualization',
         ],
      install_requires = ["distribute", "matplotlib >= 0.99.1.1"],
      packages = [info.package],
      package_dir = {info.package: info.package},
      )
