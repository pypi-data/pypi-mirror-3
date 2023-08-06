#!/usr/bin/env python

# setuptools plugin for pyflakes
# Author: Zooko O'Whielacronx

# Permission is hereby granted to any person obtaining a copy of this work to
# deal in this work without restriction (including the rights to use, modify,
# distribute, sublicense, and/or sell copies).

# See README.rst for instructions.

# Thanks to Ian Bicking for his buildutils plugin -- I copied liberally from
# that code to form this code.  Thanks to the authors of pyflakes and
# setuptools.

import os, re, sys

from setuptools import setup, find_packages

trove_classifiers=[
    "Framework :: Setuptools Plugin",
    "Development Status :: 5 - Production/Stable",
    "License :: OSI Approved :: BSD License",
    "License :: DFSG approved",
    "Intended Audience :: Developers",
    "Operating System :: Microsoft",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: Unix",
    "Operating System :: POSIX :: Linux",
    "Operating System :: POSIX",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: Microsoft :: Windows :: Windows NT/2000",
    "Operating System :: OS Independent",
    "Natural Language :: English",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.4",
    "Programming Language :: Python :: 2.5",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Topic :: Utilities",
    "Topic :: Software Development :: Libraries",
    "Framework :: Setuptools Plugin",
    ]

PKG='setuptools_pyflakes'
VERSIONFILE = os.path.join(PKG, "_version.py")
verstr = "unknown"
VSRE = re.compile("^verstr = ['\"]([^'\"]*)['\"]", re.M)
try:
    verstrline = open(VERSIONFILE, "rt").read()
except EnvironmentError:
    pass # Okay, there is no version file.
else:
    mo = VSRE.search(verstrline)
    if mo:
        verstr = mo.group(1)
    else:
        print "unable to find version in %s" % (VERSIONFILE,)
        raise RuntimeError("If %s.py exists, it is required to be well-formed." % (VERSIONFILE,))

setup_requires = []

# darcsver is needed only if you want "./setup.py darcsver" to write a new
# version stamp in pycryptopp/_version.py, with a version number derived from
# darcs history.  http://pypi.python.org/pypi/darcsver
if "darcsver" in sys.argv[1:]:
    setup_requires.append('darcsver >= 1.0.0')

readmetext = open('README.rst').read()
if readmetext[:3] == '\xef\xbb\xbf':
    # utf-8 "BOM"
    readmetext = readmetext[3:].decode('utf-8')

# distutils in Python 2.4 has a bug in that it tries to encode the long
# description into ascii. We detect the resulting exception and try again
# after squashing the long description (lossily) into ascii.


def _setup(longdescription):
    setup(
        name=PKG,
        version=verstr,
        description='setuptools plugin for pyflakes',
        long_description=longdescription,
        author="Zooko O'Whielacronx",
        author_email='zooko@zooko.com',
        url='https://tahoe-lafs.org/trac/' + PKG,
        license='BSD',
        setup_requires=setup_requires,
        install_requires=['pyflakes >= 0.3'],
        packages=find_packages(),
        include_package_data=True,
        classifiers=trove_classifiers,
        keywords='distutils setuptools setup pyflakes',
        entry_points={
            'distutils.commands': [ 'flakes = setuptools_pyflakes.setuptools_command:PyflakesCommand', ],
            },
        zip_safe=False, # I prefer unzipped for easier access.
        )

try:
    _setup(readmetext)
except UnicodeEncodeError:
    _setup(repr(readmetext))
