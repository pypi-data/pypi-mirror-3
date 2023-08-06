
from heapq import *

try:
    nlargest(0, [], key=lambda n: n)  # key arg added in 2.5
except TypeError:
    # Following code from the Python 2.7 heapq implementation...
    # Released under the Python Software Foundation Library
    # <http://www.opensource.org/licenses/Python-2.0>.

    # Extend the implementations of nlargest to use a key= argument
    from adm._compatibility._itertools import count, imap, izip, tee

    _nlargest = nlargest
    def nlargest(n, iterable, key=None):
        """Find the n largest elements in a dataset.

        Equivalent to:  sorted(iterable, key=key, reverse=True)[:n]
        """

        # Short-cut for n==1 is to use max() when len(iterable)>0
        if n == 1:
            it = iter(iterable)
            head = list(islice(it, 1))
            if not head:
                return []
            if key is None:
                return [max(chain(head, it))]
            return [max(chain(head, it), key=key)]

        # When n>=size, it's faster to use sorted()
        try:
            size = len(iterable)
        except (TypeError, AttributeError):
            pass
        else:
            if n >= size:
                return sorted(iterable, key=key, reverse=True)[:n]

        # When key is none, use simpler decoration
        if key is None:
            it = izip(iterable, count(0,-1))                    # decorate
            result = _nlargest(n, it)
            return map(itemgetter(0), result)                   # undecorate

        # General case, slowest method
        in1, in2 = tee(iterable)
        it = izip(imap(key, in1), count(0,-1), in2)             # decorate
        result = _nlargest(n, it)
        return map(itemgetter(2), result)                       # undecorate
