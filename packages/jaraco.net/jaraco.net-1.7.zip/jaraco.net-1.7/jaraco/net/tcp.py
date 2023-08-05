from __future__ import print_function

import socket
from optparse import OptionParser

from jaraco.util.string import local_format as lf

def get_connect_options():
	parser = OptionParser(conflict_handler="resolve")
	parser.add_option('-h', '--host', default='localhost')
	parser.add_option('-p', '--port', default=80, type='int')
	options, args = parser.parse_args()
	if not len(args) == 0:
		parser.error("Unexpected positional argument")
	return options

def test_connect():
	options = get_connect_options()
	addr = options.host, options.port
	family, socktype, proto, canonname, sockaddr = socket.getaddrinfo(*addr)[0]
	sock = socket.socket(family, socktype, proto)
	try:
		conn = sock.connect(sockaddr)
	except socket.error as e:
		print(e)
		raise SystemExit(1)
	args = vars(options)
	host, port = addr
	print(lf("Successfully connected to {host} on port {port}"))

def start_echo_server():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(('', 8099))
	s.listen(1)
	while True:
		conn, addr = s.accept()
		print('connected from', addr)
		while True:
			dat = conn.recv(4096)
			if not dat: break
			conn.send(dat)
