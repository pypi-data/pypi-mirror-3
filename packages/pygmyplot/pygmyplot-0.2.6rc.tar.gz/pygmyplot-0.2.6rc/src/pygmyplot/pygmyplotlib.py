#! /usr/bin/env python

"""
pygmyplot: A matplotlib wrapper plotting library.
Copyright (C) 2012  James C. Stroud

Contact: http://www.jamesstroud.com/contact-form

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import random

from itertools import izip
from Tkinter import *

import numpy

import matplotlib
matplotlib.use("Tkagg")

import pylab
from matplotlib.backends.backend_tkagg \
     import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.image import AxesImage
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.font_manager import fontManager, FontProperties

__version__ = "0.2.0"

LEGEND_LOCS = {
                'best'         : 0,   0: 0,
                'upper right'  : 1,   1: 1,
                'upper left'   : 2,   2: 2,
                'lower left'   : 3,   3: 3,
                'lower right'  : 4,   4: 4,
                'right'        : 5,   5: 5,
                'center left'  : 6,   6: 6,
                'center right' : 7,   7: 7,
                'lower center' : 8,   8: 8,
                'upper center' : 9,   9: 9,
                'center'       : 10, 10:10
              }

def limits(a, f):
  if not isinstance(a, numpy.ndarray):
    a = numpy.array(a)
  min_a = a.min()
  max_a = a.max()
  delta = 0.1 * (max_a - min_a)
  minn = min_a - delta
  maxx = max_a + delta
  return (minn, maxx)


def ticklabels(n, roots):
  if roots is None:
    roots = range(n)
    modulus = n
  else:
    modulus = len(roots)
  blocks, r = divmod(n, modulus)
  if r:
    raise ValueError, 'n should be divisible by len(roots).'
  labels = []
  for i in xrange(blocks):
    for root in roots:
      if blocks > 1:
        labels.append("%d-%s" % (i+1, root))
      else:
        labels.append(root)
  positions = range(-1, modulus * blocks + 1)
  labels = [''] + labels + ['']
  return positions, labels

def xticklabels(n):
  labels = ["", ""]
  labels[1:1] = [str(i) for i in xrange(1, n+1)]
  positions = range(-1, n+1)
  return positions, labels

def normalize(ary):
  delta = float(numpy.max(ary) - numpy.min(ary))
  ary = ary - numpy.min(ary)
  ary = ary / delta
  return ary

# one initopts() to rule them all
def initopts(cls, options):
  class OptionError(Exception): pass
  def _f(parsed, cls, options):
    # this might be clunky because no possibility of no defaults
    if hasattr(cls, "defaults"):
      for name, value in cls.defaults.items():
        value = options.pop(name, value)
        parsed.setdefault(name, value)
    for base in cls.__bases__:
      _f(parsed, base, options)
  parsed = {}
  _f(parsed, cls, options)
  if options:
    s = "" if len(options) == 1 else "s"
    badopts = ", ".join(options.keys())
    msg = "No such option%s: %s" % (s, badopts)
    raise OptionError, msg
  return parsed

def make_move_axes_x(axes, amt, canvas):
  def _f(e=None):
    p = axes.get_position()
    p = [p[0] + amt] + p[1:]
    axes.set_position(p, which='both')
    canvas.draw()
  return _f

class MyPlot(object):
  defaults = {"master":None, "window_title":"My Plot",
              "figsize":(6, 3.708), "dpi":100,
              "sibling":None, "subplot":(1,1,1),
              "title":None}
  def __init__(self, **options):
    options = initopts(self.__class__, options)
    self.options = options
    self.sibling = options['sibling']
    sibling = self.sibling
    if sibling is None:
      if options['master'] is None:
        self.master = Toplevel()
        self.master.title(options['window_title'])
      else:
        self.master = options['master']
      self.window = self.master.winfo_toplevel()
      self.frame = Frame(self.master)
      self.frame.pack(fill=BOTH, expand=YES)
      self.figure = Figure(figsize=options['figsize'],
                           dpi=options['dpi'])
      self.canvas = FigureCanvasTkAgg(self.figure, master=self.frame)
      self.toolbar = NavigationToolbar2TkAgg(self.canvas, self.frame)
      self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=YES)
      self.canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=YES)
    else:
      self.master = sibling.master
      self.frame = sibling.frame
      self.figure = sibling.figure
      self.toolbar = sibling.toolbar
      self.canvas = sibling.canvas
  def pack(self, *args, **kwargs):
    self.frame.pack(*args, **kwargs)

class MyHistogram(MyPlot):
  defaults = {"title":"My Histogram", "figsize":(4.5, 3)}
  def __init__(self, data, **options):
    hopts = """
            bins range normed cumulative bottom histtype
            align orientation rwidth log
            """.split()
    hopts = dict((k, options.pop(k)) for k in hopts if k in options)
    data = numpy.array(data)
    self.data = data
    MyPlot.__init__(self, **options)
    self.axes = self.figure.add_subplot(*self.options['subplot'])
    self.pdf, self.bins, self.patches = self.axes.hist(data, **hopts)
    self.canvas.show()

class MyHeatmap(MyPlot):
  defaults = {"cmap":None, "flip_vert":False,
              "ylabel":None, "xlabs":None, "ylabs":None,
              "label_fontsize":None, "show_colorbar":True}
  def __init__(self, data, **options):
    data = numpy.array(data)
    self.data = data
    normalized = normalize(data)
    self.normalized = normalized
    MyPlot.__init__(self, **options)
    options = self.options
    cmap = options['cmap']
    if cmap is not None:
      cmap = getattr(pylab.cm, cmap)
    if options['flip_vert']:
      mapdata = normalized[::-1]
    else:
      mapdata = normalized
    self.mapdata = mapdata
    rows, cols = numpy.shape(mapdata)
    self.axes = self.figure.add_subplot(*options['subplot'])
    self.im = self.axes.imshow(mapdata,
                               interpolation="nearest",
                               cmap=cmap,
                               vmin=0.0, vmax=1.0)
    if options['ylabel'] is not None:
      self.axes.set_ylabel(options['ylabel'])
    xpositions, xlabels = ticklabels(cols, options['xlabs'])
    self.axes.set_xticks(xpositions)
    if options['xlabs'] is None:
      self.axes.set_xticklabels([])
    else:
      self.axes.set_xticklabels(xlabels,
                                fontsize=options['label_fontsize'],
                                family='monospace')
    ypositions, ylabels = ticklabels(rows, options['ylabs'])
    if options['ylabs'] is None:
      self.axes.set_yticklabels([])
    else:
      if options['flip_vert']:
        ypositions = ypositions[::-1]
      self.axes.set_yticklabels(ylabels,
                                fontsize=options['label_fontsize'],
                                family='monospace')
    self.axes.set_yticks(ypositions)
    self.axes.set_xlim((-1, cols))
    self.axes.set_ylim((-1, rows))
    if options['show_colorbar']:
      self.colorbar = self.figure.colorbar(self.im,
                                           ax=self.axes,
                                           fraction=0.05)
    else:
      self.colorbar = None
    if options['title'] is not None:
      self.axes.set_title(options['title'])
    self.canvas.show()
  def __getitem__(self, i):
    return self.data[i]

class MyScatter(MyPlot):
  defaults = {"color":"b", "s":20}
  def __init__(self, **options):
    MyPlot.__init__(self, **options)
    options = self.options
    self.axes = self.figure.add_subplot(*options['subplot'])
    self.canvas.show()
  def plot(self, *args, **kwargs):
    line = self.axes.scatter(*args, **kwargs)
    self.canvas.show()
    return line

class MyXYPlot(MyPlot):
  defaults = {"color":"b"}
  def __init__(self, **options):
    MyPlot.__init__(self, **options)
    options = self.options
    self.axes = self.figure.add_subplot(*options['subplot'])
    self.canvas.show()
  def plot(self, *args, **kwargs):
    if ("yerr" in kwargs) or ("xerr" in kwargs):
      if len(args) == 1:
        args = [numpy.arange(len(args[0])), args[0]]
      line = self.axes.errorbar(*args, **kwargs)
    else:
      line = self.axes.plot(*args, **kwargs)
    self.canvas.show()
    return line

def scatter(x, y, **kwargs):
  """
  Returns an instance of `MyXYPlot` with the data in `x` and `y`
  plotted. This function mostly mirrors the behavior of
  `matplotlib.axes.scatter`_.

  .. _`matplotlib.axes.scatter`: http://matplotlib.sourceforge.net/api/axes_api.html#matplotlib.axes.Axes.scatter
  """
  cushion = kwargs.pop('cushion', 0.1)
  plt = MyScatter(**kwargs)
  x_lo, x_hi = limits(x, cushion)
  y_lo, y_hi = limits(y, cushion)
  plt.axes.set_xlim(x_lo, x_hi)
  plt.axes.set_ylim(y_lo, y_hi)
  plt.plot(x, y)
  return plt

def xy_heat(coords, vals, coarsen=None, heat_up=None, **kwargs):
  """
  Returns a heat-map (``MyHeatMap`` intance) with the values
  (``vals``) plotted at the positions indicated by ``coords``,
  which is organized as pairs containing (x,y) positions, e.g::

    coords = [(0, 0), (0, 1), (1, 0), (1, 2)]
    vals = [5, 2, 4, 3]

  For each (x,y) coordinate of data, the corresponding numerical
  value is plotted on the heat map at that position.
  All unfilled positions take the minimum value 
  of the data.

  The grid is coarsened by the pair (e.g. a 2-tuple)
  ``coarsen`` relative to the (x,y) positions if it is provided.
  This makes it possible for the (x,y) postions to have
  a multiplicity (e.g. 0, 4, 8 versus 0, 1, 2 in x, etc.).
  Thus, ``coarsen`` should divide evenly into the coordinates.

  For example if ``coarsen`` is ``(3, 2)``, then the coordinates could
  be::

    [(0,0), (0,2), (0,4), (3,0), (3,2), (3,4), (9,0), (9,2), (9,4)]

  If the ``heat_up`` keyword argument is provided, then the data is
  heated up by that much to make the unfilled values
  have more contrast.
  This has the side-effect of reducing the range of
  colors in the map.

  The ``**kwargs`` are passed directly to the ``MyHeatMap`` initializer.
  """
  if not isinstance(coords, numpy.ndarray):
    coords = numpy.array(coords)
  if not isinstance(vals, numpy.ndarray):
    vals = numpy.array(vals)
  if heat_up is None:
    heat_up = 1.0
  if coarsen is None:
    x_factor = 1.0
    y_factor = 1.0
  else:
    x_factor, y_factor = coarsen
  minimum = vals.min()
  maximum = vals.max()
  xs, ys = coords.T
  min_x = xs.min()
  max_x = xs.max()
  min_y = ys.min()
  max_y = ys.max()
  width = 1 + (max_x - min_x)/x_factor
  height = 1 + (max_y - min_y)/x_factor
  map_data = numpy.empty((width, height), numpy.float)
  # makes the unfilled rectangles significantly darker
  value = minimum - ((maximum - minimum) * heat_up)
  map_data.fill(value)
  # this loop should be numpyified
  for point, value in izip(coords, vals):
    x, y = point
    col = (x - min_x)/x_factor
    row = (y - min_y)/y_factor
    map_data[row, col] = value
  if 'xlabs' not in kwargs:
    xlabs = [str((x*x_factor)+min_x) for x in numpy.arange(width)]
    kwargs['xlabs'] = xlabs
  if 'ylabs' not in kwargs: 
    ylabs = [str((y*y_factor)+min_y) for y in numpy.arange(height)]
    kwargs['ylabs'] = ylabs
  hm = MyHeatmap(map_data, **kwargs)
  return hm

def xy_plot(x, *args, **kwargs):
  """
  Returns an instance of `MyXYPlot` with the data in `x` and
  `*args` (if supplied) plotted. This function mostly mirrors the
  behavior of `pyplot.plot`_.

  .. _`pyplot.plot`: http://matplotlib.sourceforge.net/api/pyplot_api.html#matplotlib.pyplot.plot
  """
  p = MyXYPlot(**kwargs)
  p.plot(x, *args)
  return p

def histogram(data, **kwargs):
  """
  Returns an instance of `MyHistogram` with the `data` (a sequence)
  binned and plotted.

  Use the `bins` keword argument to control the number of bins.
  """
  return MyHistogram(data, **kwargs)

def fontprop(*args, **kwargs):
  return FontProperties(*args, **kwargs)

def main():
  """
  The testing function.
  """
  tk = Tk()
  def doit(root=None):
    mp = MyXYPlot(title='Some Data', master=root)
    mp.plot([1,2,3,4,5], [0, 15, 25, 30, 32.5])
    mp.plot([1,2,3,4,5], list(reversed([0, 15, 25, 30, 32.5])))
  f = Frame(tk)
  f.pack(side=TOP, fill=X, expand=NO)
  b = Button(f, text='Punch the Monkey!', command=lambda :doit())
  b.pack(expand=NO, side=LEFT)
  b = Button(f, text='Punch this Monkey!', command=lambda :doit(tk))
  b.pack(expand=NO, side=LEFT)
  hm_data = []
  for i in xrange(5):
    rnum = random.randint(1,5)
    hm_data.append(range(rnum, rnum+5))
  hm = MyHeatmap(hm_data)
  tk.mainloop()

if __name__ == "__main__":
  main()
