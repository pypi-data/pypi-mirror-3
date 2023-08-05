#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
The code in this module is adapted from

"Numerical Recipes 3rd Edition - The Art of Scientific Computing",
by William H. Press, Saul A. Teukolsky, William T. Vetterling,
   Brian P. Flannery
"""

from __future__ import division
from . import tools as t
import random
import math

def four1(data):
    nn = len(data)
    n = nn // 2
    if n < 2 or (n & (n - 1)) != 0:
        raise ValueError("n must be power of 2 in four1")
    j = 1
    for i in xrange(1, nn, 2):
        if j > i:
            data[j - 1], data[i - 1] = data[i - 1], data[j - 1]
            data[j], data[i] = data[i], data[j]
        m = n
        while m >= 2 and j > m:
            j -= m
            m //= 2
        j += m
    mmax = 2
    while nn > mmax:
        istep = mmax + mmax
        theta = 2 * math.pi / mmax
        wtemp = math.sin(0.5 * theta)
        wpr = -2.0 * wtemp * wtemp
        wpi = math.sin(theta)
        wr = 1.0
        wi = 0.0
        for m in xrange(1, mmax, 2):
            for i in xrange(m, nn + 1, istep):
                j = i + mmax
                tempr = wr * data[j - 1] - wi * data[j    ]
                tempi = wr * data[j    ] + wi * data[j - 1]
                data[j - 1] = data[i - 1] - tempr
                data[j    ] = data[i    ] - tempi
                data[i - 1] += tempr
                data[i    ] += tempi
            wtemp = wr
            wr = wr * (wpr + 1) - wpi * wi
            wi = wi * (wpr + 1) + wpi * wtemp
        mmax = istep

def realft(data):
    n = len(data)
    theta = math.pi / (n // 2)
    four1(data)
    wtemp = math.sin(0.5 * theta)
    wpr = -2.0 * wtemp * wtemp
    wpi = math.sin(theta)
    wr = 1.0 + wpr
    wi = wpi
    for i in xrange(1, n // 4):
        i1 = i + i
        i2 = i + i + 1
        i3 = n - i - i
        i4 = n - i - i + 1
        h1r =  0.5 * (data[i1] + data[i3])
        h1i =  0.5 * (data[i2] - data[i4])
        h2r =  0.5 * (data[i2] + data[i4])
        h2i = -0.5 * (data[i1] - data[i3])
        data[i1] =  h1r + wr * h2r - wi * h2i
        data[i2] =  h1i + wr * h2i + wi * h2r
        data[i3] =  h1r - wr * h2r + wi * h2i
        data[i4] = -h1i + wr * h2i + wi * h2r
        wr, wi = wr * (wpr + 1) - wpi * wi, wi * (wpr + 1) + wpi * wr
    data[0], data[1] = data[0] + data[1], data[0] - data[1]

def avevar(data):
    """Returns average and variance of 'data'."""
    n = len(data)
    ave = sum(data) / n
    dif = (x - ave for x in data)
    var = (sum(x * x for x in dif) - (sum(dif) ** 2) / n) / (n - 1)
    return ave, var

@t.memoize
def _coef(dx, m):
    fac = dx
    nden = 1.0
    for i in xrange(1, m):
        fac *= dx - i
        nden *= -i
    result = [fac / (nden * dx)]
    for i in xrange(1, m):
        nden *= -i / (m - i)
        result.append(fac / (nden * (dx - i)))
    return result

def fasper(x, y, ofac, hifac):
    """Calc Lomb periodogram of the data in 'x' and 'y'.
    The values in 'x' are the positions of the corresponding amplitude values
    in 'y'. For best results, normalize 'x' values to fit into [0.0..1.0) and
    (since the data should be periodic anyway) copy the value at 0.0 to 1.0.
    """
    MACC = 4
    n = len(x)
    nout = int(round(ofac * hifac * n * 0.5))
    nfreqt = int(ofac * hifac * n * MACC)
    nfreq = 64
    while (nfreq < nfreqt):
        nfreq *= 2
    nwk = nfreq * 2

    ave, var = avevar(y)
    if var == 0.0:
        raise ValueError("zero variance in fasper")
    xmin = min(x)
    xmax = max(x)
    xdif = xmax - xmin;
    wk1 = [0.0] * nwk
    wk2 = [0.0] * nwk
    fac = nwk / (xdif * ofac)

    def spread(y, yy, x, m):
        """Reverse LaGrange interpolation of 'y' into the list 'yy'.
        'x' is the position of the interpolated value 'y' and should be between
            0 and 'len(yy) - 1'.
        'm' is the number of list entries the value is to be spread over. Its
            value must be 1 or greater.
        """
        if abs(x - int(x)) < 1e-6:
            yy[int(x)] += y
        else:
            ilo = int(x - 0.5 * m) + 1
            if ilo < 0:
                ilo = 0
            elif ilo > nwk - m:
                ilo = nwk - m
            for i, cy in enumerate(_coef(x - ilo, m)):
                yy[ilo + i] += cy * y

    for j in xrange(n):
        ck = (x[j] - xmin) * fac % nwk
        ckk = 2.0 * ck % nwk
        spread(y[j] - ave, wk1, ck, MACC)
        spread(1.0, wk2, ckk, MACC)

    realft(wk1)
    realft(wk2)
    df = 1.0 / (xdif * ofac)
    k = 2
    px = []
    py = []
    for j in xrange(nout):
        hypo = math.sqrt(wk2[k] * wk2[k] + wk2[k + 1] * wk2[k + 1])
        hc2wt = 0.5 * wk2[k] / hypo
        cwt = math.sqrt(0.5 + hc2wt)
        swt = math.copysign(math.sqrt(0.5 - hc2wt), wk2[k + 1])
        cterm = ((cwt * wk1[k    ] + swt * wk1[k + 1]) ** 2) / (n + hypo)
        sterm = ((cwt * wk1[k + 1] - swt * wk1[k    ]) ** 2) / (n - hypo)
        px.append((j + 1) * df)
        py.append((cterm + sterm) / var)
        k += 2
    p = [1.0 - pow(1.0 - math.exp(-x), 2.0 * nout / ofac) for x in py]
    return px, py, p

if __name__ == '__main__':
    n = 300
    x = [float(i) / n for i in xrange(n)]
    x.sort()
    x[0] = 0
    x.append(1)
    y = [5 * random.random() + math.sin(xi * 10 * math.pi + 0.754) for xi in x]
    px, py, p = fasper(x, y, 1, 1)
    a = zip(px, py, p)
