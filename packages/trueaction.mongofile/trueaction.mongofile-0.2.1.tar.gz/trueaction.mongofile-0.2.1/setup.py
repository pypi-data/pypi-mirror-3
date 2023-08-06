#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Install trueaction.mongofile.
"""

from os.path import join
from setuptools import setup, find_packages

CLASSIFIERS = [
	'Development Status :: 2 - Pre-Alpha',
	'Intended Audience :: Developers',
	'License :: OSI Approved :: Academic Free License (AFL)',
	'Operating System :: OS Independent',
	'Programming Language :: Python',
	'Topic :: Database',
	'Topic :: System :: Filesystems',
]
# tests_require is not always available in setup(), so we implement it a couple ways.
TESTS_REQUIRE = [
	'nosetests',
]
setup(
	name                 = 'trueaction.mongofile',
	version              = open(join('docs','VERSION.txt')).read().strip(),
	description          = 'A way to read, write, and append file-like objects to MongoDB',
	long_description     = open('README.txt').read() + '\n' + open(join('docs', 'HISTORY.txt')).read(),
	classifiers          = CLASSIFIERS,
	keywords             = 'TrueAction Python MongoDB Files',
	author               = 'Michael A. Smith',
	author_email         = 'smithm@trueaction.com',
	url                  = 'http://trueaction.com',
	license              = 'http://opensource.org/licenses/academic.php',
	packages             = find_packages(exclude=['ez_setup']),
	include_package_data = True,
	zip_safe             = True,
	tests_require        = TESTS_REQUIRE,
	extras_require       = {'test': TESTS_REQUIRE,},
	install_requires     = ['pymongo'],
	entry_points         = {'console_scripts': []},
)
