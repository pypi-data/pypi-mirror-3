#! /usr/bin/env python

"""
pygmyplot: A matplotlib wrapper plotting library.
Copyright (C) 2012  James C. Stroud
All rights reserved.
"""

import os

try:
  import _version
  __version__ = _version.__version__
except ImportError:
  __version__ = None


from pygmyplotlib import *

__all__ = ["xy_plot", "scatter", "histogram", "heat_2d", "xy_heat"]
