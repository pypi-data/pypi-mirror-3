#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Wheel tension visualization methods."""

__author__ = "Kris Andersen"
__email__ = "kris@biciworks.com"
__copyright__ = u"Copyright © 2012 Kris Andersen"
__license__ = "GPLv3"

import numpy as np

def plot_tension(axes, kgf, target, accuracy, i=0):
    """
    Polar plot of tension data.

    :Parameters:
      - `axes`: Matplotlib axes
      - `kgf`: Tension [kgf]
      - `target`: Target tension [kgf]
      - `accuracy`: Target accuracy [0.0, 1.0]
      - `i`: Wheel side index (i = 0 or 1)
    """

    color = ["m", "b"]
    label = ["Left", "Right"]

    n = len(kgf)
    avg_kgf = np.mean(kgf)
    theta = np.linspace(0.0, 2.0*np.pi, 2*n + 1)[i:-1:2]

    # plot data points
    for angle, r in zip(theta, kgf):
        if r > target*(1.0 + accuracy) or r < target*(1.0 - accuracy):
            axes.plot(angle, r, "rs")
        else:
            axes.plot(angle, r, "o", color=color[i])

    # plot line (guide for the eye)
    theta = np.append(theta, theta[0] + 2.0*np.pi)
    kgf = np.append(kgf, kgf[0])
    axes.plot(theta, kgf, "-", color=color[i], label=label[i])

    # plot average tension
    theta = np.linspace(0.0, 2.0*np.pi)
    r = np.mean(kgf)*np.ones(len(theta))
    axes.plot(theta, r, "--", color=color[i])

    axes.legend(bbox_to_anchor=(1.125, 0.025))

def plot_valid_range(axes, target, accuracy):
    """
    Plot acceptable (valid) tension range.

    :Parameters:
      - `axes`: Matplotlib axes
      - `target`: Target tension [kgf]
      - `accuracy`: Target accuracy [0.0, 1.0]
    """

    axes.bar(0.0, 2.0*accuracy*target, width=2.0*np.pi,
             bottom=target*(1.0 - accuracy), color="g", alpha=0.25)

def plot_ticks(axes, nspoke):
    """
    Number spoke tick labels.

    :Parameters:
      - `axes`: Matplotlib axes
      - `nspoke`: Number of spokes
    """

    theta = np.linspace(0.0, 2.0*np.pi, nspoke+1)[:-1]
    axes.set_xticks(theta)
    axes.set_xticklabels(np.arange(1, len(theta) + 1))

def plot(axes, kgf0, kgf1, target, accuracy):
    """
    Polar plot of wheel tension data.

    :Parameters:
      - `axes`: Matplotlib axes
      - `kgf0`: Tension for spoke set 0 [kgf]
      - `kgf1`: Tension for spoke set 1 [kgf]
      - `target`: Target tension [kgf]
      - `accuracy`: Target accuracy [0.0, 1.0]
    """

    plot_tension(axes, kgf0, target, accuracy, i=0)
    plot_tension(axes, kgf1, target, accuracy, i=1)
    plot_valid_range(axes, target, accuracy)
    plot_ticks(axes, len(kgf0) + len(kgf1))
    axes.set_xlabel("Spoke")
    axes.grid(True)
