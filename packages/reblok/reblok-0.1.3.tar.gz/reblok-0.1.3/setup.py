#!/usr/bin/env python
# -*- coding: utf8 -*-
__version__ = "$Revision: 272 $ $Date: 2011-10-07 12:17:24 +0200 (ven. 07 oct. 2011) $"
__author__  = "Guillaume Bour <guillaume@bour.cc>"
__license__ = """
	Copyright (C) 2010-2011, Guillaume Bour <guillaume@bour.cc>

	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU Affero General Public License as
	published by the Free Software Foundation, version 3.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU Affero General Public License for more details.

	You should have received a copy of the GNU Affero General Public License
	along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import subprocess
#from distutils.core import setup, Command
from setuptools import setup, Command

class BuildDebianPackage(Command):
	description = "Build debian package"
	user_options = []

	def run(self):
		subprocess.call(['dpkg-buildpackage'])


setup(
	name         = 'reblok',
	version      = '0.1.3',
	description  = 'Python decompiler',
	author       = 'Guillaume Bour',
	author_email = 'guillaume@bour.cc',
	url          = 'http://devedge.bour.cc/wiki/Reblok',
	download_url = 'http://devedge.bour.cc/resources/reblok/src/reblok.latest.tar.gz',
	license      = 'GNU General Public License v3',
	classifiers  = [
		'Development Status :: 4 - Beta',
		'Environment :: Console',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: GNU Affero General Public License v3',
		'License :: OSI Approved :: GNU General Public License (GPL)',
		'Natural Language :: English',
		'Natural Language :: French',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Programming Language :: Python :: 2.5',
		'Programming Language :: Python :: 2.6',
		'Programming Language :: Python :: 2.7',
		'Topic :: Software Development',
		'Topic :: Software Development :: Disassemblers',
		'Topic :: Software Development :: Libraries :: Python Modules',
		'Topic :: Utilities',
	],

	long_description = """Reblok build an Abstract Syntax Tree (AST) from python bytecode

Example::

	>>> from reblok import Parser
	>>> add = lambda x: x + 1
	>>> print Parser().walk(add)
	['function', '<lambda>', [['ret', ('add', ('var', 'x', 'local'), ('const', 1))]], [('x', '<undef>')], None, None, [], {}]
	""",

	scripts=['bin/reblok'],
	packages=['reblok'],
	data_files=[('share/doc/python-reblok', ('README.md','AUTHORS','COPYING'))],
	install_requires=['byteplay >= 0.2'],

	cmdclass={'bdist_deb': BuildDebianPackage}
)
