# (c) 2011 Mouad Benchchaoui
# Licensed under the BSD license:
# http://www.opensource.org/licenses/bsd-license.php
"""helpers function to resolve an object (package, module, function, class ..)
from a dotted name and locate the file and line where this object is defined.

"""
import os
import sys
import pkgutil
import zipimport
from inspect import getsourcefile, getsourcelines, ismodule


__all__ = ['resolve', 'locate', 'LocateError']


class LocateError(Exception):
    """Error raised when locating an object fail."""


def _safe_import(name, **kws):
    """Importer that always raise ImportError when the import fail.

    Argumetns:
       - name: A dotted-name in the same syntax for importing.
       - kws: Extra keywords argument, the same one accepted by ``__import__``
              function.
    Return:
       The imported object represeting ``name``.
    Raise:
       ImportError: If in any case the import fail.
    """
    try:
        return __import__(name, **kws)
    except ValueError:
        raise ImportError('Empty module name.')
    except:
        # Broken modules end up here.
        ex = sys.exc_info()[1]
        raise ImportError(str(ex))


def resolve(name):
    """Resolve an object by dotted path/name.

    Arguments
       name: A dotted-name in the same syntax used for importing.
    Return:
       The object reprseting the dotted_name.
    Raise:
       ImportError: When the import fail.

    """
    path = name.split('.')
    current = path[0]
    found = _safe_import(current)
    for part in path[1:]:
        current += '.' + part
        try:
            found = getattr(found, part)
        except AttributeError:
            found = _safe_import(current, fromlist=part)
    return found


def _get_filename_method(loader):
    """get the method ``get_filename`` from ``pkgutil.ImpLoader`` class."""
    # Python 2.6 and below ``zipimporter`` don't have a ``get_filename`` method
    # but the PEP 302 feature was implemented under ``_get_filename``.
    for attr in ("get_filename", "_get_filename"):
        meth = getattr(loader, attr, None)
        if meth:
            return meth


def _locate_without_import(name):
    """locate ``name`` source file or directory w/o trying to import it."""
    # Don't try to locate empty string because this latest will be evaluated
    # to the first found element when passed to pkgutil.get_loader.
    if not name:
        raise LocateError('Invalid object %r' % name)
    # Using pkgutils.get_loader to overcome example where the import fail.
    try:
        loader = pkgutil.get_loader(name)
        if not loader:
            return
    except ImportError:
        # If import fail we can still try using import.
        return
    except Exception:
        # Raised when name is a broken module and pkgutil.get_loader try to
        # import it to accept the module member e.g. broken_module.whatever.
        raise LocateError(str(sys.exc_info()[1]))

    filename = None
    # In case loader is wrapped in a zipimporter i.e. eggs, zip the method
    # ``get_filename`` accept the name of the module to check for.
    if isinstance(loader, zipimport.zipimporter):
        get_filename = _get_filename_method(loader)
        if get_filename:
            filename = get_filename(name)
    else:
        filename = loader.get_filename()

    return filename


def locate(name):
    """locate ``name`` source file or directory.

    Arguments:
       - name: A dotted-name in the same syntax used for importing.
    Return:
       A string representing the path of the ``name`` object if this latest was
       found.
    Raise:
       LocateError: When locating ``name`` fail.

    """
    # First try locating an object w/o importing it.
    result = _locate_without_import(name)
    if result:
        return result

    try:
        obj = resolve(name)
    except ImportError:
        raise LocateError('object %r not found.' % name)

    try:
        output = os.path.abspath(getsourcefile(obj))
    except TypeError:
        raise LocateError('%r is built-in.' % obj)

    # Print also the line number of the object if it's not a module.
    if not ismodule(obj):
        line = getsourcelines(obj)[1]
        output += ' %d' % line
    return output
