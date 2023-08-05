#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import datetime as dtm
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as dates
from . import readdata as rd
from . import analysis as an
from . import tools as t

def activity_dist(dataset, key, start=dtm.datetime(2000, 1, 1), end=dtm.datetime.utcnow(),
                  axes=None, cumulative=True, nozeros=False):
    """Display the distribution of values in dataset."""
    data = an.extract(dataset, key, start=start, end=end)
    mindate = np.floor(dates.date2num(data[0][0]))
    maxdate = np.ceil(dates.date2num(data[-1][0]))

    data = an.recode(data, fx=lambda x: x.date())
    # put data into matrix
    dist = np.zeros((int(maxdate) - int(mindate), 256))
    for day in data:
        y = dates.date2num(day[0]) - mindate
        for val in day[1]:
            if not nozeros or val > 0:
                dist[y][int(val)] += 1

    if cumulative:
        # calculate cumulative distribution
        for line in dist:
            for x in xrange(2 if nozeros else 1, 256):
                line[x] += line[x - 1]
            # normalize values to [0,1]
            if line[-1] > 0:
                line /= line[-1]
    else:
        # probability distribution is already done
        # normalize values to [0,1]
        for line in dist:
            s = sum(line)
            if s > 0:
                line /= s

    # transpose matrix to make days vertical
    dist = dist.transpose()

    # draw
    if not axes:
        fig = plt.figure()
        ax1 = fig.add_axes([0.08, 0.18, 0.90, 0.78])
    else:
        ax1 = axes

    im1 = ax1.imshow(dist, origin='lower', cmap='spectral', aspect='auto',
                     interpolation='nearest', extent=(mindate, maxdate, 0, 256))
    ax1.xaxis_date()
    fig.autofmt_xdate(rotation=90, ha='center')
    fig.colorbar(im1, fraction=0.10, shrink=0.9)
    if not axes:
        plt.show()

    return ax1

def actogram(dataset, key, start=dtm.datetime(2000, 1, 1), end=dtm.datetime.utcnow(),
             axes=None, cmap='gnuplot2_r', width=1.0, sunlines=None, bgcolor=None, colorbar=True):
    """Plot an activity dataset as an actogram."""

    @t.coroutine
    def get_grid_pos(date, dt, ncols):
        """Quantize date into discrete steps of 'dt' from start of 'date'."""
        date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        dt = int(dt)
        sampledate = (yield)
        while 1:
            diff = sampledate - date
            sampledate = (yield (diff.days * ncols + (diff.seconds // dt)))

    def reshape(data, dt, width=1.0):
        """Convert data from (x, y) pairs to a 2D list."""
        ncols = int(86400.0 / dt + 0.5)
        grid = get_grid_pos(data[0][0], dt, ncols)

        # set the array to final dimensions and fill it with nans
        finalheight = np.ceil(grid.send(data[-1][0]) / ncols)
        finalwidth = int(86400.0  * width / dt + 0.5)
        data2 = np.empty((finalheight, finalwidth))
        data2.fill(np.nan)

        # place samples into array
        for di in data:
            pos = grid.send(di[0])
            data2[pos // ncols, pos % ncols] = di[1][0]

        # copy the first day as required by width
        xpos = ncols
        shift = 1
        while xpos < finalwidth:
            xwidth = min(finalwidth - xpos, ncols)
            data2[: finalheight - shift, xpos : xpos + xwidth] = data2[shift : finalheight, 0 : xwidth]
            shift += 1
            xpos += ncols

        return data2

    data = an.extract(dataset, key, start=start, end=end)
    mindate = dates.date2num(data[0][0])
    maxdate = dates.date2num(data[-1][0])
    data = reshape(data, dataset.dt_sec, width)

    # either create a new chart or draw onto the supplied one
    if not axes:
        fig = plt.figure()
        ax1 = fig.add_axes([0.15, 0.15, 0.85, 0.80])
    else:
        ax1 = axes

    # draw data
    if bgcolor is not None:
        # background color
        ax1.patch.set_facecolor(bgcolor)

    # add palette if it's not present (for mpl < 1.0)
    if not 'gnuplot2_r' in plt.cm.datad:
        cmap_data = {'red':   ((0., 1., 1.), (0.43, 1., 1.), (0.75, 0., 0.), (1., 0., 0.)),
                     'green': ((0., 1., 1.), (0.08, 1., 1.), (0.57, 0., 0.), (1., 0., 0.)),
                     'blue':  ((0., 1., 1.), (0.08, 0., 0.), (0.58, 1., 1.), (0.75, 1., 1.),
                               (1., 0., 0.))}
        plt.cm.datad['gnuplot2_r'] = cmap_data
        plt.cm.cmap_d['gnuplot2_r'] = plt.cm.colors.LinearSegmentedColormap('gnuplot2_r', cmap_data, plt.cm.LUTSIZE)

    # plot data
    im1 = ax1.imshow(data, cmap=cmap, aspect='auto',
                     origin='lower', interpolation='nearest',
                     extent=(np.floor(mindate), np.floor(mindate) + width,
                             np.floor(mindate), np.ceil(maxdate)))
    # draw sun overlays
    if sunlines:
        import astro as ast
        suncalc = ast.sun_calc(dataset.lon, dataset.lat)

        def sunline(interval):
            # first calculate
            linedata = []
            ddelta = dtm.timedelta(days=1)
            day = dates.num2date(mindate).replace(tzinfo=None)
            maxdated = dates.num2date(np.ceil(maxdate) + 1).replace(tzinfo=None)
            baseline = np.floor(mindate)
            minutes = interval.get('minutes', 0) / 1440.0
            while day < maxdated:
                valid, inttime = suncalc(day, interval)
                inttime = dates.date2num(inttime) + minutes - baseline
                linedata.append((valid, inttime))
                day += ddelta
                baseline += 1.0

            mintime = min(ti[1] for ti in linedata)
            maxtime = max(ti[1] for ti in linedata)

            # append values at end to compensate for wrapping over
            # left edge and 'width' > 1.0
            delta = 1.0
            while mintime + delta < width:
                valid, inttime = suncalc(day, interval)
                inttime = dates.date2num(inttime) + minutes - baseline
                linedata.append((valid, inttime))
                day += ddelta
                baseline += 1.0
                delta += 1.0

            baseline = np.floor(mindate)
            # insert value at beginning if line wraps over the right edge
            if False and maxtime + delta > 0.0:
                delta = -1.0
                baseline -= 1.0
                day = dates.num2date(mindate - 1.0).replace(tzinfo=None)
                while maxtime + delta > 0.0:
                    valid, inttime = suncalc(day, interval)
                    inttime = dates.date2num(inttime) + minutes - baseline
                    linedata.append((valid, inttime))
                    day -= ddelta
                    baseline -= 1.0
                    delta -= 1.0
                # shift all values by 'delta'
                linedata = [(ti[0], ti[1] + delta) for ti in linedata]

            # check status flags, replace values with nans if they are inside
            # a series of False values, but keep the times of the first and
            # last of them.
            result = []
            for i, ti in enumerate(linedata):
                if ti[0]:
                    result.append(ti[1])
                else:
                    try:
                        pre = linedata[i - 1][0]
                    except IndexError:
                        pre = False

                    try:
                        post = linedata[i + 1][0]
                    except IndexError:
                        post = False

                    result.append(ti[1] if pre or post else np.nan)

            return result

        sundata = [sunline(line) for line in sunlines]

        # finally draw the lines
        numdays = int(np.ceil(maxdate) - np.floor(mindate))
        # nans are inserted between copies of lines to disconnect them
        yvals = np.append(np.linspace(np.floor(mindate), np.ceil(maxdate), numdays + 1), np.nan)
        for i, line in enumerate(sundata):
            xpoints = np.array([])
            ypoints = np.array([])
            startid = 0
            delta = 0.0
            while startid + numdays < len(line):
                xpoints = np.append(xpoints, np.array(line[startid:startid + numdays + 1] + [np.nan]) + (np.floor(mindate) + delta))
                ypoints = np.append(ypoints, yvals)
                startid += 1
                delta += 1.0
            ax1.plot(xpoints, ypoints, **sunlines[i].get('style', {}))

        # reset axes limits to fit tightly around the actogram
        ax1.set_xlim(np.floor(mindate), np.floor(mindate) + width)
        ax1.set_ylim(np.floor(mindate), np.ceil(maxdate))

    # set up time axis (bottom)
    ax1.xaxis_date()
    ax1.xaxis.set_major_formatter(dates.DateFormatter('%H:%M'))
    #fig.autofmt_xdate(rotation=90, ha='center')
    ax1.figure.autofmt_xdate(rotation=90, ha='center')

    # set up date axis (left)
    ax1.invert_yaxis()
    ax1.yaxis_date()
    dayspan = np.ceil(maxdate) - np.floor(mindate)
    if dayspan < 70:
        ax1.yaxis.set_major_locator(dates.DayLocator(interval=int(np.ceil(dayspan / 8))))
        ax1.yaxis.set_minor_locator(dates.DayLocator(interval=1))
    elif dayspan < 700:
        ax1.yaxis.set_major_locator(dates.MonthLocator(interval=int(np.ceil(dayspan / (30 * 8)))))
        ax1.yaxis.set_minor_locator(dates.MonthLocator(interval=1))
    else:
        ax1.yaxis.set_major_locator(dates.AutoDateLocator())
        ax1.yaxis.set_minor_locator(dates.MonthLocator(interval=1))
    ax1.yaxis.set_major_formatter(dates.DateFormatter('%Y-%m-%d'))

    if colorbar:
        ax1.figure.colorbar(im1, fraction=0.10, shrink=0.9)

    if not axes:
        plt.show()

    return ax1

def spectrogram(dataset, key, start=dtm.datetime(2000, 1, 1), end=dtm.datetime.utcnow(),
                axes=None, ndays=7, nfreq=96, ofac=1, onlysig=False,
                alpha=0.05, silent=False):
    from fasper import fasper
    # define 'total_seconds', which is not present in Python < 2.7
    if hasattr(dtm.timedelta, 'total_seconds'):
        def total_seconds(t):
            return t.total_seconds()
    else:
        def total_seconds(t):
            return t.days * 86400.0 + t.seconds + t.microseconds * 1e-6

    data = an.extract(dataset, key, start=start, end=end)
    grid = []
    for dblock in an.sliding_window(data, length=dtm.timedelta(ndays), step=dtm.timedelta(1)):
        if not dblock:
            continue
        if not silent:
            print '{0} - {1}'.format(dblock[0][0], dblock[-1][0])
        start = dblock[0][0]
        x, y = an.unpack(dblock)
        x = [total_seconds(xi - start) / 86400.0 for xi in x]

        xdif = (x[-1] - x[0])
        hifac = (2 * xdif * nfreq) / (ofac * ndays * len(x))
        px, py, p = fasper(x, y, ofac * ndays / xdif, hifac)
        if onlysig:
            for i, _ in enumerate(py):
                if p[i] > alpha:
                    py[i] = np.nan
        grid.append(py)

    # either create a new chart or draw onto the supplied one
    if not axes:
        fig = plt.figure()
        ax1 = fig.add_axes([0.15, 0.10, 0.80, 0.85])
    else:
        ax1 = axes

    mindate = dates.date2num(data[0][0])

    ax1.imshow(np.array(grid), interpolation='nearest', aspect='auto', origin='lower',
               extent=(0.5, nfreq + 0.5,
                       np.floor(mindate) - 0.5, np.floor(mindate) + len(grid) - 0.5))
    ax1.invert_yaxis()
    ax1.yaxis_date()
    ax1.yaxis.set_major_locator(dates.DayLocator(interval=int(len(grid) / 8)))
    ax1.yaxis.set_major_formatter(dates.DateFormatter('%Y-%m-%d'))

    if not axes:
        plt.show()

    return ax1

