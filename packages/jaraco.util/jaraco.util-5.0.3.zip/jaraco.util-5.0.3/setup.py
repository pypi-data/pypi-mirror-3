# -*- coding: UTF-8 -*-

"""
Setup script for building jaraco.util distribution

Copyright © 2004-2011 Jason R. Coombs
"""

from __future__ import unicode_literals

import sys

from setuptools import find_packages, Command

class PyTest(Command):
	user_options = []

	def initialize_options(self):
		pass

	def finalize_options(self):
		pass

	def run(self):
		import py.test
		raise SystemExit(py.test.main(args=[]))

name = 'jaraco.util'

setup_params = dict(
	# convert to bytes to work around UnicodeDecodeError when using bdist --formats gztar
	name = str(name),
	use_hg_version=True,
	description = 'General utility modules that supply commonly-used functionality',
	long_description = open('README').read(),
	author = 'Jason R. Coombs',
	author_email = 'jaraco@jaraco.com',
	url = 'http://pypi.python.org/pypi/' + name,
	packages = find_packages(exclude=['tests']),
	# convert to bytes to work around TypeError when installed with PIP
	# https://github.com/pypa/pip/issues/449
	namespace_packages = [str('jaraco')],
	license = 'MIT',
	classifiers = [
		"Development Status :: 5 - Production/Stable",
		"Intended Audience :: Developers",
		"Programming Language :: Python :: 2.6",
		"Programming Language :: Python :: 2.7",
		"Programming Language :: Python :: 3",
	],
	entry_points = {
		'console_scripts': [
			'roll-dice = jaraco.util.dice:do_dice_roll',
			'calc-prorate = jaraco.dateutil:calculate_prorated_values',
			],
	},
	install_requires=[
	],
	extras_require = {
		'image':
			['pil>=1.1.6'],
	},
	dependency_links = [
	],
	tests_require=[
		'pytest>=2',
	],
	setup_requires=[
		'hgtools>=0.4',
	],
	cmdclass=dict(
		test=PyTest,
	),
	use_2to3=True,
	use_2to3_exclude_fixers=['lib2to3.fixes.fix_import'],
)

if __name__ == '__main__':
	from setuptools import setup
	import pkg_resources
	if sys.version_info >= (3,):
		# distribute 0.6.24 is required to exclude the fixers
		pkg_resources.require('distribute>=0.6.24dev')
	setup(**setup_params)
