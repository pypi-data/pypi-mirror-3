#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Report generation methods."""

__author__ = "Kris Andersen"
__email__ = "kris@biciworks.com"
__copyright__ = u"Copyright © 2012 Kris Andersen"
__license__ = "GPLv3"

import numpy as np
import datetime
import os
from rst2pdf.createpdf import RstToPdf
from ConfigParser import ConfigParser

import wheel
import wheelwright
import tm1

def pdf(code, tension, accuracy, kgf0, kgf1, figure, filename):
    """
    Write report as PDF file.

    :Parameters:
      - `code`: TM-1 spoke code index
      - `target`: Target tension [kgf]
      - `accuracy`: Target accuracy [0.0, 1.0]
      - `kgf0`: Tension for spoke set 0 [kgf]
      - `kgf1`: Tension for spoke set 1 [kgf]
      - `figure`: Path to spoke tension image filename
      - `filename`: Report output filename
    """

    timestamp = datetime.datetime.now().strftime("%B %d, %Y %I:%M %p")

    # read config file for optional header (e.g., bicycle shop name)
    try:
        c = ConfigParser(allow_no_value=True)
        c.read(["wheelwright.cfg",
                os.path.expanduser("~") + "/wheelwright.cfg",
                os.path.expanduser("~") + "/.wheelwright"])
        header = c.get("Report", "header")
    except:
        header = None

    # report as reStructured text
    report = """
Wheelwright Report
==================

.. figure:: %s
    :align: center

    Spoke tensions: Spokes that have achieved the correct target
    tension for the rim are within the green region.

    | **Spoke Type**: %s
    | **Target Tension**: %.1f kgf
    | **Target Accuracy**: %.0f%%

Spoke Tensions
--------------

   +------------------------------------------+------------------------------------------+
   | Left Spokes                              | Right Spokes                             |
   +-------------------------+----------------+-------------------------+----------------+
   | Number                  | Tension (kgf)  | Number                  | Tension (kgf)  |
   +=========================+================+=========================+================+
""" % (figure, tm1.spoke_codes[code], tension, 100.0*accuracy)

    n = 1
    for x, y in zip(kgf0, kgf1):
        report += "   |%25d|%16.1f|%25d|%16.1f|\n" % (n, x, n + 1, y)
        report += "   +-------------------------+----------------+-------------------------+----------------+\n"
        n += 2

    row = "Average Tension (kgf)"
    report += "   |%25s|%16.1f|%25s|%16.1f|\n" % (row, np.mean(kgf0), row, np.mean(kgf1))
    report += "   +-------------------------+----------------+-------------------------+----------------+\n"

    row = "Standard Deviation (kgf)"
    report += "   |%25s|%16.1f|%25s|%16.1f|\n" % (row, np.std(kgf0), row, np.std(kgf1))
    report += "   +-------------------------+----------------+-------------------------+----------------+\n\n"

    report += ".. footer:: Wheelwright %s | http://biciworks.com/wheelwright/ | %s\n" \
        % (wheelwright.__version__, timestamp)
    if header:
        report += ".. header:: %s\n" % (header)

    RstToPdf(breakside="any", splittables=True).createPdf(text=report, output=filename)
