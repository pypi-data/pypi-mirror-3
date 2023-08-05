#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from collections import defaultdict
from .stats import mean

#
# 'extract' and related functions
#
def extract(data, key, start=datetime(2000, 1, 1), end=datetime.utcnow(),
            fx=None):
    """Extract all values of the specified key from the given dataset.

    Additionally a date range for the returned values can be specified,
    and a function to transform the x values with.
    """
    values = [(d['time'], [d[key]]) for d in data if start < d['time'] <= end]
    if fx is not None:
        return recode(values, fx=fx)
    else:
        return values

def by_date(data, key, start=datetime(2000, 1, 1), end=datetime.utcnow()):
    """Group an activity array by date."""
    fx = lambda x: x.date()
    return extract(data, key, start, end, fx)

def by_time(data, key, start=datetime(2000, 1, 1), end=datetime.utcnow()):
    """Group an activity array by time."""
    fx = lambda x: x - x.replace(hour = 0, minute=0, second=0, microsecond=0)
    return extract(data, key, start, end, fx)

#
# 'recode' and related functions
#
def recode(data, fx=None, fy=None):
    """Apply transformations to keys and values in supplied list."""
    if fx is None:
        return [(di[0], fy(di[1])) for di in data] if fy is not None else data
    else:
        buckets = defaultdict(list)
        for di in data:
            buckets[fx(di[0])].extend(di[1])
        if fy is None:
            return [(xpos, buckets[xpos]) for xpos in sorted(buckets.keys())]
        else:
            return [(xpos, fy(buckets[xpos])) for xpos in sorted(buckets.keys())]

def quant_time(data, size=3600, start=timedelta(0), fy=None):
    """Group timestamps to bins. Input x values are of timedelta type."""
    to_seconds = lambda x: x.days * 86400 + x.seconds
    fx = lambda x: timedelta(seconds=((to_seconds(x - start) % 86400) // size) * size)
    return recode(data, fx=fx, fy=fy)

def quant_time_raw(data, size=3600, start=timedelta(0), fy=None):
    """Group timestamps to bins. Input x values are of datetime type.

    First the date will be stripped, then the times will be discretized.
    """
    to_seconds = lambda x: x.days * 86400 + x.seconds
    fx = lambda x: timedelta(seconds=((to_seconds((x - x.replace(hour=0,
                        minute=0, second=0)) - start) % 86400) // size) * size)
    return recode(data, fx=fx, fy=fy)

#
# list management functions
#

def split(data, fx):
    """Return dictionary with data split into bins according to fx(x)."""
    result = defaultdict(list)
    for di in data:
        result[fx(di[0])].append(di)
    return result

def merge(data1, data2):
    """Merge two datasets with similar structure.

    X coordinates missing from either dataset will be created as needed.
    Values from the second dataset will be appended after those from the first.
    """
    buckets = defaultdict(list)
    for di in data1:
        buckets[di[0]] = di[1][:]
    for di in data2:
        buckets[di[0]].extend(di[1])
    return [(xpos, buckets[xpos]) for xpos in sorted(buckets.keys())]

def unpack(data):
    """Return x and y values in two separate arrays.

    If each y value list has only one value in it, the y values are returned
    as one list. Otherwise they are returned as a tuple of lists.
    """
    if data:
        x = [di[0] for di in data]
        if len(data[0][1]) <= 1:
            y = [di[1][0] for di in data]
        else:
            y = [[] for dij in data[0][1]]
            for di in data:
                for j, dij in enumerate(di[1]):
                    y[j].append(dij)
        return x, y
    else:
        return [], []


#
# everything else
#

def sliding_window(data, length, step=None, start=None):
    """Generator, return progressing portions of data.

    length: size of the window.
    step: the amount by which the starting position is increased between bins.
    start: from where to start placing bins.
    """

    if step == None:
        step = length
    # adjust 'start' to the available data
    if start == None:
        start = data[0][0]
    else:
        while start < data[0][0]:
            start += step
    # init indices of first and last relevant value
    i = 0
    while data[i][0] < start:
        i += 1

    bin_lens = []
    window = []
    while 1:
        # append new values and break if there are not enough values left
        try:
            while data[i][0] < start + length:
                window.append(data[i])
                i += 1
        except IndexError:
            # end of data reached, ignore the last window if it's too short
            if len(bin_lens) == 0:
                pass
            elif len(window) == 0 or len(window) < 0.95 * mean(bin_lens):
                break

        # return a copy since 'window' may not be changed from outside
        yield window[:]

        bin_lens.append(len(window))

        start += step
        # remove values from the start that are no more relevant
        while len(window) > 0 and window[0][0] < start:
            del window[0]

def guess_dt(data):
    """Take a sample of the first 100 values and return the most common delta."""
    dts = {}
    try:
        for i in xrange(1, min(100, len(data))):
            d = data[i][0] - data[i - 1][0]
            dts[d] = dts.get(d, 0) + 1
        dt = sorted(dts.items(), key=lambda x: x[1], reverse=True)[0][0]
        return dt.days * 86400 + dt.seconds
    except (IndexError, KeyError):
        return None
    except AttributeError:
        # dt turned out not to be a timedelta, assume it's a number
        return dt

def date_gaps(data, step=timedelta(1)):
    """Add 'None' values whenever a date is missing.

    Should only be used as the last step before plotting the data
    since 'None's among valid numeric values break many calculations.
    """
    result = [data[0]]
    delta = step + timedelta(hours = 12)
    for d in data[1:]:
        while d[0] - result[-1][0] > delta:
            result.append((result[-1][0] + step, [None] * len(d[1])))
        result.append(d)
    return result

# alternative version of date_gaps; more general, but relies on exact steps
def close_gaps(data, step):
    """Add 'None' values wherever a value is missing.

    Should only be used as the last step before plotting the data
    since 'None's among valid numeric values break many calculations.
    """
    result = [data[0]]
    for d in data[1:]:
        while d[0] - result[-1][0] > step:
            result.append((result[-1][0] + step, [None] * len(d[1])))
        result.append(d)
    return result

