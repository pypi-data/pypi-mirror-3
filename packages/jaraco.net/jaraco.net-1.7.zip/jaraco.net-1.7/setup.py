# -*- coding: UTF-8 -*-

"""
Setup script for building jaraco.net

Copyright © 2009-2011 Jason R. Coombs
"""

import sys

try:
	from distutils.command.build_py import build_py_2to3 as build_py
	# exclude some fixers that break already compatible code
	from lib2to3.refactor import get_fixers_from_package
	fixers = get_fixers_from_package('lib2to3.fixes')
	for skip_fixer in ['import']:
		fixers.remove('lib2to3.fixes.fix_' + skip_fixer)
	build_py.fixer_names = fixers
except ImportError:
	from distutils.command.build_py import build_py

from setuptools import find_packages

name = 'jaraco.net'

py26reqs = ['argparse'] if sys.version_info < (2,7) else []

setup_params = dict(
	name = name,
	use_hg_version=dict(increment='0.1'),
	description = 'Networking tools by jaraco',
	long_description = open('README').read(),
	author = 'Jason R. Coombs',
	author_email = 'jaraco@jaraco.com',
	url = 'http://bitbucket.org/jaraco/' + name,
	packages = find_packages(),
	namespace_packages = ['jaraco',],
	license = 'MIT',
	classifiers = [
		"Development Status :: 4 - Beta",
		"Intended Audience :: Developers",
		"Programming Language :: Python",
	],
	entry_points = {
		'console_scripts': [
			'whois-bridge = jaraco.net.whois:main',
			'scanner = jaraco.net.scanner:scan',
			'fake-http = jaraco.net.http:start_simple_server',
			'fake-http-auth = jaraco.net.http:auth_request_server',
			'wget = jaraco.net.http:wget',
			'serve-local = jaraco.net.http.static:serve_local',
			'fake-smtp = jaraco.net.smtp:start_simple_server',
			'udp-send = jaraco.net.udp:Sender',
			'udp-echo = jaraco.net.udp:EchoServer',
			'dns-forward-service = jaraco.net.dns:start_service',
			'dnsbl-check = jaraco.net.dnsbl:handle_cmdline',
			'ntp = jaraco.net.ntp:handle_command_line',
			'remove-known-spammers = jaraco.net.email:remove_known_spammers',
			'tcp-test-connect = jaraco.net.tcp:test_connect',
			'tcp-echo-server = jaraco.net.tcp:start_echo_server',
			'http-headers = jaraco.net.http:headers',
			'build-dir-index = jaraco.net.site:make_index_cmd',
			'content-type-reporter = jaraco.net.http.content:ContentTypeReporter.run',
			'web-tail = jaraco.net.tail:handle_command_line',
			],
	},
	install_requires=[
		'jaraco.util>=4.0dev',
		'clientform>=0.2.7',
		'BeautifulSoup',
	] + py26reqs,
	extras_require = {
	},
	dependency_links = [
	],
	tests_require=[
	],
	cmdclass=dict(build_py=build_py),
	setup_requires = [
		'hgtools>=0.6.4',
	],
)

if __name__ == '__main__':
	from setuptools import setup
	setup(**setup_params)
