.. pygmyplot documentation master file, created by
   sphinx-quickstart on Wed Feb 29 11:59:29 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

============
 pygmyplot
============


Introduction
============

Pygmyplot is a simplified wrapper around matplotlib_, designed to
make it easier to embed specific types of matplotlib plots
into Tkinter_ applications while retaining matplotlib
levels of configurability.
The idea behind pygmyplot is similar to that
of `python megawidgets (PMW)`_, although the interface to pygmyplot
is not intended to be similar to PMW.
The four types of plots currently supported by pygmyplot are:

* X-Y Plots
* Scatter Plots
* Histograms
* Heat Maps


.. _matplotlib: http://matplotlib.sourceforge.net/
.. _Tkinter: http://wiki.python.org/moin/TkInter
.. _`python megawidgets (PMW)`: http://pmw.sourceforge.net/


Changes
=======

- 0.2.11rc
    * reformatted some documentation, improved examples,
      added `heat_2d`_ example, and added example images
    * added __version__ attribute
    * added simplified `heat_2d`_ function
    * corrected bug when heatmaps aren't square

- 0.2.6rc
    * Updated packaging to use distribute_, which allows for
      proper handling of dependencies with PyPI


- 0.2.2rc
    * Fixed bug with heatmap labels

- From 0.2.0
    * Solidified public API for distribution
    * Created documentation in sphinx_
    * Added cushion for scatter: better limits for scatter plots.

.. _distribute: http://packages.python.org/distribute/
.. _sphinx: http://sphinx.pocoo.org/


API Documentation
=================

Overview
--------

At present, pygmyplot has four stable convenience functions as part
of the API. These functions take minimal arguments to produce
plots and return instances of ``MyPlot`` subclasses (e.g. ``MyXYPlot``)
through which the matplotlib API is accessible. Because of this
accessibility, pygmyplot plots are as configurable as matplotlib
plots.

Although ``MyPlot`` subclasses are defined for each type of plot,
these classes are not presently part of the official pygmyplot
API, so use of these classes directly is not yet supported and
may affect the forward-compatibility of your code.

Several examples_ of pygmyplot usage follow descriptions
of the `convenience functions`_.



Convenience Functions
---------------------

The four convenience functions currently in the official
pygmyplot API are:

* ``xy_plot()``
* ``scatter()``
* ``histogram()``
* ``heat_2d()``
* ``xy_heat()``

In all four functions, the ``master`` keyword argument designates
the Tkinter widget that serves as the container for the resulting
plot. Use of the ``master`` keyword argument is given below in the
Examples_. Other keyword arguments for these functions will be documented in the future.

.. autofunction:: pygmyplot.xy_plot

.. autofunction:: pygmyplot.scatter

.. autofunction:: pygmyplot.histogram

.. autofunction:: pygmyplot.heat_2d

.. autofunction:: pygmyplot.xy_heat


Plots
-----

Plots are instances of ``MyPlot`` subclasses. The most useful attribute
of plots is the ``axes`` attribute, which exposes the `matplotlib.axes`_
API. See the `X-Y Plot` example for how the ``axes`` attribute is
accessed and used to modify the appearance of the plot.

.. _`matplotlib.axes`: http://matplotlib.sourceforge.net/api/axes_api.html



Examples
========

The following examples are *complete* Tkinter programs,
so may look complicated. However,
only one or two lines in each example go to constructing the
actual plot. To see the results, just cut-and-paste an example
into a python interactive interpreter or make a ``.py`` file
and run it as a python script (e.g. ``python xyplot_example.py``).

Note that you will need matplotlib installed.


X-Y Plot
--------

Here is an example that puts an x-y plot in a toplevel window::

  import Tkinter as TK
  import pygmyplot
  tk = TK.Tk()
  tk.title("My Plot")
  x, y = ([1, 2, 3, 4, 5, 6], [1, 4, 8, 16, 32, 64])
  p = pygmyplot.xy_plot(x, y, 'ro-', master=tk)
  p.axes.set_ylabel('ordinate')
  TK.Button(tk, text="Quit", command=tk.destroy).pack()
  tk.mainloop()


.. image:: xy_plot.png
   :scale: 50
   :alt: Image of X-Y Plot


Scatter and Histogram Combo
---------------------------

Here, both a scatter plot and a histogram populate the same
toplevel window::

  import random
  import Tkinter as TK
  import pygmyplot
  tk = TK.Tk()
  tk.title("Scatter and Histogram")
  data = [random.normalvariate(10, 5) for i in range(100)]
  pygmyplot.scatter(sorted(data[:50]), sorted(data[50:]), master=tk)
  pygmyplot.histogram(data, master=tk, bins=10)
  TK.Button(tk, text="Quit", command=tk.destroy).pack()
  tk.mainloop()

.. image:: scatter-hist.png
   :scale: 50
   :alt: Image of Scatter and Histogram Plot Combo


Heatmaps
--------

heat_2d
~~~~~~~

This is a very simple example of a heatmap using the `heat_2d`
function. See `xy_heat`_ for a more elaborate heatmap. Note
that keyword arguments for both work identically, except
that the ``heat_up`` and ``coarsen`` keyword arguments are not
accepted for `heat_2d`.

::

  import numpy
  import Tkinter as TK
  import pygmyplot
  tk = TK.Tk()
  tk.title("Simple Heatmap")
  ary = numpy.arange(20).reshape((5,4))
  hm = pygmyplot.heat_2d(ary, master=tk)
  TK.Button(tk, text="Quit", command=tk.destroy).pack()
  tk.mainloop()

.. image:: heat_2d.png
   :scale: 50
   :alt: Image of a 2D Heatmap


xy_heat
~~~~~~~

Here is an example of a heatmap in a toplevel window.
Note that the coordinate and value corresponding to the
central position, ``(2, 3)``, is popped, leaving it
undefined and thus filled with the implicit background
color (white in this example).
Also note that the ``heat_up`` is a fraction (``0.5``), giving the
map more dynamic range in color, but reducing the
contrast of the positions colored
in the background color with the rest of the map.
Finally, the value of the ``cmap`` option is ``cool``, which is
a `Matplotlib colormap`_. Other colormaps can be specified to improve
contrast or appearance.

.. _`Matplotlib colormap`: http://www.scipy.org/Cookbook/Matplotlib/Show_colormaps

::

  import random
  import Tkinter as TK
  import pygmyplot
  tk = TK.Tk()
  tk.title("A Heatmap")
  # make some data
  coords = []
  vals = []

  for i in xrange(5):
    # x coordinate is in the second dimension of an array (!)
    for j in xrange(7):
      rnum = random.normalvariate(10, 5)
      coords.append((i, j))
      vals.append(rnum)

  idx_to_pop = coords.index((2, 3))
  coords.pop(idx_to_pop)
  vals.pop(idx_to_pop)
  hm = pygmyplot.xy_heat(coords, vals, heat_up=0.5,
                         figsize=(4, 3.5),
                         xlabs=["A", "B", "C", "D", "E"],
                         ylabs=["i", "j", "k", "l", "m", "n", "o"],
                         cmap="cool",
                         master=tk)
  TK.Button(tk, text="Quit", command=tk.destroy).pack()
  tk.mainloop()


.. image:: xy_heat.png
   :scale: 50
   :alt: Image of an XY Heatmap


.. Contents:

.. .. toctree::
      :maxdepth: 2



.. Indices and tables
   ==================

.. * :ref:`genindex`
   * :ref:`modindex`
   * :ref:`search`

