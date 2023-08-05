# -*- encoding: utf-8 -*-
"""Locate a python object (package, module, function, class ...) source file.

Usage:
   pywhereis [OPTIONS] dotted_name...

Options:
   -h, --help: print the help message and exit.
   -v, --verbose: Enable the verbose mode.
   -s, --site-packages: Search in site-packages before current directory.

"""
import sys
import copy
import getopt

from .util import locate, resolve, LocateError


__all__ = ['locate', 'resolve', 'LocateError', '__version__', 'main']


__author__ = "Mouad Benchchaoui"
__copyright__ = "Copyright © 2011, Mouad Benchchaoui"
__license__ = "BSD license"
__version__ = "0.0.2"


def usage(err_msg=None):
    """Print error message and usage string."""
    if err_msg:
        sys.stderr.write('Error: %s' % err_msg)
        sys.stderr.write('\n\n')
    sys.stderr.write(__doc__)


def main(argv=sys.argv[1:]):
    """Main function."""
    try:
        opts, args = getopt.getopt(
                          argv, 'hvs', ('help', 'verbose', 'site-packages'))
    except getopt.GetoptError:
        usage(sys.exc_info()[1])
        return 1

    verbose = 0
    site_packages = False  # Search in site_packages first or in curdir first.
    for opt, _ in opts:
        if opt in ('-h', '--help'):
            return usage()
        elif opt in ('-v', '--verbose'):
            verbose = 1
        elif opt in ('-s', '--site-packages'):
            site_packages = True

    if not args:
        usage('No name was given.')
        return 1

    # Save the current sys.path to recover it in the end of the function.
    original_sys_path = copy.copy(sys.path)
    if site_packages:
        sys.path.append('.')
    else:
        # Add the curpath to make imports works for modules/packages in curdir.
        sys.path.insert(0, '.')

    try:
        for dotted_name in args:
            res = None
            try:
                res = locate(dotted_name)
            except LocateError:
                if verbose:
                    res = 'Error: %s' % sys.exc_info()[1]
            print('%s: %s' % (dotted_name, res or ''))
    finally:
        sys.path = original_sys_path
