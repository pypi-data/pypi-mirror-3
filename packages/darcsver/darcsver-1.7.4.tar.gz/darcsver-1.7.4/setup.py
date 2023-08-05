#!/usr/bin/env python
# -*- coding: utf-8 -*-

# darcsver -- generate a version number from darcs history
#
# Copyright © 2007-2012 Zooko Wilcox-O'Hearn

# Permission is hereby granted to any person obtaining a copy of this work to
# deal in this work without restriction (including the rights to use, modify,
# distribute, sublicense, and/or sell copies).

import os, re, sys

from setuptools import find_packages, setup

trove_classifiers=[
    "Framework :: Setuptools Plugin",
    "Development Status :: 5 - Production/Stable",
    "License :: OSI Approved :: BSD License",
    "License :: DFSG approved",
    "Intended Audience :: Developers",
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
    ]

PKG='darcsver'
VERSIONFILE = os.path.join(PKG, "_version.py")
verstr = "unknown"
try:
    verstrline = open(VERSIONFILE, "rt").read()
except EnvironmentError:
    pass # Okay, there is no version file.
else:
    VSRE = r"^verstr = ['\"]([^'\"]*)['\"]"
    mo = re.search(VSRE, verstrline, re.M)
    if mo:
        verstr = mo.group(1)
    else:
        print "unable to find version in %s" % (VERSIONFILE,)
        raise RuntimeError("if %s.py exists, it must be well-formed" % (VERSIONFILE,))

data_fnames=[ 'README.rst' ]

# In case we are building for a .deb with stdeb's sdist_dsc command, we put the
# docs in "share/doc/python-$PKG".
doc_loc = "share/doc/python-" + PKG
data_files = [(doc_loc, data_fnames)]

tests_require=[
    # Mock - Mocking and Testing Library
    # http://www.voidspace.org.uk/python/mock/
    "mock",
    ]

setup_requires=[]
if 'trial' in sys.argv:
    tests_require.append('setuptools_trial')
    setup_requires.append('setuptools_trial')

readmetext = open('README.rst').read()
if readmetext[:3] == '\xef\xbb\xbf':
    # utf-8 "BOM"
    readmetext = readmetext[3:].decode('utf-8')

setup(name='darcsver',
      version=verstr,
      description='generate a version number from darcs history',
      long_description=readmetext,
      author='Zooko O\'Whielacronx',
      author_email='zooko@zooko.com',
      url='https://tahoe-lafs.org/trac/' + PKG,
      license='BSD',
      packages=find_packages(),
      include_package_data=True,
      data_files=data_files,
      classifiers=trove_classifiers,
      keywords='distutils setuptools plugin setup darcs',
      entry_points = {
        'console_scripts': [ 'darcsver = scripts.darcsverscript:main' ],
        'distutils.commands': [ 'darcsver = darcsver.setuptools_command:DarcsVer', ],
        'distutils.setup_keywords': [
            "versionfiles = darcsver.setuptools_command:validate_versionfiles",
            "versionbodies = darcsver.setuptools_command:validate_versionbodies",
        ],
        },
      setup_requires=setup_requires,
      test_suite=PKG+'.test',
      tests_require=tests_require,
      zip_safe=False, # I prefer unzipped for easier access.
      )
