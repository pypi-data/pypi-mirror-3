# -*- coding: UTF-8 -*-

"""cookies.py
Implements cookie support.
This works better than the library supplied in Python.
	
Copyright © 2004 Jason R. Coombs
"""

__author__ = 'Jason R. Coombs <jaraco@jaraco.com>'
__version__ = '$Rev$'[6:-2]
__svnauthor__ = '$Author$'[9:-2]
__date__ = '$Date$'[7:-2]

import os, copy, urllib, httplib
# import case-insensitive string & dictionary
from jaraco.util.string import FoldedCase
from jaraco.util.dictlib import FoldedCaseKeyedDict
import itertools
import string, re

class CookieMonster(object):
	"Read cookies out of a user's IE cookies file"
	def __init__(self, filename):
		profileDir = os.environ['USERPROFILE']
		self.cookieDir = os.path.join(profileDir, 'Cookies')
		self.cookieFile = file(os.path.join(self.cookieDir, filename))
		self.entries = self.getEntries(self.cookieFile)

	def getEntries(self, cookieFile):
		while True:
			entry = itertools.takewhile(isNotCookieDelimiter, cookieFile)
			entry = map(string.rstrip, entry)
			if not entry: break
			cookie = self.makeCookie(*entry)
			yield cookie

	def makeCookie(self, key, value, domain, flags, ExpireLow, ExpireHigh, CreateLow, CreateHigh):
		expires = (int(ExpireHigh) << 32) | int(ExpireLow)
		created = (int(CreateHigh) << 32) | int(CreateLow)
		del ExpireHigh, ExpireLow, CreateHigh, CreateLow
		flags = int(flags)
		domain, path = string.split(domain, '/', 1)
		path = '/' + path
		cookie = vars()
		del cookie['self']
		return cookie

def getCookies(source, path = None):
	"""Takes a Set-Cookie header (possibly with multiple cookies) or multiple Set-Cookie
	headers, and returns a list of cookies in those headers.
	source may be an httplib.HTTPResponse or httplib.HTTPMessage or a list of Set-Cookie headers or a Set-Cookie header.
	>>> getCookies('A=B, C=D')
	[<cookie A=B, C=D>]
	>>> getCookies(['A=B', 'C=D'])
	[<cookie A=B>, <cookie C=D>]
	"""
	result = []
	if isinstance(source, httplib.HTTPResponse):
		source = source.msg
	if isinstance(source, httplib.HTTPMessage):
		source = source.getheaders('Set-Cookie')
	if isinstance(source, (list, tuple)):
		map(result.extend, map(getCookies, source, (path,)*len(source)))
	elif isinstance(source, str):
		c = cookie(source)
		path and c.setPathIfEmpty(path)
		result.append(c)
	return result

def isNotCookieDelimiter(s):
	return s != '*\n'

class cookie(object):
	"""cookie class parses cookie information from HTTP Responses and outputs
	for HTTP Requests"""
	parameterNames = tuple(map(FoldedCase, ('expires', 'path', 'domain', 'secure')))
	def __init__(self, source = None):
		if isinstance(source, basestring):
			self.readFromSetHeader(source)
		if isinstance(source, self.__class__):
			self.__dict__ = source.__dict__.copy()
			
	def readFromSetHeader(self, header):
		'Read a cookie from a header as received in an HTTP Response'
		if hasattr(self, '__name'):
			raise RuntimeError, 'Cookies may not be re-used.'
		fields = re.split(';\s*', header)
		splitEquals = lambda x: x.split('=', 1)
		fieldPairs = map(splitEquals, fields)
		self.__parameters = FoldedCaseKeyedDict(fieldPairs)
		self.__findName()

	def __findName(self):
		"Find the name of the cookie, which should be the only pair that's not a parameter"
		isNotParameter = lambda k: k not in self.parameterNames
		names = filter(isNotParameter, self.__parameters)
		if not len(names) == 1:
			raise ValueError, "Found more than one name/value pair where name isn't a cookie parameter %s" % names
		name = names[0]
		self.__name = name
		self.__value = self.__parameters[name]
		del self.__parameters[name]

	def getRequestHeader(self):
		"returns the cookie as can be used in an HTTP Request"
		return '='.join((self.__name, self.__value))

	def isSecure(self):
		return eval(string.capwords(self.__parameters.get('secure', 'False')))

	def __eq__(self, other):
		"Instances of the same path and name will overwrite each other."
		samepath = self.getPath() == other.getPath()
		return self.__name == other.__name and samepath

	def getPath(self):
		return self.__parameters.get('path', '')

	def getParameters(self):
		return self.__parameters

	def get(self, *args):
		return self.__parameters.get(*args)

	def setPathIfEmpty(self, path):
		if not self.getPath():
			self.__parameters['path'] = path

	def __str__(self):
		return 'Cookie: ' + self.__parameterString()

	def __repr__(self):
		return '<%s %s>' % (self.__class__.__name__, self.__parameterString())

	def __parameterString(self):
		return '; '.join(map('='.join, [(self.__name, self.__value)] + self.__parameters.items()))

class Container(object):
	"An object for storing cookies as a web browser would."
	def __init__(self):
		self.__cookies = []

	def get_request_header(self, test = lambda x: True):
		"return the cookies for which test(cookie) == True"
		delimiter = '; '
		matched_cookies = filter(test, self.__cookies)
		# it would be more efficient to do an insertion sort.  Is this easily done?
		matched_cookies.sort(self._path_compare)
		strings = map(lambda c: c.getRequestHeader(), matched_cookies)
		return delimiter.join(strings)

	def _path_compare(self, ca, cb):
		"""Compare the paths of two cookies, used for a sort routine to ensure cookies
		with paths of /bar appear before cookies with path /."""
		return -cmp(ca.getPath(), cb.getPath())

	def add(self, cookie):
		"Add cookie(s) to the list.  If two cookies compare equal, replace the original."
		if isinstance(cookie, (tuple, list)):
			map(self.add, cookie)
		elif cookie in self.__cookies:
			self.__cookies[self.__cookies.index(cookie)] = cookie
		else:
			self.__cookies.append(cookie)

	def __repr__(self):
		return repr(self.__cookies)