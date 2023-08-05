def csv_reader(filename, columns=None, delimiter='\t', quotechar=None, header=True):
    with open(filename) as infile:
        import csv
        data = csv.reader(infile, delimiter=delimiter, quotechar=quotechar)

        # determine mode of operation
        if isinstance(columns, dict):
            try:
                line = data.next()
                cols = dict((ci, line.index(columns[ci])) for ci in columns)
            except (StopIteration, ValueError), e:
                raise ValueError('Bad header structure, ' + str(e))
            for line in data:
                result = {}
                for ci in cols:
                    result[ci] = line[cols[ci]]
                yield result
        else:
            if header:
                # skip first line
                data.next()
            if isinstance(columns, list):
                for line in data:
                    yield [line[ci] for ci in columns]
            else:
                for line in data:
                    yield line

def coroutine(func):
    """Decorator that starts a coroutine automatically on call."""
    def start(*args,**kwargs):
        cr = func(*args,**kwargs)
        cr.next()
        return cr
    return start

@coroutine
def dump(filename, delimiter='\t'):
    """Write iterables to file as delimited lists."""
    with open(filename, 'w') as outfile:
        while 1:
            data = (str(di) for di in (yield))
            outfile.write(delimiter.join(data) + '\n')

def memoize(f):
    """Take a function as parameter, memoize its results.

    Can also be used as a decorator.
    """
    cache = {}
    def memf(*args):
        if args not in cache:
            cache[args] = f(*args)
        return cache[args]
    return memf
