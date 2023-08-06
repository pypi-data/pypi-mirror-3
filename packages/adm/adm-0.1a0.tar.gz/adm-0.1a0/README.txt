The test harness for this project can be run under Python 3 or Python 2.
It requires the use of 3to2 -- available on PyPI at <http://pypi.python.org/pypi/3to2>
or <http://pypi.python.org/pypi/3to2_py3k>.

Once you have 3to2 installed, open a terminal window and navigate to the
project directory. Run the following script:

    python runtests.py

You can also run tests using setup.py with the following command:

    python setup.py test

If you're using Python 3, the test suite should run as normal. If you're
using Python 2, `backport' is used to build a copy of the project,
convert it with 3to2, and run test suite using the Python 2 interpreter.
