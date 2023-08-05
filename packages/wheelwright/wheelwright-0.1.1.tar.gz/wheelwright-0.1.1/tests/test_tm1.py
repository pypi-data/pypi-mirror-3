#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test tm1 module routines."""

import pylab
from wheelwright.tm1 import TM1, data_table, spoke_codes

def assert_relerr(x, y, tol):
    """Assert that the relative error is less than tolerance."""
    relerr = abs(x - y) / abs(y)
    if relerr > tol:
        raise AssertionError, "relative error %g > %g" % (relerr, tol)

TOL = 0.02865

def test_fit():
    """Test polynomial fit to TM-1 data table."""

    for code in range(38):
        tm1 = TM1(code)
        if max(tm1.err) > TOL:
            raise AssertionError, "Fit error too large"

def test_convert_to_kgf():
    """Test conversion from TM-1 reading to kilograms-force."""

    for code in range(38):
        tm1 = TM1(code)
        x, y = data_table(code)
        for i, ans in enumerate(y):
            kgf = tm1.convert_to_kgf(x[i])
            assert_relerr(kgf, ans, TOL)

def test_tm1_target():
    """Test determination of TM-1 reading target."""

    target = 110.0
    accuracy = 0.2
    tmin_ans = target*(1.0 - accuracy)
    tmax_ans = target*(1.0 + accuracy)
    for code in range(38):
        tm1 = TM1(code)
        x, y = data_table(code)
        t, tmin, tmax = tm1.tm1_target(target, accuracy)
        if t < min(x) or t > max(x):
            raise AssertionError, "Target TM-1 reading outside of range"
        kgf = tm1.convert_to_kgf(t)
        assert_relerr(kgf, target, 1.0e-12)
        kgf = tm1.convert_to_kgf(tmin)
        assert_relerr(kgf, tmin_ans, 1.0e-12)
        kgf = tm1.convert_to_kgf(tmax)
        assert_relerr(kgf, tmax_ans, 1.0e-12)

# def test_plot():
#     """Visual test of TM-1 data and polynomial fit."""

#     for code in range(38):
#         tm1 = TM1(code)
#         fig = pylab.figure()
#         axes = fig.add_subplot(111)
#         tm1.plot(axes, 110.0, 0.2)
#         pylab.title(spoke_codes[code])
#         pylab.savefig("%d.png" % (code))
