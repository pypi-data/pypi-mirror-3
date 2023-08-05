#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from math import log, exp, sqrt
try:
    from math import erfc
except ImportError:
    # Python < 2.7
    _erfc_cof = [-2.8e-17, 1.21e-16, -9.4e-17, -1.523e-15, 7.106e-15,
                  3.81e-16, -1.12708e-13, 3.13092e-13, 8.94487e-13,
                 -6.886027e-12, 2.394038e-12, 9.6467911e-11,
                 -2.27365122e-10, -9.91364156e-10, 5.059343495e-9,
                  6.529054439e-9, -8.5238095915e-8, 1.5626441722e-8,
                  1.303655835580e-6, -1.624290004647e-6,
                 -2.0278578112534e-5, 4.2523324806907e-5,
                  3.66839497852761e-4, -9.46595344482036e-4,
                 -9.561514786808631e-3, 1.9476473204185836e-2,
                  6.4196979235649026e-1, -1.3026537197817094]
    def erfc(x):
        """Calculate the value of error function at x."""
        def erfccheb(z):
            d = 0.0
            dd = 0.0
            t = 2.0 / (2.0 + z)
            ty = 4.0 * t - 2.0
            for j in xrange(len(_erfc_cof) - 1):
                d, dd = ty * d - dd + _erfc_cof[j], d
            return t * exp(-z * z + 0.5 * (_erfc_cof[-1] + ty * d) - dd)

        if x >= 0.0:
            return erfccheb(x)
        else:
            return 2.0 - erfccheb(-x)

from . import tools as t

@t.memoize
def stdnorm_invcdf(p):
    """Calculate quantile value of standard normal distribution."""
    # code adapted from Numerical Recipes
    def inverfc(p):
        pp = p if p < 1.0 else 2.0 - p
        t = sqrt(-2.0 * log(pp / 2.0))
        x = -0.70711 * ((2.30753 + t * 0.27061) / (1.0 + t * (0.99229 + t * 0.04481)) - t)
        err = erfc(x) - pp
        x += err / (1.12837916709551257 * exp(-x * x) - x * err)
        err = erfc(x) - pp
        x += err / (1.12837916709551257 * exp(-x * x) - x * err)
        return x if p < 1.0 else -x

    if not 0.0 < p < 1.0:
        raise ValueError('p value outside valid range')
    return -1.41421356237309505 * inverfc(2.0 * p)

def mean(data):
    """Return the mean of the supplied list."""
    return sum(data) / len(data) if len(data) > 0 else None

def variance(data):
    """Return variance of 'data'."""
    n = len(data)
    mdata = mean(data)
    dif = (x - mdata for x in data)
    return (sum(x * x for x in dif) - (sum(dif) ** 2) / n) / (n - 1)

def mean_var(data):
    """Return mean value and variance of 'data'.

    Use this routine if you need both instead of calculating them separately."""
    n = float(len(data))
    md = mean(data)
    if n <= 1:
        return md, 0
    else:
        dif = (x - md for x in data)
        return md, (sum(x * x for x in dif) - (sum(dif) ** 2) / n) / (n - 1)

def mean_stderr(data):
    """Return mean value and standard error."""
    md, var = mean_var(data)
    stderr = sqrt(var / len(data))
    return md, stderr

def mean_ci(data, alpha):
    """Return mean value and confidence interval."""
    md, stderr = mean_stderr(data)
    return md, stderr * stdnorm_invcdf(1.0 - alpha / 2.0)

def median(data):
    """Return the median of the supplied list."""
    return quantile(data, 0.5)

def quantile(data, q):
    """Return the specified quantile(s) q of the supplied list.

    The function can be called with either a single value for q or a list of
    values. In the latter case, the returned value is a tuple.
    """
    sx = sorted(data)
    def get_quantile(q1):
        pos = (len(sx) - 1) * q1
        if abs(pos - int(pos) - 0.5) < 0.1:
            # quantile in the middle between two values, average them
            return (sx[int(pos)] + sx[int(pos) + 1]) * 0.5
        else:
            # otherwise return the nearest value
            return sx[int(pos + 0.5)]

    if hasattr(q, '__iter__'):
        return tuple([get_quantile(qi) for qi in q])
    else:
        return get_quantile(q)

if __name__ == '__main__':
    pass
