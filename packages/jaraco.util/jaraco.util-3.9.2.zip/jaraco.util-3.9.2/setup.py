# -*- coding: UTF-8 -*-

"""
Setup script for building jaraco.util distribution

Copyright © 2004-2010 Jason R. Coombs
"""

import sys
import subprocess

from setuptools import find_packages, Command

import setuptools.command.build_py

def install_fixer_names():
	"""
	Distribute doesn't provide an exemption mechanism, so we need to build
	the full list as if distribute had done it, then we can skip the fixers
	we want to exempt.
	"""
	# if we're not on Python 3, do nothing - this routine can cause
	#  problems, so don't run it if we're not going to need it.
	if sys.version_info < (3,): return
	if not hasattr(setuptools, 'lib2to3_fixer_packages'): return
	names = getattr(setuptools.command.build_py.build_py, 'fixer_names', None) or []
	from lib2to3.refactor import get_fixers_from_package
	for p in setuptools.lib2to3_fixer_packages:
		names.extend(get_fixers_from_package(p))
	setuptools.command.build_py.build_py.fixer_names = names

def skip_fixer(fixer_name):
	names = getattr(setuptools.command.build_py.build_py, 'fixer_names', None)
	names and names.remove(fixer_name)

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
	name = name,
	use_hg_version=True,
	description = 'General utility modules that supply commonly-used functionality',
	long_description = open('README').read(),
	author = 'Jason R. Coombs',
	author_email = 'jaraco@jaraco.com',
	url = 'http://pypi.python.org/pypi/'+name,
	packages = find_packages(exclude=['tests']),
	namespace_packages = ['jaraco',],
	license = 'MIT',
	classifiers = [
		"Development Status :: 5 - Production/Stable",
		"Intended Audience :: Developers",
		"Programming Language :: Python",
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
)

if __name__ == '__main__':
	from setuptools import setup
	install_fixer_names()
	skip_fixer('lib2to3.fixes.fix_import')
	setup(**setup_params)
