#!/usr/bin/env python

from socket import *
import struct
import sys
import time
import logging
import argparse

from jaraco.util.string import trim
import jaraco.util.logging

log = logging.getLogger(__name__)

TIME1970 = 2208988800L		# Thanks to F.Lundh

def query(server, force_ipv6=False):
	timeout = 3
	ntp_port = 123

	family = AF_INET6 if force_ipv6 else 0
	sock_type = SOCK_DGRAM

	infos = getaddrinfo(server, ntp_port, family, sock_type)

	log.debug(infos)
	family, socktype, proto, canonname, sockaddr = infos[0]
	socktype = SOCK_DGRAM

	log.info('Requesting time from %(sockaddr)s' % vars())
	client = socket(family=family, type=socktype, proto=proto)
	client.settimeout(timeout)

	data = '\x1b' + 47 * '\0'
	client.sendto(data, sockaddr)
	data, address = client.recvfrom(1024)
	if data:
		log.info('Response received from: %s', address)
		t = struct.unpack('!12I', data)[10]
		t -= TIME1970
		log.info('\tTime=%s', time.ctime(t))

def handle_command_line():
	"""
	Query the NTP server for the current time.
	"""
	parser = argparse.ArgumentParser(usage=trim(handle_command_line.__doc__))
	parser.add_argument('-6', '--ipv6', help="Force IPv6", action="store_true", default=False)
	parser.add_argument('server', help="IP Address of server to query")
	jaraco.util.logging.add_arguments(parser)
	args = parser.parse_args()
	jaraco.util.logging.setup(args)
	logging.root.handlers[0].setFormatter(logging.Formatter("%(message)s"))
	query(args.server, args.ipv6)

if __name__ == '__main__': handle_command_line()