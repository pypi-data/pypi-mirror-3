#!python

# $Id$

import sys
import socket

def reverse_ip(ip):
	return '.'.join(reversed(ip.split('.')))

blocklist_servers = [
	'dnsbl.jaraco.com',
	'zen.spamhaus.org',
	'ips.backscatterer.org',
	'bl.spamcop.net',
	'list.dsbl.org',
]

def lookup_host(host):
	ip = socket.gethostbyname(host)

	result = False
	for bl in (blocklist_servers):
		lookup = '.'.join((reverse_ip(ip), bl))
		try:
			res = socket.gethostbyname(lookup)
			print host, 'listed with', bl, 'as', res
			result = True
		except socket.gaierror:
			pass
	return result

def handle_cmdline():
	lookup_host(sys.argv[1])

if __name__ == '__main__':
	handle_cmdline()