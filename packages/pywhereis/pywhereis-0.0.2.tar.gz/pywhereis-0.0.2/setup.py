"""Setup/installation script."""
import os
from distutils.core import setup

import whereis


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name='pywhereis',
    description='Unix whereis-like python script and package to find the '
                'source file of python object (package, module, function, '
                'class ...).',
    long_description='\n' + read('README.rst'),
    license=whereis.__license__,
    version=whereis.__version__,
    author=whereis.__author__,
    author_email='mouadino@gmail.com',
    url='https://bitbucket.org/mouad/pywhereis',
    platforms='Cross Platform',
    keywords = 'file source object dotted name automatic discovery',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities'
    ],
    packages=['whereis'],
    scripts=['scripts/pywhereis']
)
