#! /usr/bin/env python
# -*- encoding: utf8 -*-
"""Test Cases for whereis package."""
from __future__ import with_statement  # python2.5 backward compatibility.
import os
import re
import sys
import shutil
import zipfile
import tempfile
import unittest
import textwrap
import contextlib
from inspect import getsourcefile

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO  # For python3.

from whereis import resolve, locate, LocateError, main, __doc__ as usage_string


def write_to_file(filepath, data=''):
    """Create the file in ``path`` and write ``data`` in it."""
    if isinstance(filepath, (tuple, list)):
        filepath = os.path.join(*filepath)
    with open(filepath, 'w') as file_:
        file_.write(data)

@contextlib.contextmanager
def capture_output(stdout=True, stderr=False):
    """Context manager for capturing stdout, stderr in ``StringIO`` instance
    and Yield the two captured file object.

    Arguments:
       - stdout: Set to True to capture stdout (default True).
       - stderr: Set To True to caputre stderr (default False).
    Yield:
       A tuple (stdout, stderr).

    """
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    if stdout:
        sys.stdout = stdout = StringIO()
    if stderr:
        sys.stderr = stderr = StringIO()

    try:
        yield stdout, stderr
    finally:
        # Flush and return to the begining of file object to be able to read it.
        if isinstance(stdout, StringIO):
            stdout.flush()
            stdout.seek(0)
        if isinstance(stderr, StringIO):
            stderr.flush()
            stderr.seek(0)
        # Recover original stdout and stderr.
        sys.stdout = original_stdout
        sys.stderr = original_stderr


# Monkey patch unittest.TestCase with a simple version of assertRegexpMatches
# that exist in python2.7 and above.
def assertRegexpMatches(self, text, regexp):
    """Fail the test unless the text matches the regular expression."""
    if not re.match(regexp, text):
        msg = "Regexp didn't match: %r not found in %r" % (regexp, text)
        raise self.failureException(msg)

unittest.TestCase.assertRegexpMatches = assertRegexpMatches


class PyWhereisTestCase(unittest.TestCase):
    """TestCase class for the functions locate, resolve, main."""

    def test_builtin_packages(self):
        """Test built-in resolving module and package."""
        self.assertEqual(resolve('sys'), sys)
        self.assertEqual(resolve('os'), os)
        self.assertEqual(resolve('os.path'), os.path)

        self.assertRaises(LocateError, locate, 'sys')
        self.assertRaises(LocateError, locate, 'sys')
        self.assertEqual(locate('os'), getsourcefile(os))
        self.assertEqual(locate('os.path'), getsourcefile(os.path))

    def test_buitlin_modules_member(self):
        """Test stdlib module members (functions, class, method ...)."""
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

        # Use try/finally to be able to remove the temp package w/o having to
        # use self.addCleanup which is not available in python 2.6 and below.
        try:
            sys.path.insert(0, tmpdir)
            self.assertEqual(resolve('a.b').__name__, 'a.b')
            self.assertEqual(resolve('a.b.c.Foo').__name__, 'Foo')
            self.assertEqual(resolve('a.b.e.FooBar.Bar.baz').__name__, 'baz')

            # locate should find module/package even if the import will fail.
            self.assertEqual(locate('a.b.d'), os.path.join(tmpdir, 'a/b/d.py'))
            # The path returned should always be absolute.
            filepath = locate('a.b.e.FooBar.Bar.baz').split()[0]
            if not os.path.isabs(filepath):
                raise self.failureException('Path returned is not absolute.')
        finally:
            shutil.rmtree(tmpdir)

    def test_broken_module(self):
        """Test broken module/package resolve."""
        tmpdir = tempfile.mkdtemp()
        # The module a.py will raise a SyntaxError when imported/executed.
        module_path = os.path.join(tmpdir, 'a.py')
        write_to_file(module_path, 'raise SyntaxError')

        try:
            sys.path.insert(0, tmpdir)
            self.assertRaises(ImportError, resolve, 'a')
            self.assertRaises(ImportError, resolve, 'a.something')
            # Locate the module should work just fine.
            self.assertEqual(locate('a'), module_path)
            # But member of the module will fail.
            self.assertRaises(LocateError, locate, 'a.something')
        finally:
            shutil.rmtree(tmpdir)

    def test_script_call(self):
        """Test calling pywhereis script.

        In this test function instead of calling the script in a subprocess,
        we will can the main function passing to it the right parameters as
        if it was called using the script ``pywhereis``.

        """
        # Calling main (script) to locate stdlib os module.
        with capture_output() as output:
            main(['os'])

        stdlib_os_path = output[0].read()
        self.assertEqual(stdlib_os_path, 'os: %s\n' % getsourcefile(os))

        tmpdir = tempfile.mkdtemp()
        # Save the current directory to be able to go back to it.
        test_dir = os.path.abspath(os.curdir)
        # Change the current directory to the temporary directory to be able
        # to check the -s/--site-packages option .
        os.chdir(tmpdir)
        # Create a new os module in the temporary directory.
        new_os_path = os.path.join(tmpdir, 'os.py')
        write_to_file(new_os_path)
        try:
            with capture_output() as output:
                main(['os'])
            self.assertEqual(output[0].read(), 'os: %s\n' % new_os_path)

            # When using the -s option the return value should be stdlib os.
            with capture_output() as output:
                main(['-s', 'os'])
            self.assertEqual(output[0].read(), stdlib_os_path)
        finally:
            # Go back to the test directory before removing the current dir
            # else the location of the dotted_name will fail.
            os.chdir(test_dir)
            shutil.rmtree(tmpdir)

        # Test the help argument.
        with capture_output(stderr=True) as output:
            main(['-h'])
        self.assertEqual(output[1].read(), usage_string)

        # Test the verbose argument.
        with capture_output() as output:
            main(['-v', 'sys'])
        self.assertEqual(output[0].read(),'sys: Error: %r is built-in.\n' % sys)

        # Call main (script) with no dotted_name.
        with capture_output(stderr=True) as output:
            main([])
        self.assertEqual(output[1].read(),
                         'Error: No name was given.\n\n%s' % usage_string)

        # Call main with invalid argument.
        with capture_output(stderr=True) as output:
            main(['--invalidargument'])
        err_msg = 'option --invalidargument not recognized'
        self.assertEqual(output[1].read(),
                        'Error: %s\n\n%s' % (err_msg, usage_string))

    def test_nonexistant_modules(self):
        """Test modules that don't exist."""
        self.assertRaises(ImportError, resolve, '')
        self.assertRaises(ImportError, resolve, 'a.nonexistant')
        self.assertRaises(ImportError, resolve, 'in-va-li.d name')
        self.assertRaises(ImportError, resolve, '...w.ei.rd...name')
        self.assertRaises(ImportError, resolve, '')
        self.assertRaises(ImportError, resolve, '........')
        self.assertRaises(ImportError, resolve, '....sys....')

        self.assertRaises(LocateError, locate, '')
        self.assertRaises(LocateError, locate, 'a.nonexistant')
        self.assertRaises(LocateError, locate, 'a.nonexistant')
        self.assertRaises(LocateError, locate, 'in-va-li.d name')
        self.assertRaises(LocateError, locate, '...w.ei.rd...name')

    def test_zip_archives(self):
        """Test importing dotted_name from zip/eggs archives."""
        tmpdir = tempfile.mkdtemp()
        # Create a test module to use to test zip import.
        test_module = 'foo.py'
        write_to_file((tmpdir, test_module), 'def bar(): pass')
        # Locate to tmpdir to be able to add foo.py without all parent dirs.
        os.chdir(tmpdir)
        # Create a zip archive and add the python module to it.
        zip_filepath = os.path.join(tmpdir, 'a.zip')
        zip_fp = zipfile.ZipFile(zip_filepath, 'w')
        zip_fp.write(test_module)
        zip_fp.close()
        # Remove the test module to be able to import the one from the zip.
        os.remove(test_module)

        try:
            # Add the zip to sys.path be be able to importe module inside it.
            module_fullpath = os.path.join(zip_filepath, test_module)
            sys.path.insert(0, zip_filepath)
            self.assertEqual(locate('foo'), module_fullpath)
            self.assertEqual(locate('foo.bar'), '%s 1' % module_fullpath)
        finally:
            shutil.rmtree(tmpdir)


if __name__ == '__main__':
    unittest.main()
