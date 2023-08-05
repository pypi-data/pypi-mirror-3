Summary
=======
Locate a python object (package, module, function, class ...) source file.

Usage
=====

   ``pywhereis [-v] dotted_name...``

CMD line Examples
=================

- The ``pywhereis`` script accept a package, module, function or a class ::

    $ pywhereis shlex
    shlex: /usr/lib/python2.6/shlex.py
    $ pywhereis os.path.abspath
    os.path.abspath: /usr/lib/python2.6/posixpath.py  337

- You can pass more than one dotted-name to it ::

    $ pywhereis shlex inspect.ismodule
    shlex: /usr/lib/python2.6/shlex.py
    inspect.ismodule: /usr/lib/python2.6/inspect.py  51

- If the name is a function, class or method the result will contain the line
  number where the object is defined ::

    $ pywhereis unittest.TestCase.assertEqual
    unittest.TestCase.assertEqual: /usr/lib/python2.6/unittest.py  344

- It will **fail** localizing object that are not pure python ::

    $ pywhereis.py sys
    sys:

- For more info about why the localization fail you can use the verbose
  mode ::

    $ pywhereis -v sys
    sys: Error: <module 'sys' (built-in)> is built-in.

- Of course you can search in a different python version by running this
  script using that version ::
   
    $ python3.2 /path/to/pywhereis html
    html: /usr/local/lib/python3.2/html/__init__.py

- For python2.7 and above you can also do ::

    $ python2.7 -mwhereis subprocess.Popen
    subprocess.Popen: /usr/local/lib/python2.7/subprocess.py 33


Code Examples
=============

This package come also with a python package ``whereis`` that can be used like
so ::

    >>> import whereis
    >>> whereis.resolve('sys')
    <module 'sys' (built-in)>
    >>> whereis.locate('os')
    '/usr/lib/python2.6/os.py'
