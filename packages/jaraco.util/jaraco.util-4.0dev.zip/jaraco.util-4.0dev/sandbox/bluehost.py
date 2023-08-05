"""
Fabric recipes for bluehost
"""

import urllib2
import os
import sys
import types
import contextlib

from fabric.api import run, cd
from fabric.contrib import files

@contextlib.contextmanager
def _tarball_context(url):
	"""
	Get a tarball, extract it, change to that directory, yield, then
	clean up.
	"""
	build_dir = os.path.basename(url).replace('.tar.gz', '').replace(
		'.tgz', '')
	run('wget {url} -O - | tar xz'.format(**vars()))
	try:
		with cd(build_dir):
			yield build_dir
	finally:
		run('rm -R {build_dir}'.format(**vars()))

def _url_module_import(url):
	"""
	Grab a python file from a URL and import it as a module
	"""
	data = urllib2.urlopen(url).read()
	name = os.path.basename(url)
	name, ext = os.path.splitext(name)
	module = sys.modules.setdefault(name, types.ModuleType(name))
	module.__file__ = url
	exec data in module.__dict__
	return module

def install_distribute():
	"""
	Install distribute (setuptools) into the user's .local profile
	"""
	# get the latest version info from the installer_script
	distribute_setup = _url_module_import('http://python-distribute.org/distribute_setup.py')
	download_url = '{DEFAULT_URL}distribute-{DEFAULT_VERSION}.tar.gz'.format(**vars(distribute_setup))
	#prefix = '--prefix={prefix}'.format(**vars()) if prefix else ''
	with _tarball_context(download_url):
		run('python2.6 setup.py install --user')

def install_cherrypy(url_base = '/cp'):
	"""
	Install a CherryPy application as a FCGI application on `url_base`.
	"""
	run('.local/bin/easy_install cherrypy')
	run('.local/bin/easy_install flup')
	
	url_base = url_base.strip('/')
	# set up the FCGI handler
	files.append('public_html/.htaccess', [
		'AddHandler fcgid-script .fcgi',
		'RewriteRule ^{url_base}/(.*)$ /cgi-bin/cherryd.fcgi/$1 [last]'.format(**vars()),
	])
	# install the cherrypy conf
	files.append('public_html/cgi-bin/cherryd.conf', [
		'[global]',
		'server.socket_file=None',
		'server.socket_host=None',
		'server.socket_port=None',
	])
	
	# install the cherrypy fcgi handler
	files.append('public_html/cgi-bin/cherryd.fcgi', [
		'#!/bin/sh',
		'~/.local/bin/cherryd -P modules -c cherryd.conf -f -i app',
	])
	run('chmod 755 public_html/cgi-bin/cherryd.fcgi')
	
	run('mkdir -p public_html/cgi-bin/modules')
	files.append('public_html/cgi-bin/modules/app.py', [
		'import cherrypy',
		'class Application:',
		'\t"Define your application here"',
		'cherrypy.tree.mount(Application(), "/cgi-bin/cherryd.fcgi")',
	])
