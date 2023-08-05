# -*- coding: UTF-8 -*-

"""
IPTools
Tools for IP communication.

Objects:
	PortScanner: scans a range of ports
	PortListener: listens on a port
	PortRangeListener: listens on a range of ports
	
Copyright © 2004-2009 Jason R. Coombs
"""

__author__ = 'Jason R. Coombs <jaraco@jaraco.com>'
__version__ = '$Revision$a'[11:-2]
__svnauthor__ = '$Author$'[9:-2]
__date__ = '$Date$'[7:-2]

import threading, socket, sys, operator, time

import logging
log = logging.getLogger('IP Tools')

class PortScanner(object):
	def __init__(self):
		self.ranges = [range(1, 1024)]
		self.nThreads = 100
		
	def SetRange(self, *r):
		self.ranges = [range(*r)]

	def AddRange(self, *r):
		self.ranges.append(range(*r))

class ScanThread(threading.Thread):
	allTesters = []
	
	def __init__(self, address):
		threading.Thread.__init__(self)
		self.address = address
		
	def run(self):
		ScanThread.allTesters.append(self)
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			s.connect(self.address)
			s.close()
			self.result = True
		except socket.error:
			self.result = False
		
		self.report()

	def __str__(self):
		resultMsg = {
			True: '%(address)s connection established.',
			False: '%(address)s connection failed.',
			None: '%(address)s no result obtained.'}
		resultMsg = resultMsg[getattr(self,'result',None)]
		return resultMsg % vars(self)
		
	def report(self):
		log_method = {
			True: log.info,
			False: log.debug,
			None: log.error}
		log_method = log_method[getattr(self,'result',None)]
		log_method(str(self))

	def waitForTestersToFinish():
		map(lambda x: x.join(), ScanThread.allTesters)
	waitForTestersToFinish = staticmethod(waitForTestersToFinish)

def portscan_hosts(hosts, *args, **kargs):
	map(lambda h: portscan(h, *args, **kargs), hosts)

def portscan(host, ports = range(1024), frequency = 20):
	makeAddress = lambda port: (host, port)
	addresses = map(makeAddress, ports)
	testers = map(ScanThread, addresses)
	for tester in testers:
		log.debug('starting tester')
		tester.start()
		time.sleep(1.0/frequency)
		
class PortListener(threading.Thread):
	def __init__(self, port):
		threading.Thread.__init__(self)
		self.port = port
		self.setDaemon(1)
		self.output = sys.stdout
		
	def run(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			s.bind(('', self.port))
			s.listen(1)
			while 1:
				conn, addr = s.accept()
				self.output.write('Received connection on %d from %s.\n' % (self.port, str(addr)))
				conn.close()
		except socket.error, e:
			if e[0] == 10048:
				self.output.write('Cannot listen on port %d: Address already in use.\n' % self.port)
			else: raise

class PortRangeListener(object):
	def __init__(self):
		self.ranges = [range(1, 1024)]

	def Listen(self):
		ports = reduce(operator.add, self.ranges)
		ports.sort()
		self.threads = map(PortListener, ports)
		map(lambda t: t.start(), self.threads)

def ping_host(host):
	x = os.system("ping %s -n 1" % host)
	if x:
		print("Either %s is offline, or ping request has been blocked." %ip)
	else:
		print("%s is online." %ip)
		