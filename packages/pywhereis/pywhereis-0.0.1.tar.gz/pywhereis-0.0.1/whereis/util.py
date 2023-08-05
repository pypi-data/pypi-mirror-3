# (c) 2011 Mouad Benchchaoui
# Licensed under the BSD license:
# http://www.opensource.org/licenses/bsd-license.php
"""helpers function to resolve an object (package, module, function, class ..)
from a dotted name and locate the file and line where this object is defined.

"""
import os
import sys
import pkgutil
from inspect import getsourcefile, getsourcelines, ismodule


__all__ = ['resolve', 'locate']


def _safe_import(name, **kws):
    """Importer that always raise ImportError when the import fail."""
    try:
        return __import__(name, **kws)
    except ValueError:
        raise ImportError('Empty module name.')


def resolve(path):
    """Resolve an object by dotted path."""
    path = path.split('.')
    current = path[0]
    found = _safe_import(current)
    for part in path[1:]:
        current += '.' + part
        try:
            found = getattr(found, part)
        except AttributeError:
            found = _safe_import(current, fromlist=part)
    return found


def locate(name, verbose=0):
    """locate the ``name`` source file or directory."""
    # Using pkgutils.get_loader to overcome example where the import fail.
    try:
        loader = pkgutil.get_loader(name)
        if loader and loader.get_filename():
            return loader.get_filename()
    except ImportError:
        pass

    try:
        obj = resolve(name)
    except ImportError:
        if verbose:
            return 'Error: object %s not found.' % name
        return

    try:
        output = os.path.abspath(getsourcefile(obj))
    except TypeError:
        if verbose:
            return 'Error: %r is built-in.' % obj
        return

    # Print also the line number of the object if it's not a module.
    if not ismodule(obj):
        line = getsourcelines(obj)[1]
        output += ' %d' % line
    return output
