u"""Location for Active Data Mapping."""

from adm._compatibility._builtins import *
from adm._interfaces import _is_container
from adm._interfaces import _is_hashable
from adm._interfaces import _is_mapping
from adm._interfaces import _is_sequence
import adm._compatibility._inspect as inspect
import adm._compatibility._pprint as pprint


class _UNSPECIFIED(object):  # Sentinel for unspecified argumenmts.
    pass


def _is_nonstrsequence(obj):
    return _is_sequence(obj) and not isinstance(obj, unicode)


def _is_nonstriterable(obj):
    return _is_iterable(obj) and not isinstance(obj, unicode)


def _makemap(obj):
    u"""Convert given object to mapping object (dictionary)."""
    if not _is_mapping(obj):
        if not _is_nonstrsequence(obj):
            raise TypeError(u"Encountered non-sequence or string type "
                            u"'%s'." % type(obj).__name__)
        obj = dict(enumerate(obj))
    return obj


class Location(object):
    def __init__(self, *location, **kwds):
        u"""Location(key1[, key2[, ...]][, adapter])"""
        self._keys = ()
        self._adapter  = None
        self.update(*location, **kwds)

    def __call__(self, obj):
        obj = _makemap(obj)
        items = [(key, obj[key]) for key in self.keys]
        if self.adapter:
            result = self.adapter(*tuple(v for k,v in items))
        elif len(items) == 1:
            result = items[0][1]  # Unwrap single value (discards key).
        else:
            result = dict(items)
        return result

    def __repr__(self):
        clsname = self.__class__.__name__
        width = 80 - len(clsname)
        pretty = self._prettify(self.keys, width=width)
        if self.adapter:
            pretty += u', adapter=' + self.adapter.__name__
        return clsname + u'(' + pretty + u')'

    @staticmethod
    def _prettify(allkeys, width=80):
        pretty = pprint.pformat(tuple(allkeys), width=width)
        pretty = pretty[1:-1]        # Slice begin/end parentheses.
        pretty = pretty.strip(u' ,')  # Strip begin/end syntax.
        return pretty

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.keys      == other.keys      and
                self.adapter   == other.adapter)

    def __hash__(self):
        keylst = []   # Need to keep list of already-seen keys in case
        keyshash = 0  # to prevent recursion if infinite-chain exists.
        for key in self.keys:
            keyshash = keyshash ^ hash(key)
            keylst.append(key)
            if key in keylst:
                break
        return hash(self.__class__) ^ keyshash ^ hash(self.adapter)

    def _get_keys(self):
        return self._keys

    def _set_keys(self, keys):
        if not _is_nonstrsequence(keys):
            keys = [keys]
        self._validate_pair(keys, self.adapter)
        self._keys = tuple(keys)

    keys = property(_get_keys, _set_keys,
                    doc=u'A tuple containing one or more keys.')

    def _get_adapter(self):
        return self._adapter

    def _set_adapter(self, adapter):
        self._validate_pair(self.keys, adapter)
        self._adapter = adapter

    adapter = property(_get_adapter, _set_adapter,
                       doc=(u'A function to get value from location '
                            u'objects.'))

    def update(self, *location, **kwds):
        u"""Location.update(key1[, key2[, ...]][, adapter])"""
        keys, adapter, kwds = self._normalize_args(*location, **kwds)

        if keys is _UNSPECIFIED:
            keys = self.keys
        if adapter is _UNSPECIFIED:
            adapter = self.adapter

        self._validate_pair(keys, adapter)
        self._keys = tuple(keys)
        self._adapter = adapter

    @staticmethod
    def _normalize_args(*location, **kwds):
        location = list(location)
        if (location and _is_sequence(location[0]) and
            not isinstance(location[0], unicode)):  # Unwrap if nested
            if len(location) == 1:              # sequence.
                location = location[0]
            elif len(location) == 2 and inspect.isfunction(location[-1]):
                location = location[0] + [location[1]]  # Inline adapter

        if u'adapter' in kwds:
            adapter = kwds.pop(u'adapter')
        elif len(location) > 1 and inspect.isfunction(location[-1]):
            adapter = location.pop()  # adapter was inlined.
        else:
            adapter = _UNSPECIFIED

        if u'keys' in kwds:
            keys = kwds.pop(u'keys')
            if isinstance(keys, unicode) or not _is_sequence(keys):
                keys = [keys]
        elif location:
            keys = location
        else:
            keys = _UNSPECIFIED

        return keys, adapter, kwds

    @staticmethod
    def _validate_pair(keys, adapter):
        u"""Raises Exception if invalid, returns None if all OK."""
        if not keys:
            raise AttributeError(u'keys are required (none provided)')

        if not _is_sequence(keys):  # Container must be ordered.
            raise TypeError(u"keys is non-sequence type '%s'" %
                            (type(keys).__name__))

        for key in keys:               # keys items must be suitable
            if not _is_hashable(key):  # mapping keys (hashable).
                raise TypeError(u"keys contains unhashable type '%s'" %
                                (type(key).__name__))

        # adapter must be callable or None.
        if adapter is not None and not callable(adapter):
            raise TypeError(u"adapter is uncallable type '%s'" %
                            (type(adapter).__name__))

        # Validate adapter/location compatibility.
        if adapter:
            argspec = inspect.getfullargspec(adapter)
            (args,     varargs,    varkw,
             defaults, kwonlyargs, kwonlydefaults) = argspec[:6]

            if varkw or kwonlyargs or kwonlydefaults:
                raise AttributeError(u'adapter must not use keyword '
                                     u'arguments')

            # Determine max and min number of args adapter requires.
            if varargs:
                minlen = len(args) + 1
                maxlen = float(u'inf')   # Infinity.
            else:
                minlen = maxlen = len(args)

            if defaults:
                minlen -= len(defaults)  # Adjust for default values.

            # Test keys and adapter for compatiblility.
            locationlen = len(keys)
            if not minlen <= locationlen <= maxlen:
                if minlen == maxlen:
                    qualifier = u'exactly'
                    required = minlen
                elif locationlen < minlen:
                    qualifier = u'at least'
                    required = minlen
                elif locationlen > maxlen:
                    qualifier = u'at most'
                    required = maxlen

                if required > 1:
                    plural = u's'
                else:
                    plural = u''

                raise AttributeError(u"adapter '%s' takes %s %s "
                                     u"argument%s (keys gives %s)" %
                                     (adapter.__name__, qualifier,
                                      required, plural, locationlen))

