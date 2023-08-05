#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Wheelwright: Bicycle wheel tension visualizer.

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

                                -----

Units: Tensions are given in kilograms-force (kgf), a non-standard
(non-SI) unit of force common in the bicycle industry. 1 kgf = 9.81
N."""

__author__ = "Kris Andersen"
__email__ = "kris@biciworks.com"
__copyright__ = u"Copyright © 2012 Kris Andersen"
__license__ = "GPLv3"
__version__ = "0.1.3"

import sys
import os
import numpy as np
import pylab
import pickle

from PyQt4 import QtCore, QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

import report
from canvas import WheelCanvas, TMCanvas
from tm1 import TM1, spoke_codes

NSPOKE_MAX = 36  # maximum number of spokes (must be even)

class Wheelwright(QtGui.QMainWindow):
    """Wheelwright PyQt4 GUI."""

    def __init__(self, parent=None):
        """
        GUI constructor.

        :Parameters:
          - `parent`: Parent widget
        """

        super(Wheelwright, self).__init__(parent)

        self.setWindowTitle("Wheelwright")
        self.filename = None  # no open file on start

        def label(text, alignment=QtCore.Qt.AlignRight):
            """Label maker."""
            label = QtGui.QLabel(text)
            label.setAlignment(alignment)
            return label

        #
        # actions
        #

        open_action = QtGui.QAction("&Open", self)
        open_action.setShortcut("Ctrl+O")
        self.connect(open_action, QtCore.SIGNAL("triggered()"), self.open)

        save_action = QtGui.QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        self.connect(save_action, QtCore.SIGNAL("triggered()"), self.save)

        report_action = QtGui.QAction("Generate &Report", self)
        report_action.setShortcut("Ctrl+R")
        self.connect(report_action, QtCore.SIGNAL("triggered()"), self.report)

        self.tm_action = QtGui.QAction("Show Tension Meter &Calibration", self)
        self.tm_action.setCheckable(True)
        self.connect(self.tm_action, QtCore.SIGNAL("triggered()"), self.calibration)

        about_action = QtGui.QAction("&About", self)
        about_action.setShortcut("Ctrl+A")
        self.connect(about_action, QtCore.SIGNAL("triggered()"), self.about)

        exit_action = QtGui.QAction("&Quit", self)
        exit_action.setShortcut("Ctrl+Q")
        self.connect(exit_action, QtCore.SIGNAL("triggered()"), self.close)

        #
        # menus
        #

        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(exit_action)

        tools_menu = self.menuBar().addMenu("&Tools")
        tools_menu.addAction(report_action)

        view_menu = self.menuBar().addMenu("&View")
        view_menu.addAction(self.tm_action)

        help_menu = self.menuBar().addMenu("&Help")
        help_menu.addAction(about_action)

        #
        # information displays
        #

        self.average_tm0 = QtGui.QLabel()
        self.average_tm1 = QtGui.QLabel()
        self.average_kgf0 = QtGui.QLabel()
        self.average_kgf1 = QtGui.QLabel()

        # matplotlib canvas
        self.wheel_canvas = WheelCanvas(width=6, height=6, dpi=100, polar=True)

        #
        # main widgets
        #

        self.code = QtGui.QComboBox()
        self.code.addItems(spoke_codes)
        self.code.setCurrentIndex(4)
        self.connect(self.code, QtCore.SIGNAL("currentIndexChanged(int)"), self.update_code)

        self.target = QtGui.QDoubleSpinBox()
        self.target.setRange(0.0, 200.0)
        self.target.setDecimals(1)
        self.target.setSingleStep(5.0)
        self.target.setValue(110.0)
        self.connect(self.target, QtCore.SIGNAL("valueChanged(double)"), self.update_target)

        self.accuracy = QtGui.QDoubleSpinBox()
        self.accuracy.setRange(0.0, 1.0)
        self.accuracy.setDecimals(2)
        self.accuracy.setSingleStep(0.05)
        self.accuracy.setValue(0.2)
        self.connect(self.accuracy, QtCore.SIGNAL("valueChanged(double)"), self.update_accuracy)

        self.nspoke = QtGui.QSpinBox()
        self.nspoke.setRange(2, NSPOKE_MAX / 2)
        self.nspoke.setSingleStep(1)
        self.nspoke.setValue(16)
        self.connect(self.nspoke, QtCore.SIGNAL("valueChanged(int)"), self.update_nspoke)

        #
        # spoke tension widgets
        #

        self.t0 = []
        self.t1 = []
        for n in range(0, NSPOKE_MAX):
            t = QtGui.QDoubleSpinBox()
            t.setRange(0.0, 30.0)
            t.setValue(15.0)
            t.setDecimals(1)
            if n >= 2*self.nspoke.value():
                t.setEnabled(False)
            self.connect(t, QtCore.SIGNAL("valueChanged(double)"), self.update_tension)
            if n % 2 == 0:
                self.t0.append(t)
            else:
                self.t1.append(t)

        #
        # widget layout
        #

        header = QtGui.QHBoxLayout()
        header.addWidget(label("Left Spokes", QtCore.Qt.AlignCenter))
        header.addWidget(label("Right Spokes", QtCore.Qt.AlignCenter))

        spoke_grid = QtGui.QGridLayout()
        for n, widget in enumerate(self.t0):
            spoke_grid.addWidget(label(str(2*n + 1)), n, 0)
            spoke_grid.addWidget(widget, n, 1)
        for n, widget in enumerate(self.t1):
            spoke_grid.addWidget(label(str(2*n + 2)), n, 2)
            spoke_grid.addWidget(widget, n, 3)
        spoke_grid.addWidget(label("Average (TM-1)"), NSPOKE_MAX/2, 0)
        spoke_grid.addWidget(label("Average (TM-1)"), NSPOKE_MAX/2, 2)
        spoke_grid.addWidget(label("Average (kgf)"), NSPOKE_MAX/2+1, 0)
        spoke_grid.addWidget(label("Average (kgf)"), NSPOKE_MAX/2+1, 2)
        spoke_grid.addWidget(self.average_tm0, NSPOKE_MAX/2, 1)
        spoke_grid.addWidget(self.average_tm1, NSPOKE_MAX/2, 3)
        spoke_grid.addWidget(self.average_kgf0, NSPOKE_MAX/2+1, 1)
        spoke_grid.addWidget(self.average_kgf1, NSPOKE_MAX/2+1, 3)

        table = QtGui.QVBoxLayout()
        table.addWidget(label("Spoke Tensions", QtCore.Qt.AlignCenter))
        table.addLayout(header)
        table.addLayout(spoke_grid)

        main = QtGui.QGridLayout()
        main.addWidget(self.code, 0, 0)
        main.addWidget(label("Spoke Type", QtCore.Qt.AlignLeft), 0, 1)
        main.addWidget(self.target, 1, 0)
        main.addWidget(label("Target Tension (kgf)", QtCore.Qt.AlignLeft), 1, 1)
        main.addWidget(self.accuracy, 2, 0)
        main.addWidget(label("Target Accuracy", QtCore.Qt.AlignLeft), 2, 1)
        main.addWidget(self.nspoke, 3, 0)
        main.addWidget(label("Number of Spokes (per side)", QtCore.Qt.AlignLeft), 3, 1)

        panel = QtGui.QVBoxLayout()
        panel.addLayout(main)
        panel.addWidget(self.wheel_canvas)

        columns = QtGui.QHBoxLayout()
        columns.addLayout(table)
        columns.addLayout(panel)

        main_window = QtGui.QWidget()
        main_window.setLayout(columns)
        self.setCentralWidget(main_window)

        #
        # initialization and updates
        #

        self.tm = TM1(self.code.currentIndex())
        self.update_code()
        self.update_tension()

    def open(self):
        """Open binary data file."""

        self.filename = QtGui.QFileDialog.getOpenFileName(self)
        try:
            data = pickle.load(open(self.filename, "rb"))
            self.code.setCurrentIndex(data["code"])
            self.target.setValue(data["target"])
            self.accuracy.setValue(data["accuracy"])
            self.nspoke.setValue(data["nspoke"])
            for i, t in enumerate(data["t0"]):
                self.t0[i].setValue(t)
            for i, t in enumerate(data["t1"]):
                self.t1[i].setValue(t)
            self.setWindowTitle("Wheelwright : %s" % self.filename)
        except:
            box = QtGui.QMessageBox()
            box.setText("Error: Unable to open file")
            box.setInformativeText(self.filename)
            box.exec_()
            self.filename = None

    def save(self):
        """Save binary data file."""

        t0 = [t.value() for t in self.t0]
        t1 = [t.value() for t in self.t1]
        data = {"code": self.code.currentIndex(),
                "target": self.target.value(),
                "accuracy": self.accuracy.value(),
                "nspoke": self.nspoke.value(),
                "t0": t0,
                "t1": t1}

        if self.filename is not None:
            pickle.dump(data, open(self.filename, "wb"), protocol=2)
        else:
            try:
                self.filename = QtGui.QFileDialog.getSaveFileName(self)
                pickle.dump(data, open(self.filename, "wb"), protocol=2)
                self.setWindowTitle("Wheelwright : %s" % self.filename)
            except:
                box = QtGui.QMessageBox()
                box.setText("Error: Unable to save")
                box.setInformativeText(self.filename)
                box.exec_()

    def calibration(self):
        """Open tension meter calibarion window."""

        if self.tm_action.isChecked():
            self.tm_window = TMWindow(parent=self)
            self.tm_window.update()
            self.tm_window.setFocus()
        else:
            self.tm_window.close()
            del self.tm_window
            self.setFocus()

    def about(self):
        """About message box."""

        about = "Version %s\n%s\n\n%s" % (__version__, __copyright__, __doc__)
        box = QtGui.QMessageBox()
        box.setText("Wheelwright")
        box.setInformativeText(about)
        box.exec_()

    def report(self):
        """Write report log."""

        filename = QtGui.QFileDialog.getSaveFileName(self, "Save Report As...")
        figure = "%s.png" % (filename)
        self.wheel_canvas.savefig(figure, dpi=300)
        t0 = [t.value() for t in self.t0[:self.nspoke.value()]]
        t1 = [t.value() for t in self.t1[:self.nspoke.value()]]
        kgf0 = self.tm.convert_to_kgf(t0)
        kgf1 = self.tm.convert_to_kgf(t1)
        report.pdf(self.code.currentIndex(), self.target.value(), self.accuracy.value(), kgf0, kgf1, figure, filename)
        os.unlink(figure)

    def update_code(self):
        """Update spoke code."""

        self.tm = TM1(self.code.currentIndex())
        self.update_tension()
        if self.tm_action.isChecked():
            self.tm_window.update()

    def update_target(self):
        """Update target tension."""

        self.update_tension()
        if self.tm_action.isChecked():
            self.tm_window.update()

    def update_accuracy(self):
        """Update target accuracy."""

        self.update_tension()
        if self.tm_action.isChecked():
            self.tm_window.update()

    def update_nspoke(self):
        """Update number of spokes."""

        for i, n in enumerate(np.arange(0, NSPOKE_MAX, 2)):
            if n < 2*self.nspoke.value():
                self.t0[i].setEnabled(True)
                self.t1[i].setEnabled(True)
            else:
                self.t0[i].setEnabled(False)
                self.t1[i].setEnabled(False)
        self.update_tension()

    def update_tension(self):
        """Update wheel tension canvas."""

        t0 = [t.value() for t in self.t0[:self.nspoke.value()]]
        t1 = [t.value() for t in self.t1[:self.nspoke.value()]]
        kgf0 = self.tm.convert_to_kgf(t0)
        kgf1 = self.tm.convert_to_kgf(t1)
        self.average_tm0.setText("%.1f" % np.mean(t0))
        self.average_tm1.setText("%.1f" % np.mean(t1))
        self.average_kgf0.setText("%.1f" % np.mean(kgf0))
        self.average_kgf1.setText("%.1f" % np.mean(kgf1))
        self.wheel_canvas.plot_figure(kgf0, kgf1, self.target.value(), self.accuracy.value())

class TMWindow(QtGui.QDialog):
    """Tension meter calibration window."""

    def __init__(self, parent):
        """
        Window constructor.

        :Parameters:
          - `parent`: Parent widget
        """

        super(TMWindow, self).__init__(parent)
        self.parent = parent
        self.setWindowTitle("Tension Meter Calibration")
        self.tm_canvas = TMCanvas(width=6, height=4, dpi=100)

        box = QtGui.QVBoxLayout()
        box.addWidget(self.tm_canvas)
        self.setLayout(box)
        self.show()

    def closeEvent(self, event):
        """Close calibration window."""

        self.parent.tm_action.setChecked(False)
        self.close()

    def update(self):
        """Update calibration window canvas."""

        self.tm_canvas.plot_figure(self.parent.tm, self.parent.target.value(), self.parent.accuracy.value())

def main():
    """Start Wheelwright application."""

    app = QtGui.QApplication(sys.argv)
    w = Wheelwright()
    w.show()
    w.raise_()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
