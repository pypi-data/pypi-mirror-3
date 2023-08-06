u"""Partitions for Active Data Mapping."""

from adm._compatibility._builtins import *
from adm.detection import Locator
from adm.location  import Location
from adm.location  import _makemap


class Cell(Location):
    u""" """
    def __init__(self, label, *location, **kwds):
        self.label = label
        if u'maptype' in kwds:
            self.maptype = kwds.pop(u'maptype')
        else:
            self.maptype = dict
        Location.__init__(self, *location, **kwds)

    def _set_keys(self, keys):
        super(self.__class__, self)._set_keys(keys)
        self._validate_chain(self)

    keys = property(Location._get_keys, _set_keys,
                    doc=u'A tuple containing one or more keys.')

    def __call__(self, obj, maptype=None):
        def getitem(obj, key):
            if isinstance(key, self.__class__):      # Closing over
                return key.label, key(obj, maptype)  # maptype.
            #if isinstance(key, Locator):
            if isinstance(key, (Locator, Location)):  # ??? TODO: Enforce
                return None, key(obj)                 # adapter/single return val
            return key, obj.get(key, None)

        obj = _makemap(obj)
        items = [getitem(obj, key) for key in self.keys]
        if self.adapter:
            result = self.adapter(*tuple(v for k,v in items))
        elif len(items) == 1:
            result = items[0][1]  # Unwrap single value (discards key).
        else:
            if maptype is None:
                maptype = self.maptype

            if callable(maptype) and maptype.__name__ == u'namedtuple':
                tup = maptype(self.label, [k for k,v in items])
                result = tup(*[v for k,v in items])
                # Above, we check callable and __name__ to support
                # namedtuple functions in versions 2.5 and earlier
                # (collections.namedtuple is new in 2.6).
            elif issubclass(maptype, dict):
                result = maptype(items)
            elif issubclass(maptype, (list, tuple)):
                result = maptype([v for k,v in items])
        return result

    def _ismapped(self):
        u"""Returns True if a Cell's location is fully mapped."""
        def fn(x):
            if isinstance(x, self.__class__):
                return x._ismapped()
            if isinstance(x, Locator):
                return x.ismapped()
            if isinstance(x, Location) or x != tuple():
                return True  # ??? CHECK: Do we need to test for tuple?
            return False

        return all(fn(x) for x in self.keys)

    def _getsubcells(self):
        subcells = set()
        for key in self.keys:
            if isinstance(key, self.__class__):
                subcells.add(key)
                subcells = subcells | key._getsubcells()
        return subcells

    def mapped(self):
        u"""Returns labels of all mapped subcells."""
        subcells = self._getsubcells()
        return set(x.label for x in subcells if x._ismapped())

    def unmapped(self):
        u"""Returns labels of all unmapped subcells."""
        subcells = self._getsubcells()
        return set(x.label for x in subcells if not x._ismapped())

    def identify(self, sample, **criteria):
        for key in self.keys:
            if isinstance(key, Locator):
                key.scan(sample, **criteria)
            elif isinstance(key, self.__class__):
                self.__class__.identify(key, sample, **criteria)

    def __repr__(self):
        clsname = self.__class__.__name__
        width = 80 - len(clsname) - len(repr(self.label))
        pretty = self._prettify(self.keys, width=width)
        if self.adapter:
            pretty += u', adapter=' + self.adapter.__name__
        return clsname + u'(' + repr(self.label) + u', ' + pretty + u')'

    @staticmethod
    def _get_digraph(tail, digraph=None):
        u"""Get list of directed graph arcs as tuples (tail, head)."""
        if digraph is None:
            digraph = []
        for head in tail.keys:
            if (tail, head) not in digraph:
                digraph.append((tail, head))
                if isinstance(head, tail.__class__):
                    Cell._get_digraph(tail=head, digraph=digraph)
        return digraph

    @staticmethod
    def _get_leaf_arcs(digraph):
        u"""Get list of leaves (arcs to nodes without children)."""
        leaves = set(y for x, y in digraph) - set(x for x, y in digraph)
        return [(x, y) for x, y in digraph if y in leaves]

    @staticmethod
    def _get_orphan_arcs(digraph):
        u"""Get list of orphans (arcs from nodes without parents)."""
        orphans = set(x for x, y in digraph) - set(y for x, y in digraph)
        return [(x, y) for x, y in digraph if x in orphans]

    @staticmethod
    def _validate_chain(obj):
        u"""Asserts that partition meets finite chain condition."""
        graph = Cell._get_digraph(obj)

        # Test graph for acyclicity by successively removing all leaves.
        leaf_arcs = Cell._get_leaf_arcs(graph)
        while leaf_arcs:
            graph = [arc for arc in graph if arc not in leaf_arcs]
            leaf_arcs = Cell._get_leaf_arcs(graph)

        # If graph still contains arcs, then there's an infinite chain.
        if graph:
            # Successively remove all orphans (they're not the problem).
            orphan_arcs = Cell._get_orphan_arcs(graph)
            while orphan_arcs:
                graph = [arc for arc in graph if arc not in orphan_arcs]
                orphan_arcs = Cell._get_orphan_arcs(graph)

            # Format chain description and raise Exception.
            chain = [unicode(x.label)+u'->'+unicode(y.label) for x,y in graph]
            chain = u', '.join(chain)
            raise AttributeError(u'violates finite chain condition: %s' %
                                 (chain))

