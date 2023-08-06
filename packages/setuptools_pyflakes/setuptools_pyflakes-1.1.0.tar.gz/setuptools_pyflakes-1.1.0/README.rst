

setuptools_pyflakes Manual
==========================

About
-----

This is a plugin for setuptools that integrates pyflakes.  Once installed,
"python setup.py flakes" will run pyflakes on all of the modules in your
project.


Installation
------------

With easy_install:

  easy_install setuptools_pyflakes

Alternative manual installation:

  tar -zxvf setuptools_pyflakes-X.Y.Z.tar.gz
  cd setuptools_pyflakes-X.Y.Z
  python setup.py install

Where X.Y.Z is a version number.


Usage
-----

To use this plugin, you must first package your python module with
`setup.py` and use setuptools.  The former is well documented in the
distutils manual:

  http://docs.python.org/dist/dist.html

To use setuptools instead of distutils, just edit `setup.py` and
change

  from distutils.core import setup

to

  from setuptools import setup

Then, if this plugin is installed, "python setup.py flakes" will work.


Automatically installing setuptools_pyflakes
--------------------------------------------

You can make sure that anyone who uses your setup.py, and who invokes "python
setup.py flakes", automatically gets this plugin installed, by adding a
`setup_requires` argument.::

  setup_requires=[]
  # setuptools_pyflakes is required to make "python setup.py flakes" work.
  if 'flakes' in sys.argv[1:]:
    setup_requires.append('setuptools_pyflakes')

  setup(...,
    setup_requires = setup_requires,
    ...)


References
----------

How to distribute Python modules with Distutils:

  http://docs.python.org/dist/dist.html


Setuptools documentation:

  http://peak.telecommunity.com/DevCenter/setuptools


Thanks to Yannick Gingras for providing the prototype for this
README.rst.
