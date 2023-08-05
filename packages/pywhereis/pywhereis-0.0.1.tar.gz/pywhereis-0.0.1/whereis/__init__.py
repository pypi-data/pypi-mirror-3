# -*- encoding: utf-8 -*-
"""Locate a python object (package, module, function, class ...) source file.

Usage:
   pywhereis [-v] dotted_name...

"""
import sys
import getopt

from . import util


__all__ = ['locate', 'resolve', '__version__', 'main']


__author__ = "Mouad Benchchaoui"
__copyright__ = "Copyright © 2011, Mouad Benchchaoui"
__license__ = "BSD license"
__version__ = "0.0.1"


# Create a shortcuts for util.locate and util.resolve.
locate = util.locate
resolve = util.resolve


def usage(err_msg=None):
    """Print error message and usage string."""
    if err_msg:
        sys.stderr.write('Error: %s' % err_msg)
        sys.stderr.write('\n\n')
    sys.stderr.write(__doc__)


def main(argv=sys.argv):
    """Main function."""
    try:
        opts, args = getopt.getopt(argv[1:], 'hv', ('help', 'verbose'))
    except getopt.GetoptError:
        usage(sys.exc_info()[1])
        return 1

    verbose = 0
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            return usage()
        elif opt in ('-v', '--verbose'):
            verbose = 1
        else:
            usage('Unhandled option.')
            return 1

    if not args:
        usage('No name was given.')
        return 1

    # Add the curpath to make imports works for modules/packages in curdir.
    sys.path.append('.')
    for dotted_name in args:
        res = locate(dotted_name, verbose=verbose)
        print('%s: %s' % (dotted_name, res or ''))
