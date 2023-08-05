#! -*- coding: UTF-8 -*-

"""whois_bridge.py

HTTP scraper for nic servers who only offer whois service via web only.

Run the script from the command line and it will service port 43 as a whois server,
passing the query to the appropriate web form and parsing the results into a textual format.

Copyright © 2005-2009 Jason R. Coombs
"""

__author__ = 'Jason R. Coombs <jaraco@jaraco.com>'
__version__ = '$Rev$'[6:-2]
__svnauthor__ = '$Author$'[9:-2]
__date__ = '$Date$'[7:-2]

import urllib2
import os
import re
import sys
from ClientForm import ParseResponse, ItemNotFoundError
from htmllib import HTMLParser
from formatter import NullFormatter, DumbWriter, AbstractFormatter
from jaraco.net.http import PageGetter
from jaraco.util.meta import LeafClassesMeta
from urllib import basejoin
import logging
from StringIO import StringIO
from BeautifulSoup import BeautifulSoup, UnicodeDammit

log = logging.getLogger(__name__)

try:
	import cookielib
	urlopen = urllib2.urlopen
except ImportError:
	from ClientCookie import urlopen

def init():
	"""Initialize HTTP functionality to support cookies, which are necessary
	to use the HTTP interface."""
	try:
		cj = cookielib.CookieJar()
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
		urllib2.install_opener(opener)
	except NameError:
		pass

class WhoisHandler(object):
	"""WhoisHandler is an abstract class for defining whois interfaces for
	web-based nic servers.
	Child classes must define a 'services' attribute which is a regular expression
	that will match domains serviced by that handler.
	Also, child classes must define LoadHTTP which will retrieve the HTTP response
	and a _parser class which is an HTMLParser capable of parsing the response and
	outputting the textual result."""
	
	__metaclass__ = LeafClassesMeta
	
	def __init__(self, query = None):
		self._query = query

	@classmethod
	def _query_matches_services(cls, query):
		return re.search(cls.services, query, re.IGNORECASE)

	@staticmethod
	def GetHandler(query):
		"""Search through the WhoisHandler subclasses and return the one
		that matches the query."""
		query = query.lower()
		handlers = WhoisHandler._leaf_classes
		matches = [c for c in handlers if c._query_matches_services(query)]
		if not len(matches) == 1:
			error = [
				'Domain for %s is not serviced by this server.',
				'Server error, ambiguous nic server resolution for %s.',
				][bool(len(matches))]
			raise ValueError, error % query
		return matches[0](query)

	def _IsWhoisHandler_(ob):
		return hasattr(ob, '__bases__') and WhoisHandler in ob.__bases__
	_IsWhoisHandler_ = staticmethod(_IsWhoisHandler_)

	def ParseResponse(self, s_out):
		# fix the response; the parser doesn't understand tags that have a slash
		# immediately following the tag name (part of the XHTML 1.0 spec).
		# Alternatively, one could use tidylib with 'drop-empty-paras' set to False
		# response = str(tidy.parseString(response, drop_empty_paras = False))
		response = re.sub(r'<(\w+)/>', r'<\1 />', self._response)
		writer = MyWriter(s_out)
		self._parser(AbstractFormatter(writer)).feed(response)

class ArgentinaWhoisHandler(WhoisHandler):
	services = r'\.ar$'
	
	def LoadHTTP(self):
		query = self._query
		pageURL = 'http://www.nic.ar/consdom.html'
		form = ParseResponse(urlopen(pageURL))[0]
		form['nombre'] = query[:query.find('.')]
		try:
			domain = query[query.find('.') :]
			form['dominio'] = [domain]
		except ItemNotFoundError:
			raise ValueError, 'Invalid domain (%s)' % domain
		req = form.click()
		#req.data = 'nombre=%s&dominio=.com.ar' % query
		req.add_header('referer', pageURL)
		resp = urlopen(req)
		self._response = resp.read()

	class _parser(HTMLParser):
		def start_tr(self, attrs):
			pass # have to define this for end_tr to be called.
			
		def end_tr(self):
			self.formatter.add_line_break()

class CoZaWhoisHandler(WhoisHandler):
	services = r'\.co\.za$'
	
	def LoadHTTP(self):
		query = self._query
		pageURL = 'http://whois.co.za/'
		form = ParseResponse(urlopen(pageURL))[0]
		form['Domain'] = query[:query.find('.')]
		req = form.click()
		resp = urlopen(req)
		self._response = resp.read()

	_parser = HTMLParser

class GovWhoisHandler(WhoisHandler):
	services = r'(\.fed\.us|\.gov)$'
	def LoadHTTP(self):
		query = self._query
		"Perform an whois query on the dotgov server."
		url = urlopen('http://dotgov.gov/whois.aspx')
		forms = ParseResponse(url)
		assert len(forms) == 1
		form = forms[0]
		if form.attrs['action'] == 'agree.aspx':
			# we've been redirected to a different form
			# need to agree to license agreement
			self.Agree(form)
			# note this could get to an infinite loop if cookies aren't working
			# or for whatever reason we're always being redirected to the
			# agree.aspx page.
			return self.LoadHTTP()
		form['who_search'] = query
		resp = urlopen(forms[0].click())
		self._response = resp.read()

	def Agree(self, form):
		"agree to the dotgov agreement"
		agree_req = form.click()
		u2 = urlopen(agree_req)
		resp = u2.read()

	class _parser(HTMLParser):
		def __init__(self, formatter):
			self.__formatter__ = formatter
			# Use the null formatter to start; we'll switch to the outputting
			#  formatter when we find the right point in the HTML.
			HTMLParser.__init__(self, NullFormatter())
			
		def start_td(self, attrs):
			attrs = dict(attrs)
			# I identify the important content by the tag with the ID 'TD1'.
			# When this tag is found, switch the formatter to begin outputting
			#  the response.
			if 'id' in attrs and attrs['id'] == 'TD1':
				self.formatter = self.__formatter__

		def end_td(self):
			# switch back to the NullFormatter
			if not isinstance(self.formatter, NullFormatter):
				self.formatter = NullFormatter()

mozilla_headers = {
	'referer': 'http://www.nic.bo/buscar.php',
	'accept': 'text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5',
	'accept-encoding': 'gzip,deflate',
	'user-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8) Gecko/20051111 Firefox/1.5',
	'accept-charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
	'accept-language': 'en-us,en;q=0.5',
}

class BoliviaPageGetter(PageGetter):
	url = 'http://www.nic.bo/'
#	def GetRequest(self):
#		request = super(self.__class__, self).GetRequest()
#		map(request.add_header, mozilla_headers.keys(), mozilla_headers.values())
#		return request
	
class BoliviaWhoisHandler(WhoisHandler):
	services = r'\.bo$'
	class _parser(HTMLParser):
		def anchor_end(self):
			if self.anchor:
				self.handle_data('[%s]' % self.anchor)
				self.anchor = None

	def LoadHTTP(self):
		name, domain = self._query.split('.', 1)
		domain = '.' + domain
		getter = BoliviaPageGetter()
		getter.form_items = {'subdominio': [domain], 'dominio': name}
		getter.request = getter.Process()
		self._response = getter.Fetch().read()
		del getter.request
		
		# now that we've submitted the request, we've got a response.
		# Unfortunately, this page returns 'available' or 'not available'
		# If it's not available, we need to know who owns it.
		if re.search('Dominio %s registrado' % self._query, self._response):
			getter.url = basejoin(getter.url, 'informacion.php')
			self._response = getter.Fetch().read()
		
	def ParseResponse(self, s_out):
		soup = BeautifulSoup(self._response)
		#self._response = unicode(soup.strong.parent.div).encode('latin-1')
		self._response = unicode(soup.strong.parent.div)
		return super(self.__class__, self).ParseResponse(s_out)

class SourceWhoisHandler(WhoisHandler):
	"""This is not a typical Whois handler, but rather a special
	handler that returns the source of this file"""
	services = r'^source$'
	def LoadHTTP(self): pass
	def ParseResponse(self, s_out):
		filename = os.path.splitext(__file__)[0] + '.py'
		s_out.write(open(filename).read())

class DebugHandler(WhoisHandler):
	services = r'^debug (.*)$'
	authorized_addresses = ['127.0.0.1']
	def LoadHTTP(self): pass
	def ParseResponse(self, s_out):
		if self.client_address[0] in self.authorized_addresses:
			match = re.match(self.services, self._query)
			s_out.write('result: %s' % eval(match.group(1)))
del DebugHandler # disable the debug handler

class MyWriter(DumbWriter):
	def send_flowing_data(self, data):
		data = UnicodeDammit(data).unicode
		# convert non-breaking spaces to regular spaces
		data = data.replace(u'\xa0', u' ')
		DumbWriter.send_flowing_data(self, data)
		
from SocketServer import ThreadingTCPServer, BaseRequestHandler, StreamRequestHandler, socket
from select import select

class Handler(StreamRequestHandler):
	def handle(self):
		try:
			self._handle()
		except:
			log.exception('unhandled exception')

	def _handle(self):
		query = self.rfile.readline().strip()
		log.info('%s requests %s', self.client_address, query)
		try:
			handler = WhoisHandler.GetHandler(query)
			handler.client_address = self.client_address
			handler.LoadHTTP()
			handler.ParseResponse(self.wfile)
			log.info('%s success', self.client_address)
		except urllib2.URLError:
			msg = 'Could not contact whois HTTP service.'
			self.wfile.write(msg + '\n')
			log.exception(msg)
		except ValueError, e:
			log.info('%s response %s', self.client_address, e)
			self.wfile.write('%s\n' % e)

class ConnectionClosed(Exception): pass

class Listener(ThreadingTCPServer):
	def __init__(self):
		ThreadingTCPServer.__init__(self, ('', 43), Handler)

	def serve_until_closed(self):
		try:
			while True: self.handle_request()
		except ConnectionClosed:
			pass

	def get_request(self):
		# use select here because select will throw an exception if the socket
		#  is closed.  Simply blocking on accept will block even if the socket
		#  object is closed.
		try:
			select((self.socket,), (), ())
		except socket.error, e:
			if e[1].lower() == 'bad file descriptor':
				raise ConnectionClosed
		return ThreadingTCPServer.get_request(self)

def serve():
		init()
		l = Listener()
		l.serve_forever()
		
try:
	import win32service, win32serviceutil, win32event

	class TheService(win32serviceutil.ServiceFramework):
		_svc_name_ = 'whois_bridge'
		_svc_display_name_ = 'Whois HTTP Bridge'

		def __init__(self, args):
			win32serviceutil.ServiceFramework.__init__(self, args)

		def SvcStop(self):
			self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
			self.listener.server_close()

		def SvcDoRun(self):
			import servicemanager

			self._setup_logging()			

			log.info('%s service is starting.', self._svc_display_name_)
			servicemanager.LogMsg(
				servicemanager.EVENTLOG_INFORMATION_TYPE,
				servicemanager.PYS_SERVICE_STARTED,
				(self._svc_name_, '')
				)

			self.run()

			servicemanager.LogMsg(
				servicemanager.EVENTLOG_INFORMATION_TYPE,
				servicemanager.PYS_SERVICE_STOPPED,
				(self._svc_name_, '')
				)
			log.info('%s service is stopped.', self._svc_display_name_)

		def run(self):
			init()
			self.listener = Listener()
			self.listener.serve_until_closed()

		def _setup_logging(self):
			from jaraco.util import TimestampFileHandler, LogFileWrapper
			logfile = os.path.join(os.environ['WINDIR'], 'system32', 'LogFiles', self._svc_display_name_, 'events.log')
			handler = TimestampFileHandler(logfile)
			handlerFormat = '[%(asctime)s] - %(levelname)s - [%(name)s] %(message)s'
			handler.setFormatter(logging.Formatter(handlerFormat))
			logging.root.addHandler(handler)
			# if I don't redirect stdoutput and stderr, when the stdio flushes,
			#  an exception will be thrown and the service will bail
			sys.stdout = LogFileWrapper('stdout')
			sys.stderr = LogFileWrapper('stderr')
			logging.root.level = logging.INFO
			
	def main():
		win32serviceutil.HandleCommandLine(TheService)
except ImportError:
	main = serve

if __name__ == '__main__':
	main()
