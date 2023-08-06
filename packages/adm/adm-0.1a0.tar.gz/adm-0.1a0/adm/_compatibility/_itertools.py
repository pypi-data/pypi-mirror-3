
from itertools import *

try:
    count(start=0, step=2)  # step argument added in Python 2.7.
except TypeError:
    def count(start=0, step=1):
        n = start
        while True:
            yield n
            n += step

try:
    product  # New in Python 2.6.
except NameError:
    def product(*args, **kwds):
        # product('ABCD', 'xy') --> Ax Ay Bx By Cx Cy Dx Dy
        # product(range(2), repeat=3) --> 000 001 010 011 100 101 110 111
        pools = map(tuple, args) * kwds.get('repeat', 1)
        result = [[]]
        for pool in pools:
            result = [x+[y] for x in result for y in pool]
        for prod in result:
            yield tuple(prod)
