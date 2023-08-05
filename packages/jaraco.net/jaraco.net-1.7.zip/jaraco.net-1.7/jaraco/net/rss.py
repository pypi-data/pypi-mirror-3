"""
Routines for handling RSS feeds
"""

from __future__ import print_function
from __future__ import absolute_import

import feedparser
import itertools
import subprocess
import os
import functools
import re
import operator
import datetime
import sys
import mimetypes
import urllib2
import logging
import jaraco.util.logging
from jaraco.util.filesystem import encode as encode_filename
from jaraco.net.http import get_url
from dateutil import parser as date_parser
from optparse import OptionParser

log = logging.getLogger(__name__)

def parse_filter(filter_string):
	filter_pattern = re.compile('(?:(before|after) )?([0-9-]+)$', re.I)
	match = filter_pattern.match(filter_string)
	sign, date_string = match.groups()
	op = dict(before=operator.le, after=operator.ge).get(sign, operator.eq)
	spec_date = date_parser.parse(date_string)
	return lambda entry: op(datetime.datetime(*entry.updated_parsed[:6]), spec_date)

class CombinedFilter(object):
	def __init__(self, filters):
		self.filters = filters

	def __call__(self, subject):
		results = [filter(subject) for filter in self.filters]
		return reduce(operator.and_, results, True)

def _parse_filters(options):
	filters = map(parse_filter, options.date_filter)
	options.date_filter = CombinedFilter(filters)

def _parse_args(parser=None):
	parser = parser or OptionParser()
	parser.add_option('-u', '--url')
	#parser.add_option('-r', '--reverse', help="show in reverse order")
	parser.add_option('-f', '--date-filter', help="add a date filter such as 'before 2006'", default=[], action="append")
	jaraco.util.logging.add_options(parser)
	options, args = parser.parse_args()
	if not options.url: parser.error("URL is required")
	_parse_filters(options)
	jaraco.util.logging.setup(options)
	return options, args

def download_enclosures():
	options, args = _parse_args()
	d = feedparser.parse(options.url)
	for entry in filter(options.date_filter, d['entries']):
		enclosure = entry.enclosures.pop()
		assert not entry.enclosures, "Only support one enclosure per item"
		
		title = entry.title
		ext = mimetypes.guess_extension(enclosure.type) or '.mp3'
		filename = title + ext
		log.info('Getting %s', filename)
		filename = encode_filename(filename)
		try:
			get_url(enclosure.url, filename, replace_newer=True)
		except KeyboardInterrupt:
			if os.path.exists(filename): os.remove(filename)
			log.info('Quitting')
			break

def launch_feed_enclosure():
	"""
	RSS Feed Launcher
	"""
	parser = OptionParser(usage=launch_feed_enclosure.__doc__)
	parser.add_option('-i', '--index', help="launch feed found at specified index")
	options, args = _parse_args(parser)
	assert not args, "Positional arguments not allowed"
	load_feed_enclosure(options.url, options.date_filter, options.index)

def load_feed_enclosure(url, filter_=None, index=None):
	d = feedparser.parse(url)
	print('loaded', d['feed']['title'])
	filtered_entries = filter(filter_, d['entries'])
	
	if index is None:
		for i, entry in enumerate(filtered_entries):
			fmt = unicode('{0:4d} {1}')
			print(fmt.format(i, entry.title))
		try:
			index = int(raw_input('Which one? '))
		except ValueError:
			print("Nothing selected")
			sys.exit(0)

	player_search = (
		r'C:\Program Files\Windows Media Player\wmplayer.exe',
		r'C:\Program Files (x86)\Windows Media Player\wmplayer.exe',
		)
	player = itertools.ifilter(os.path.exists, player_search).next()

	command = [player, filtered_entries[index].enclosures[0].href]
	print('running', subprocess.list2cmdline(command))
	subprocess.Popen(command)

def launch_feed_as_playlist():
	options, args = _parse_args()
	assert not args, "Positional arguments not allowed"
	get_feed_as_playlist(options.url, filter_=options.date_filter)

def get_feed_as_playlist(url, outfile=sys.stdout, filter_=None):
	d = feedparser.parse(url)
	filtered_entries = filter(filter_, d['entries'])
	# RSS feeds are normally retrieved in reverse cronological order
	filtered_entries.reverse()
	for e in filtered_entries:
		outfile.write(e.enclosures[0].href)
		outfile.write('\n')

if __name__ == '__main__': launch_feed_enclosure()