
import pprint

try:
    # Test for issue 14998 <http://bugs.python.org/issue14998>.
    pprint.pformat({(None,): 0, (1,): 0})
except TypeError:
    class _safe_key(pprint._safe_key):
        def __lt__(self, other):
            try:
                rv = self.obj.__lt__(other.obj)
            except TypeError:
                rv = NotImplemented

            if rv is NotImplemented:
                rv = (str(type(self.obj)), id(self.obj)) < \
                     (str(type(other.obj)), id(other.obj))
            return rv

    pprint._safe_key = _safe_key  # Apply monkey patch if needed.


from pprint import *  # Import into local namespace after patching.

