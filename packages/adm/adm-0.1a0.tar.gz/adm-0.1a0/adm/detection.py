"""Detection for Active Data Mapping."""

import re  # TODO: Explore the idea of lazy-importing this.
import adm._compatibility._itertools   as itertools
import adm._compatibility._collections as collections
import adm._compatibility._pprint as pprint

#from adm._interfaces import _is_hashable
from adm._interfaces import _is_container
from adm._interfaces import _is_iterable
from adm._interfaces import _is_sequence
from adm._interfaces import _is_mapping

from adm.location import Location
from adm.location import _makemap
from adm.location import _is_nonstrsequence



def total_classifier(fn):
    """Decorator function"""
    def wrapped(sample):
        preface = ("Function %s() has been wrapped for use in a "
                   "classifier.  It requires an iterable collection of "
                   "mappings or sequences - " % fn.__name__)
        if not _is_iterable(sample):
            raise TypeError(preface + ("'%s' type is not iterable." %
                                       type(sample).__name__))
        if isinstance(sample, str):
            raise TypeError(preface + "instead, received a string (an "
                            "iterable collection of characters) -- "
                            "this is not allowed.")

        sample = (_makemap(obj) for obj in sample)
        outcome = fn(sample)

        # Validate outcome.
        if not _is_mapping(outcome):
            raise TypeError("Classifier %s() returned illegal type "
                            "'%s' (must return a mapping)." %
                            (fn.__name__, type(outcome).__name__))
        for val in outcome.values():
            if not isinstance(val, (float, int)):
                raise TypeError("Returned mapping contains illegal "
                                 "type '%s', %s" %
                                 (type(val).__name__, repr(outcome)))
            if val < 0 or val > 1:
                raise ValueError("Returned mapping contains illegal "
                                 "values " + repr(val))

        return outcome

    wrapped._is_classifier = True  # Wrapped classifier flag.
    wrapped.__wrapped__ = fn
    return wrapped


def column_classifier(fn):
    """Decorator function"""
    @total_classifier
    def wrapped(sample):
        # Get columns as individial lists.
        columns = collections.defaultdict(list)
            # ??? replace above with dict.fromkeys([1, 2, 3, 4], [])
        for mapping in sample:            # !!! TODO: Explore idea of
            for k, v in mapping.items():  # using generators to map
                columns[k].append(v)      # columns as individual
                                          # iterables instead of using
                                          # lists.
        outcomes = {}
        for key, column in columns.items():
            outcomes[key] = fn(column)  # Call classifier.
        return outcomes

    wrapped.__wrapped__ = fn
    return wrapped


def element_classifier(fn):
    """Decorator function"""
    @column_classifier
    def wrapped(column):
        if not _is_iterable(column) or isinstance(column, str):
            raise TypeError("Function '%s' has been wrapped for use as "
                            "a classifier.  It requires an iterable "
                            "collection of items - '%s' object is not "
                            "allowed." %
                            (fn.__name__, type(column).__name__))
            # Using LBYL style here because we should not allow strings
            # to be iterated over.  In the best case, iteration will
            # fail with a confusing traceback.  In the worst case, it's
            # conceivable that a wrapped classifier function could
            # misbehave and return false positives.
        outcomes = 0
        sample_size = 0
        for element in column:
            outcome = fn(element)  # Apply classifier function.
            if outcome is None:  # None indicates no-result, skip.
                continue

            if outcome is True:     # Explicit boolean conversion
                outcome = 1         # is more instructive.
            elif outcome is False:
                outcome = 0

            if isinstance(outcome, (float, int)) and 0 <= outcome <= 1:
                outcomes += outcome
                sample_size += 1
            else:
                raise ValueError("Calling %s() classifier on type '%s' "
                                 "returned illegal value (%s)." %
                                 (fn.__name__, type(item).__name__,
                                  outcome.__repr__()))

        if sample_size == 0:
            return 0
        return outcomes / sample_size

    wrapped.__doc__ = """Decorated function calling %s() as part of
                         classifier.""" % (fn.__name__)
    wrapped.__wrapped__ = fn
    return wrapped


class Locator(object):
    def __init__(self, *adapters, **classifiers):
        self.classifier = {}
        self.threshold  = {}
        self.result     = {}
        if adapters:
            self.adapters = list(adapters)
        else:
            self.adapters = [None]

        for clsname, clsfunc in classifiers.items():
            # If clsfunc is not callable, check for special handling.
            if not callable(clsfunc):
                try:
                    handler = getattr(self, clsname + '_handler')
                    clsfunc = handler(clsfunc)
                except AttributeError:
                    raise TypeError("Special handling for '%s' "
                                    "classifier is unsupported." %
                                    (clsname))
            # If clsfunc is not classifier, wrap as element classifier.
            try:
                assert clsfunc._is_classifier
            except:
                clsfunc = element_classifier(clsfunc)

            self.classifier[clsname] = clsfunc

    def __repr__(self):
        matches = self._get_matches(self.adapters, self.threshold, self.result)
        matchcount = len(matches)
        if matchcount == 1:
            status = 'mapped'
        elif matchcount > 1:
            status = 'ambiguous'
        else:
            status = 'unmapped'

        requirements = self.threshold.items()
        requirements = sorted(requirements)
        requirements = [str(k)+'='+repr(v) for k, v in requirements]
        requirements = ', '.join(requirements)
        if requirements:
            requirements = ', using ' + requirements

        if self.result:
            stats = [x for x in self.result if x.clsvalue > 0]
            stats = pprint.pformat(stats)
        else:
            stats = ''

        return ('<%s object, status: %s%s> %s' %
                (self.__class__.__name__, status, requirements, stats))

    @staticmethod
    def _filter_cutoff(cutoff, results):
        """Takes cutoff dict and results set and returns only those
        results with values that meet or exceed the matching cutoff.

        Individual result objects are 4-tuples:
            0=objkey, 1=adapter, 2=clsname, 3=clsvalue

        """
        def meets_cutoff(result):
            clsname, clsresult = result[2], result[3]  # Unpack tuple.
            clscutoff = cutoff.get(clsname)
            return clscutoff is not None and clsresult >= clscutoff
        return {r for r in results if meets_cutoff(r)}

    @staticmethod
    def _filter_required(cutoff, results):
        """Takes cutoff dict and results set, returns results for only
        those objkeys that are matched by all required cutoffs.

        Individual result objects are 4-tuples:
            0=objkey, 1=adapter, 2=clsname, 3=clsvalue

        """
        required_clsnames = set(cutoff.keys())

        getobjkey  = lambda r: r[0]  # Get object key from result tuple.
        results = sorted(results, key=getobjkey)

        filtered = set()
        for objkey, group in itertools.groupby(results, key=getobjkey):
            group = set(group)
            matched_clsnames = {result[2] for result in group}
            if matched_clsnames >= required_clsnames:
                filtered = filtered | group  # Union of sets.

        return filtered

    @staticmethod
    def _filter_average(results):
        """
        Individual result objects are 4-tuples:
            0=objkey, 1=adapter, 2=clsname, 3=clsvalue

        """
        # Sort by objkey and id value of adapter.
        sortfn = lambda r: (r[0], id(r[1]))
        results = sorted(results, key=sortfn)

        # Group by objkey & adapter (direct reference) and build result
        # with an average clsvalue for each objkey/adapter pair.
        groupfn = lambda r: (r[0], r[1])
        averaged_results = set()
        for key, group in itertools.groupby(results, key=groupfn):
            objkey, adapter = key # Unpack tuple.
            group = list(group)

            clsnames = frozenset(x[2] for x in group)
            clsvalues = [x[3] for x in group]
            clsaverage = sum(clsvalues) / len(clsvalues)

            rtype = type(group[0])  # Reuse type (namedtuple or tuple).
            #average = rtype([objkey, adapter, clsnames, clsaverage])
            try:
                average = rtype(objkey, adapter, clsnames, clsaverage)
            except TypeError:
                average = rtype([objkey, adapter, clsnames, clsaverage])

            averaged_results.add(average)

        return averaged_results

    @staticmethod
    def _filter_maximum(results):
        """
        Individual result objects are 4-tuples:
            0=objkey, 1=adapter, 2=clsname, 3=clsvalue

        """
        def sortfn(r):
            return r[0]  # By objkey.
        results = sorted(results, key=sortfn)

        maxvals = {}
        for objkey, group in itertools.groupby(results, key=sortfn):
            clsvals = [x[3] for x in group]
            maxvals[objkey] = max(clsvals)

        return {r for r in results if r[3]==maxvals.get(r[0])}

    @staticmethod
    def _filter_order(adapters, results):
        """Takes list of adapters and set of results.  Returns set of
        results with unique objkeys paired with the first matching
        adapter.

        Individual result objects are 4-tuples:
            0=objkey, 1=adapter, 2=clsname, 3=clsvalue

        """
        def sortfn(r):  # Sort by objkey & adapter index position.
            return r[0], adapters.index(r[1])
        results = sorted(results, key=sortfn)

        def groupfn(r):  # Group by objkey only.
            return r[0]
        first_adapter = set()
        for key, group in itertools.groupby(results, key=groupfn):
            result = next(group)  # Take first result only.
            first_adapter.add(result)

        return first_adapter

    @staticmethod
    def _get_matches(adapters, cutoff, stats):
        stats = Locator._filter_cutoff(cutoff, stats)
        stats = Locator._filter_required(cutoff, stats)
        stats = Locator._filter_average(stats)
        stats = Locator._filter_maximum(stats)
        stats = Locator._filter_order(adapters, stats)
        return stats

        #stats    = self.results
        #cutoff   = self.threshold
        #adapters = self.adapters

    def location(self):
        stats = self._get_matches(self.adapters, self.threshold,
                                  self.result)
        # Take resulting matches and build Location obects for each.
        locations = {Location(x[0], adapter=x[1]) for x in stats}

        if len(locations) == 0:  # Set empty set to None.
            locations = None
        elif len(locations) == 1:  # Unwrap if single item.
            locations = locations.pop()
        return locations

    def ismapped(self):
        matches = self._get_matches(self.adapters, self.threshold,
                                    self.result)
        return len(matches) == 1

    def __call__(self, obj):
        if self.ismapped():
            location = self.location()
            return location(obj)
        return None

    def scan(self, sample, **criteria):
        """
        Individual result objects are 4-tuples:
            0=objkey, 1=adapter, 2=clsname, 3=clsvalue

        """
        # Register threshold values.
        self.threshold = criteria

        # Normalize sample as a list of mappings.
        def normalize(mapping):
            if not _is_mapping(mapping):
                if isinstance(mapping, str):
                    raise TypeError(("sample must be an iterable "
                                     "collection of mappings or "
                                     "sequences - a collection of "
                                     "strings is not allowed.") %
                                     fn.__name__)
                mapping = dict(enumerate(mapping))
            return mapping
        sample = [normalize(mapping) for mapping in sample]

        # Closure (closes over 'sample').
        def classify(adapter, classifier_key):  # !!! TODO: Replace closures with partial()
            if adapter:
                fn = lambda mapping: {k:adapter(v) for k,v in mapping.items()}  # Closes over adapter
                sample_values = (fn(mapping) for mapping in sample)
            else:
                sample_values = sample
            return self.classifier[classifier_key](sample_values)

        # Build adapter/classifier combinations and classify.
        product = itertools.product(self.adapters, criteria.keys())

        rtup = collections.namedtuple('result', ['objkey',  'adapter',
                                                 'clsname', 'clsvalue'])
        result = []
        for adapter, clsname in product:
            objscores = classify(adapter, clsname)
            for objkey, clsvalue in objscores.items():
                bar = rtup(objkey, adapter, clsname, clsvalue)
                result.append(bar)

        self.result = set(result)

    @staticmethod
    def form_handler(patterns):
        if isinstance(patterns, str) or not _is_container(patterns):
            patterns = [patterns]

        retype = type(re.compile('foo'))  # re module's compiled object
                                          # type is poorly defined.
        compiled_pats = []
        for pat in patterns:
            if not isinstance(pat, retype):
                pat = re.compile(pat)
            compiled_pats.append(pat)

        @element_classifier
        def classify_by_form(element):  # Closure over compiled_pats.
            for pat in compiled_pats:
                if pat.search(element):
                    return True
            return False

        return classify_by_form

    @staticmethod
    def freq_handler(pmf):  # Probability mass function.
        """Accepts probability distribution as a dict."""

        @column_classifier
        def classify_by_freq(column):
            count = collections.Counter(column)
            total = sum(count.values())
            count = {k:v/total for k,v in count.items()}

            common = set(count.keys()) & set(pmf.keys())
            if len(common) < 2:
                return 0

            filtered_count = [(k,v) for k,v in count.items() if k in common]
            filtered_pmf = [(k,v) for k,v in pmf.items() if k in common]

            freq_count = [v for k,v in sorted(filtered_count)]
            freq_pmf   = [v for k,v in sorted(filtered_pmf)]

            # Calibrate.
            min_pmf, min_count = sorted(zip(freq_pmf, freq_count))[0]
            adjust = min_count / min_pmf
            freq_pmf = [v * adjust for v in freq_pmf]

            coefficient = pearsonr(freq_count, freq_pmf)
            return max(coefficient, 0)

        return classify_by_freq

    @staticmethod
    def head_handler(patterns):
        if isinstance(patterns, str) or not _is_container(patterns):
            patterns = [patterns]

        retype = type(re.compile('foo'))  # re module's compiled object
                                          # type is poorly defined.
        compiled_pats = []
        for pat in patterns:
            if not isinstance(pat, retype):
                pat = re.compile(pat)
            compiled_pats.append(pat)

        @column_classifier
        def classify_by_head(column):  # Closure over compiled_pats.
            first_row = column[0]
            for pat in compiled_pats:
                if pat.search(first_row):
                    return 1
            return 0

        return classify_by_head



def pearsonr(x, y):
    """Returns the Pearson product-moment correlation coefficient
    (Pearson's r) between sequence x and sequence y.

    """
    #print(x, y)

    n = len(x)
    assert n == len(y)
    x_bar = sum(x) / n
    y_bar = sum(y) / n
    xy_sum = x_sq_sum = y_sq_sum = 0
    for x_diff, y_diff in ((xi-x_bar, yi-y_bar) for xi, yi in zip(x, y)):
        xy_sum += x_diff * y_diff
        x_sq_sum += x_diff ** 2
        y_sq_sum += y_diff ** 2
    return xy_sum / ((x_sq_sum * y_sq_sum) ** 0.5)

