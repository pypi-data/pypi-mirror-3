#!/usr/bin/env python
# -*- coding: utf-8 -*-
#try:
#    from setuptools import setup
#except ImportError:
#    from distutils.core import setup
from distutils.core import setup

import os
import sys


########################################################################
# Define top-level package, test suite, and locations for Py 2 versions.
########################################################################
PY3_PACKAGES = {
    'adm':                'adm',
    'adm.tests':          'adm/tests',
    'adm._compatibility': 'adm/_compatibility'
}

PY2_PACKAGES = {
    'adm':                'py2src_no-edit/adm',
    'adm.tests':          'py2src_no-edit/adm/tests',
    'adm._compatibility': 'py2src_no-edit/adm/_compatibility'
}

TEST_SUITE = 'adm.tests'



BACKPORT_DIR = 'py2src_no-edit'
PACKAGE_DIR_PY3 = 'adm'
PACKAGE_DIR_PY2 = 'py2src_no-edit/adm'


########################################################################
# Basic setup.py stuff...
########################################################################
if __name__ == '__main__':
    if sys.version_info[0] == 3:
        PACKAGE_DIR = PY3_PACKAGES
    else:
        PACKAGE_DIR = PY2_PACKAGES
        #import backport
        #if sys.version_info[0] == 2:                # Add import hooks for
        #    backport.add_import_hook(BACKPORT_DIR)  # testing.


    #if 'script_args' not in attrs:
    #    attrs['script_args'] = sys.argv[1:]

    # Prepare extra key word arguments.
    extras = {}
    if 'setuptools' in sys.modules:
        extras['test_suite'] = TEST_SUITE

    setup(name         = 'adm',
          version      = '0.1a0',
          description  = '',
          url          = 'http://code.google.com/p/activedatamapping/',
          author       = 'Shawn Brown',
          author_email = '',  # Expected if author is specified.
          license      = '',
          long_description = '',
          #platforms    = '',
          classifiers  = ['Development Status :: 2 - Pre-Alpha',
                         'License :: OSI Approved :: Apache Software License',
                         'Topic :: Scientific/Engineering :: Information Analysis',
                         'Programming Language :: Python :: 2.4',
                         'Programming Language :: Python :: 2.5',
                         'Programming Language :: Python :: 2.6',
                         'Programming Language :: Python :: 2.7',
                         'Programming Language :: Python :: 3'],
          packages     = PACKAGE_DIR.keys(),
          package_dir  = PACKAGE_DIR,
          **extras)

