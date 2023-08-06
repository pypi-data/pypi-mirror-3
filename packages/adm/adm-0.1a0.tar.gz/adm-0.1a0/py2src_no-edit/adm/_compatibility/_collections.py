
from collections import *

#from adm._compatibility.__abcoll import *
#import adm._compatibility.__abcoll as _abcoll
##__all__ += _abcoll.__all__


try:
    namedtuple  # New in Python 2.6
except NameError:
    # Copyright 2007 Raymond Hettinger
    # From http://code.activestate.com/recipes/500261-named-tuples/
    # Released under the Python Software Foundation License
    # <http://www.opensource.org/licenses/Python-2.0>.
    from operator import itemgetter as _itemgetter
    from keyword import iskeyword as _iskeyword
    import sys as _sys

    def namedtuple(typename, field_names, verbose=False, rename=False):
        # Parse and validate the field names.  Validation serves two purposes,
        # generating informative error messages and preventing template injection attacks.
        if isinstance(field_names, basestring):
            field_names = field_names.replace(u',', u' ').split() # names separated by whitespace and/or commas
        field_names = tuple(map(unicode, field_names))
        if rename:
            names = list(field_names)
            seen = set()
            for i, name in enumerate(names):
                if (not min(c.isalnum() or c==u'_' for c in name) or _iskeyword(name)
                    or not name or name[0].isdigit() or name.startswith(u'_')
                    or name in seen):
                        names[i] = u'_%d' % i
                seen.add(name)
            field_names = tuple(names)
        for name in (typename,) + field_names:
            if not min(c.isalnum() or c==u'_' for c in name):
                raise ValueError(u'Type names and field names can only contain alphanumeric characters and underscores: %r' % name)
            if _iskeyword(name):
                raise ValueError(u'Type names and field names cannot be a keyword: %r' % name)
            if name[0].isdigit():
                raise ValueError(u'Type names and field names cannot start with a number: %r' % name)
        seen_names = set()
        for name in field_names:
            if name.startswith(u'_') and not rename:
                raise ValueError(u'Field names cannot start with an underscore: %r' % name)
            if name in seen_names:
                raise ValueError(u'Encountered duplicate field name: %r' % name)
            seen_names.add(name)

        # Create and fill-in the class template
        numfields = len(field_names)
        argtxt = repr(field_names).replace(u"'", u"")[1:-1]   # tuple repr without parens or quotes
        reprtxt = u', '.join(u'%s=%%r' % name for name in field_names)
        template = u'''class %(typename)s(tuple):
            '%(typename)s(%(argtxt)s)' \n
            __slots__ = () \n
            _fields = %(field_names)r \n
            def __new__(_cls, %(argtxt)s):
                return _tuple.__new__(_cls, (%(argtxt)s)) \n
            @classmethod
            def _make(cls, iterable, new=tuple.__new__, len=len):
                'Make a new %(typename)s object from a sequence or iterable'
                result = new(cls, iterable)
                if len(result) != %(numfields)d:
                    raise TypeError('Expected %(numfields)d arguments, got %%d' %% len(result))
                return result \n
            def __repr__(self):
                return '%(typename)s(%(reprtxt)s)' %% self \n
            def _asdict(self):
                'Return a new dict which maps field names to their values'
                return dict(zip(self._fields, self)) \n
            def _replace(_self, **kwds):
                'Return a new %(typename)s object replacing specified fields with new values'
                result = _self._make(map(kwds.pop, %(field_names)r, _self))
                if kwds:
                    raise ValueError('Got unexpected field names: %%r' %% kwds.keys())
                return result \n
            def __getnewargs__(self):
                return tuple(self) \n\n''' % locals()
        for i, name in enumerate(field_names):
            template += u'            %s = _property(_itemgetter(%d))\n' % (name, i)
        if verbose:
            print template

        # Execute the template string in a temporary namespace
        namespace = dict(_itemgetter=_itemgetter, __name__=u'namedtuple_%s' % typename,
                         _property=property, _tuple=tuple)
        try:
            exec(template, namespace)
        except SyntaxError, e:
            raise SyntaxError(unicode(e) + u':\n' + template)
        result = namespace[typename]

        # For pickling to work, the __module__ variable needs to be set to the frame
        # where the named tuple is created.  Bypass this step in enviroments where
        # sys._getframe is not defined (Jython for example) or sys._getframe is not
        # defined for arguments greater than 0 (IronPython).
        try:
            result.__module__ = _sys._getframe(1).f_globals.get(u'__name__', u'__main__')
        except (AttributeError, ValueError):
            pass

        return result


try:
    Counter  # New in Python 2.7
except NameError:
    # Copyright 2009 Raymond Hettinger
    # From http://code.activestate.com/recipes/576611-counter-class/
    # Released under the MIT License
    # <http://www.opensource.org/licenses/MIT>.

    from operator import itemgetter
    from adm._compatibility._heapq import nlargest
    from adm._compatibility._itertools import repeat, ifilter

    class Counter(dict):
        u'''Dict subclass for counting hashable objects.  Sometimes called a bag
        or multiset.  Elements are stored as dictionary keys and their counts
        are stored as dictionary values.

        >>> Counter('zyzygy')
        Counter({'y': 3, 'z': 2, 'g': 1})

        '''

        def __init__(self, iterable=None, **kwds):
            u'''Create a new, empty Counter object.  And if given, count elements
            from an input iterable.  Or, initialize the count from another mapping
            of elements to their counts.

            >>> c = Counter()                           # a new, empty counter
            >>> c = Counter('gallahad')                 # a new counter from an iterable
            >>> c = Counter({'a': 4, 'b': 2})           # a new counter from a mapping
            >>> c = Counter(a=4, b=2)                   # a new counter from keyword args

            '''
            self.update(iterable, **kwds)

        def __getitem__(self, key):
            # This try/catch was added for Python 2.4 support since
            # builtin __missing__ support was added in Python 2.5.
            try:
                return dict.__getitem__(self, key)
            except KeyError:
                self[key] = value = self.__missing__(key)
                return value

        def __missing__(self, key):
            return 0

        def most_common(self, n=None):
            u'''List the n most common elements and their counts from the most
            common to the least.  If n is None, then list all element counts.

            >>> Counter('abracadabra').most_common(3)
            [('a', 5), ('r', 2), ('b', 2)]

            '''
            if n is None:
                return sorted(self.iteritems(), key=itemgetter(1), reverse=True)
            return nlargest(n, self.iteritems(), key=itemgetter(1))

        def elements(self):
            u'''Iterator over elements repeating each as many times as its count.

            >>> c = Counter('ABCABC')
            >>> sorted(c.elements())
            ['A', 'A', 'B', 'B', 'C', 'C']

            If an element's count has been set to zero or is a negative number,
            elements() will ignore it.

            '''
            for elem, count in self.iteritems():
                for _ in repeat(None, count):
                    yield elem

        # Override dict methods where the meaning changes for Counter objects.

        @classmethod
        def fromkeys(cls, iterable, v=None):
            raise NotImplementedError(
                u'Counter.fromkeys() is undefined.  Use Counter(iterable) instead.')

        def update(self, iterable=None, **kwds):
            u'''Like dict.update() but add counts instead of replacing them.

            Source can be an iterable, a dictionary, or another Counter instance.

            >>> c = Counter('which')
            >>> c.update('witch')           # add elements from another iterable
            >>> d = Counter('watch')
            >>> c.update(d)                 # add elements from another counter
            >>> c['h']                      # four 'h' in which, witch, and watch
            4

            '''
            if iterable is not None:
                if hasattr(iterable, u'iteritems'):
                    if self:
                        self_get = self.get
                        for elem, count in iterable.iteritems():
                            self[elem] = self_get(elem, 0) + count
                    else:
                        dict.update(self, iterable) # fast path when counter is empty
                else:
                    self_get = self.get
                    for elem in iterable:
                        self[elem] = self_get(elem, 0) + 1
            if kwds:
                self.update(kwds)

        def copy(self):
            u'Like dict.copy() but returns a Counter instance instead of a dict.'
            return Counter(self)

        def __delitem__(self, elem):
            u'Like dict.__delitem__() but does not raise KeyError for missing values.'
            if elem in self:
                dict.__delitem__(self, elem)

        def __repr__(self):
            if not self:
                return u'%s()' % self.__class__.__name__
            items = u', '.join(map(u'%r: %r'.__mod__, self.most_common()))
            return u'%s({%s})' % (self.__class__.__name__, items)

        # Multiset-style mathematical operations discussed in:
        #       Knuth TAOCP Volume II section 4.6.3 exercise 19
        #       and at http://en.wikipedia.org/wiki/Multiset
        #
        # Outputs guaranteed to only include positive counts.
        #
        # To strip negative and zero counts, add-in an empty counter:
        #       c += Counter()

        def __add__(self, other):
            u'''Add counts from two counters.

            >>> Counter('abbb') + Counter('bcc')
            Counter({'b': 4, 'c': 2, 'a': 1})


            '''
            if not isinstance(other, Counter):
                return NotImplemented
            result = Counter()
            for elem in set(self) | set(other):
                #newcount = self[elem] + other[elem]
                selfelem = self[elem]
                otherelem = other[elem]
                newcount = selfelem + otherelem

                if newcount > 0:
                    result[elem] = newcount
            return result

        def __sub__(self, other):
            u''' Subtract count, but keep only results with positive counts.

            >>> Counter('abbbc') - Counter('bccd')
            Counter({'b': 2, 'a': 1})

            '''
            if not isinstance(other, Counter):
                return NotImplemented
            result = Counter()
            for elem in set(self) | set(other):
                newcount = self[elem] - other[elem]
                if newcount > 0:
                    result[elem] = newcount
            return result

        def __or__(self, other):
            u'''Union is the maximum of value in either of the input counters.

            >>> Counter('abbb') | Counter('bcc')
            Counter({'b': 3, 'c': 2, 'a': 1})

            '''
            if not isinstance(other, Counter):
                return NotImplemented
            _max = max
            result = Counter()
            for elem in set(self) | set(other):
                newcount = _max(self[elem], other[elem])
                if newcount > 0:
                    result[elem] = newcount
            return result

        def __and__(self, other):
            u''' Intersection is the minimum of corresponding counts.

            >>> Counter('abbb') & Counter('bcc')
            Counter({'b': 1})

            '''
            if not isinstance(other, Counter):
                return NotImplemented
            _min = min
            result = Counter()
            if len(self) < len(other):
                self, other = other, self
            for elem in ifilter(self.__contains__, other):
                newcount = _min(self[elem], other[elem])
                if newcount > 0:
                    result[elem] = newcount
            return result


try:
    defaultdict  # New in Python 2.5
except NameError:
    # Copyright 2007 Jason Kirtland
    # From http://code.activestate.com/recipes/523034-emulate-collectionsdefaultdict/
    # Released under the Python Software Foundation License
    # <http://www.opensource.org/licenses/Python-2.0>.
    class defaultdict(dict):
        def __init__(self, default_factory=None, *a, **kw):
            if (default_factory is not None and
                not hasattr(default_factory, u'__call__')):
                raise TypeError(u'first argument must be callable')
            dict.__init__(self, *a, **kw)
            self.default_factory = default_factory

        def __getitem__(self, key):
            try:
                return dict.__getitem__(self, key)
            except KeyError:
                return self.__missing__(key)

        def __missing__(self, key):
            if self.default_factory is None:
                raise KeyError(key)
            self[key] = value = self.default_factory()
            return value

        def __reduce__(self):
            if self.default_factory is None:
                args = tuple()
            else:
                args = self.default_factory,
            return type(self), args, None, None, self.items()

        def copy(self):
            return self.__copy__()

        def __copy__(self):
            return type(self)(self.default_factory, self)

        def __deepcopy__(self, memo):
            import copy
            return type(self)(self.default_factory,
                              copy.deepcopy(self.items()))

        def __repr__(self):
            return u'defaultdict(%s, %s)' % (self.default_factory,
                                            dict.__repr__(self))

