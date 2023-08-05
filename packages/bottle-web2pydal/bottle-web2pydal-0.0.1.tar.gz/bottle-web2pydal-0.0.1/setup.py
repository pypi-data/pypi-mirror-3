#!/usr/bin/env python

"""
python setup.py sdist upload
"""

import sys
import os
from distutils.core import setup

try:
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
    from distutils.command.build_py import build_py

# This ugly hack executes the first few lines of the module file to look up some
# common variables. We cannot just import the module because it depends on other
# modules that might not be installed yet.
filename = os.path.join(os.path.dirname(__file__),\
                     'bottle_web2pydal/bottle_dal.py')
source = open(filename).read().split('### CUT HERE')[0]
exec(source)

setup(
    name='bottle-web2pydal',
    version=__version__,
    description='Web2py Dal integration in Bottle Framework.',
    long_description=__doc__,
    author='Martin Mulone',
    author_email='martin@tecnodoc.com.ar',
    url='http://bottleweb2py.tecnodoc.com.ar',
    license=__license__,
    platforms='any',
    packages=['bottle_web2pydal',
              'bottle_web2pydal.contrib',
              'bottle_web2pydal.contrib.markmin',
              'bottle_web2pydal.contrib.markdown'],
    requires=[
        'bottle (>=0.9)',
        'simplejson'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    cmdclass={'build_py': build_py}
)
