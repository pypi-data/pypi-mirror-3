import sys
from socket import *

class EchoServer(object):
	def __init__(self):
		options, args = self.get_options()
		if args:
			raise RuntimeError, 'Incorrect arguments'
		self.serve(options)

	def get_options(self):
		from optparse import OptionParser
		parser = OptionParser()
		parser.add_option("-p", "--port",
						   help="listen on this port", type="int",
						   default=9999)
		return parser.parse_args()

	def serve(self, options):
		host = ''
		port = options.port
		infos = getaddrinfo(host, port)
		(family, socktype, proto, canonname, sockaddr) = infos[0]
		s = socket(family, SOCK_DGRAM)
		s.settimeout(1)
		s.bind(('', options.port))
		while True:
			try:
				res, addr = s.recvfrom(1024)
				print res, addr
			except timeout:
				pass
			except KeyboardInterrupt:
				break

class Sender(object):
	def __init__(self):
		self.options, args = self.get_options()
		if len(args) != 0:
			raise RuntimeError, 'Bad arguments provided'
		self.send_message()
		
	def send_message(self):
		host, port = self.options.connect.split(':')
		infos = getaddrinfo(host, port)
		(family, socktype, proto, canonname, sockaddr) = infos[0]
		self.sockaddr = sockaddr
		s = socket(family, SOCK_DGRAM)
		s.connect(sockaddr)
		s.send(self.options.message)
		s.close()

	def get_options(self):
		from optparse import OptionParser
		parser = OptionParser()
		parser.add_option("-m", "--message",
						   help="send this message", default="message!")
		parser.add_option('-c', '--connect',
						   help="host:port to connect to",
						   default="localhost:9999")
		return parser.parse_args()

	def __repr__(self):
		return 'message sent to %(sockaddr)s' % self.__dict__
		