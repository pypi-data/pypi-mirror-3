#!/usr/bin/env python

"""
setup.py script

Made with mkpkg.py_.

.. _mkpkg.py: http://www.tummy.com/journals/entries/jafo_20100302_003614
"""

__docformat__ = "restructuredtext en"

from sys import version

from setuptools import setup

setup(name = 'pygmyplot',
      #############################
      # NOTE change version _init_#
      version = '0.2.6rc',        # <=== change _init_
      #############################
      long_description = open('README.txt').read(),
      author = 'James C. Stroud',
      author_email = 'jstroud@mbi.ucla.edu',
      url = 'pygmyplot.bravais.net',
      license = 'LICENSE.txt',
      description = 'Matplotlib wrapper plotting library',
      # platform = "OS Independent",
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
      packages = ['pygmyplot'],
      package_dir = {'pygmyplot': 'src/pygmyplot'},
      )
