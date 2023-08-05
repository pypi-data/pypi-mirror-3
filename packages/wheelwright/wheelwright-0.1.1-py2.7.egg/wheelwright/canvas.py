#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Matplotlib figure canvases."""

__author__ = "Kris Andersen"
__email__ = "kris@biciworks.com"
__copyright__ = u"Copyright © 2012 Kris Andersen"
__license__ = "GPLv3"

import pylab
import wheel
from PyQt4 import QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

class Canvas(FigureCanvas):
    """Generic Matplotlib canvas."""

    def __init__(self, width=5, height=4, dpi=100, polar=False, expand=True):
        """
        Canvas constructor.

        :Parameters:
          - `width`: Figure width [inch]
          - `height`: Figure height [inch]
          - `dpi`: Figure resolution [dots per inch]
          - `polar`: Whether to use polar coordinates
        """

        self.figure = pylab.Figure(figsize=(width, height), dpi=dpi)
        #self.figure.subplots_adjust(bottom=0.15)  # enough room to show xlabel on TM-1 plot
        self.axes = self.figure.add_subplot(111, polar=polar)

        super(Canvas, self).__init__(self.figure)
        if expand:
            FigureCanvas.setSizePolicy(self,
                                       QtGui.QSizePolicy.Expanding,
                                       QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def savefig(self, filename, dpi=300):
        """Save figure."""

        self.figure.savefig(filename, dpi=dpi)


class WheelCanvas(Canvas):
    """Wheel tension polar plot canvas."""

    def plot_figure(self, kgf0, kgf1, target, accuracy):
        """
        Polar plot of wheel tension data.

        :Parameters:
          - `axes`: Matplotlib axes
          - `kgf0`: Tension for spoke set 0 [kgf]
          - `kgf1`: Tension for spoke set 1 [kgf]
          - `target`: Target tension [kgf]
          - `accuracy`: Target accuracy [0.0, 1.0]
        """

        self.axes.cla()
        wheel.plot(self.axes, kgf0, kgf1, target, accuracy)
        self.draw()

class TMCanvas(Canvas):
    """TM-1 instrument canvas."""

    def plot_figure(self, tm1, target, accuracy):
        """
        Plot TM-1 calibration data.

        :Parameters:
          - `tm1`: TM-1 instrument object
          - `target`: Target tension [kgf]
          - `accuracy`: Target accuracy [0.0, 1.0]
        """

        self.axes.cla()
        tm1.plot(self.axes, target, accuracy)
        self.draw()
