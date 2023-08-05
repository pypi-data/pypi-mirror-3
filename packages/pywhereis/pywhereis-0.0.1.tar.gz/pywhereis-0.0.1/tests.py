#! /usr/bin/env python
# -*- encoding: utf8 -*-
"""Test Cases for pywhereis resolve and locate functions."""
from __future__ import with_statement  # python2.5 backward compatibility.
import os
import re
import sys
import shutil
import tempfile
import unittest
import textwrap
from inspect import getsourcefile

from whereis import resolve, locate


def write_to_file(filepath, data=''):
    """Create the file in ``path`` and write ``data`` in it."""
    if isinstance(filepath, (tuple, list)):
        filepath = os.path.join(*filepath)
    with open(filepath, 'w') as file_:
        file_.write(data)


# Monkey patch unittest.TestCase with a simple version of assertRegexpMatches
# that exist in python2.7 and above.
def assertRegexpMatches(self, text, regexp):
    """Fail the test unless the text matches the regular expression."""
    if not re.match(regexp, text):
        msg = "Regexp didn't match: %r not found in %r" % (regexp, text)
        raise self.failureException(msg)

unittest.TestCase.assertRegexpMatches = assertRegexpMatches


class PyWhereisTestCase(unittest.TestCase):
    """TestCase class for the functions locate, resolve."""

    def test_builtin_packages(self):
        """Test built-in resolving module and package."""
        self.assertEqual(resolve('sys'), sys)
        self.assertEqual(resolve('os'), os)
        self.assertEqual(resolve('os.path'), os.path)

        self.assertEqual(locate('sys'), None)
        self.assertEqual(locate('sys', 1), 'Error: %r is built-in.' % sys)
        self.assertEqual(locate('os'), getsourcefile(os))
        self.assertEqual(locate('os.path'), getsourcefile(os.path))

    def test_buitlin_modules_member(self):
        """Test built-in module members (functions, class, method ...)"""
        self.assertEqual(resolve('unittest.TestCase'), unittest.TestCase)
        from inspect import ismodule
        self.assertEqual(resolve('inspect.ismodule'), ismodule)
        from os.path import abspath
        self.assertEqual(resolve('os.path.abspath'), abspath)

        # Match the file path + the line number.
        regexp = '%s \d+'
        self.assertRegexpMatches(locate('unittest.TestCase'),
                                 regexp % getsourcefile(unittest.TestCase))
        self.assertRegexpMatches(locate('inspect.ismodule'),
                                 regexp % getsourcefile(ismodule))
        self.assertRegexpMatches(locate('os.path.abspath'),
                                 regexp % getsourcefile(abspath))

    def test_user_modules(self):
        """Test user defined modules and their members."""
        # Create a package structure to test with.
        tmpdir = tempfile.mkdtemp()
        os.makedirs(os.path.join(tmpdir, 'a', 'b'))
        write_to_file((tmpdir, 'a', '__init__.py'))
        write_to_file((tmpdir, 'a', 'b', '__init__.py'))
        write_to_file((tmpdir, 'a', 'b', 'c.py'), 'class Foo: pass')
        write_to_file((tmpdir, 'a', 'b', 'd.py'), 'raise ImportError')
        code = textwrap.dedent("""
        class FooBar:
            class Bar:
                def baz(self):
                    pass
        """)
        write_to_file((tmpdir, 'a', 'b', 'e.py'), code)

        # To temove the temp package w/o self.addCleanup (python 2.6, 2.5).
        try:
            sys.path.append(tmpdir)
            self.assertEqual(resolve('a.b').__name__, 'a.b')
            self.assertEqual(resolve('a.b.c.Foo').__name__, 'Foo')
            self.assertEqual(resolve('a.b.e.FooBar.Bar.baz').__name__, 'baz')

            # locate should find module/packge even if the import will fail.
            self.assertEqual(locate('a.b.d'), os.path.join(tmpdir, 'a/b/d.py'))
            # The path returned should always be absolute.
            filepath = locate('a.b.e.FooBar.Bar.baz').split()[0]
            if not os.path.isabs(filepath):
                raise self.failureException('Path returned is not absolute.')
        finally:
            shutil.rmtree(tmpdir)

    def test_nonexistant_modules(self):
        """Test modules that don't exist."""
        self.assertRaises(ImportError, resolve, 'a.nonexistant')
        self.assertRaises(ImportError, resolve, 'in-va-li.d name')
        self.assertRaises(ImportError, resolve, '...w.ei.rd...name')
        self.assertRaises(ImportError, resolve, '')
        self.assertRaises(ImportError, resolve, '........')
        self.assertRaises(ImportError, resolve, '....sys....')

        self.assertEqual(locate('a.nonexistant'), None)
        self.assertEqual(locate('a.nonexistant', 1),
                         'Error: object a.nonexistant not found.')
        self.assertEqual(locate('in-va-li.d name'), None)
        self.assertEqual(locate('...w.ei.rd...name'), None)


if __name__ == '__main__':
    unittest.main()
