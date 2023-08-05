#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import struct
from datetime import datetime, timedelta

class ActivityDataset(object):
    def _guess_dt(self):
        """Take a sample of the first 100 values and return the most common delta."""
        dts = {}
        try:
            for i in xrange(1, min(100, len(self._data))):
                d = self._data[i]['time'] - self._data[i - 1]['time']
                dts[d] = dts.get(d, 0) + 1
            dt = sorted(dts.items(), key=lambda x: x[1], reverse=True)[0][0]
            return dt
        except (IndexError, KeyError):
            raise ValueError('Unexpected data structure')

    def extract(self, key, start=datetime(2000, 1, 1), end=datetime.utcnow()):
        """Extract all values of the specified key.

        Additionally a date range for the returned values can be specified.
        """
        return ((d['time'], [d[key]]) for d in self._data if start < d['time'] <= end)

    def summary(self):
        """Print info about the data."""
        lines = []
        fields = [('Collar ID', 'cid'), ('Sampling period (s)', 'dt'),
                  ('Activity mode', 'mode'), ('Firmware', 'firmware')]
        for field, attr in fields:
            if hasattr(self, attr):
                lines.append('{0}: {1}'.format(field, getattr(self, attr)))
        if lines:
            # add an empty line for aesthetics
            lines.append('')
            print('\n'.join(lines))

        _delta = timedelta(hours=1)
        ranges = []
        rstart = 0
        for i in xrange (1, len(self._data)):
            if self._data[i]['time'] - self._data[i - 1]['time'] > _delta:
                ranges.append((rstart, i - 1))
                rstart = i
        ranges.append((rstart, len(self._data) - 1))
        for start, end in ranges:
            print('{0} - {1}, {2} sample(s)'.format(self._data[start]['time'], self._data[end]['time'], end - start + 1))

    def __getitem__(self, index):
        return self._data[index]

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return (x for x in self._data)

class CSVReader(ActivityDataset):
    def __init__(self, filename, lon=None, lat=None, columns=None, delimiter='\t',
                 skiplines=0, coltypes=None, format=None):
        if format == 'vas':
            # data from Vectronic Aerospace collars, converted by GPS Plus
            columns = {'date': 'UTC_Date', 'time': 'UTC_Time',
                       'x': 'ActivityX', 'y': 'ActivityY', 'temp': 'Temp'}
            delimiter = ' '
            skiplines = 1

            def vas_coltypes(value):
                time = value['date'].split('.')[::-1] + value['time'].split(':')
                del value['date']
                value['time'] = datetime(int(time[0]), int(time[1]), int(time[2]), int(time[3]), int(time[4]), int(time[5]))
                value['x'] = int(value['x'])
                value['y'] = int(value['y'])
                value['temp'] = int(value['temp'])
                return value
            coltypes = vas_coltypes

        if columns is None:
            raise ValueError('No columns specified')

        self.lon = lon
        self.lat = lat

        import tools as t
        infile = t.csv_reader(filename, columns, delimiter)
        for _ in xrange(skiplines):
            infile.next()

        if coltypes:
            #convert data to usable types
            self._data = [coltypes(line) for line in infile]

            self.dt = self._guess_dt()
            # convert self.dt to float
            try:
                self.dt_sec = float(self.dt)
            except TypeError:
                # not int or float, try timedelta
                if hasattr(self.dt, 'total_seconds'):
                    # timedelta with python >= 2.7
                    self.dt_sec = self.dt.total_seconds()
                else:
                    # possibly timedelta with python < 2.6
                    try:
                        self.dt_sec = (self.dt.days * 86400.0 + self.dt.seconds +
                                       self.dt.microseconds * 1e-6)
                    except AttributeError:
                        # not timedelta, give up
                        raise TypeError('data type of dt unrecognized: ' + type(self.dt))
            # adjust times to point to the middle of periods
            dt2 = self.dt / 2
            for di in self._data:
                di['time'] = di['time'] - dt2
        else:
            # no coltypes provided, leave data as strings
            self._data = list(infile)

if __name__ == '__main__':
    #a = CSVReader('../data/ACT_Collar05161.TXT', format='vas')
    a = ADFReader('../data/Collar07151.adf')
