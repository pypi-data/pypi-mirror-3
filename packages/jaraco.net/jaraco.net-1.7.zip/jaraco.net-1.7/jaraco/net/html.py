# -*- coding: UTF-8 -*-

"""TableParser
	Objects for parsing an HTML file with tables in it.

Copyright © 2004 Jason R. Coombs
"""

__author__ = 'Jason R. Coombs <jaraco@jaraco.com>'
__version__ = '$Revision$a'[11:-2]
__svnauthor__ = '$Author$'[9:-2]
__date__ = '$Date$'[7:-2]

import htmllib, formatter, types
import logging

log = logging.getLogger('TableParser')

class HTMLObject(object):
	def __init__(self, name):
		self.name = name

class HTMLTable(list):
	currentRow = None

class HTMLRow(list):
	currentElement = None

class HTMLElement(object):
	"A mutable variant object"
	def __init__(self):
		self.value = None
		
	def setValue(self, value):
		self.value = value

	def append(self, value):
		if type(self.value) == types.ListType:
			self.value.append(value)
		if type(self.value) == types.TupleType:
			self.value += (value,)
		if type(self.value) == types.StringType:
			self.value += value
		if self.value is None:
			self.value = value
			
	def __str__(self):
		return str(self.value)

	def __repr__(self):
		return repr(self.value)

	def getValue(self):
		return self.value

class TableParser(htmllib.HTMLParser):
	"""Parses any number of tables from an HTML file.  This will attempt to parse incorrect HTML
	as well, but no guarantees are made.

	The parser will accept nested tables as <table> inside <td> elements.
	"""
	def __init__(self):
		htmllib.HTMLParser.__init__(self, formatter.NullFormatter())
		self.tables = []
		self.currentTable = None

	def start_table(self, attrs):
		if self.currentTable:
			# we were already in a table, so grab any data that was already parsed for this element
			self.saveCurrent()
		newTable = HTMLTable()
		self.tables.append(newTable)
		newTable.parentTable = self.currentTable
		self.currentTable = newTable
		self.currentTable.extraRows = {}

	def end_table(self):
		self.currentTable = self.currentTable.parentTable
		if self.currentTable:
			# we were already in a table, so start saving data again.
			self.save_bgn()

	def start_tr(self, attrs):
		self.end_tr()
		newRow = HTMLRow()
		self.currentTable.append(newRow)
		self.currentTable.currentRow = newRow

	def end_tr(self):
		if self.currentTable.currentRow is None:
			#do nothing and
			return
		self.checkForExtraRows()
		# the following two statements might be a bit confusing, so here's some background.
		# the first statement replaces all elements in the current row with elements converted
		# to strings.  It uses the [:] notation so it modifies the existing object in place and doesn't
		# just replace it... and since that object is referenced by the list of rows in the currentTable,
		# that list will also be modified.
		# the second statement removes the currentRow reference, but the object is still referenced
		# by the list of rows in the currentTable.
		self.currentTable.currentRow[:] = map(lambda x: x.getValue(), self.currentTable.currentRow)
		self.currentTable.currentRow = None

	def start_td(self, attrs):
		if self.currentTable.currentRow is None:
			# found a <td> tag not preceeded by a <tr> tag, so one is implied.
			self.start_tr({})
		self.checkForExtraRows()
		attrs = dict(attrs)
		try:
			# TODO: assign for additional columns as well if 'colspan' is set
			currentColumnNumber = len(self.currentTable.currentRow)
			self.currentTable.extraRows[currentColumnNumber] = int(attrs['rowspan']) - 1
		except KeyError:
			pass
		try:
		    self.currentTable.currentRow.extraCols = int(attrs['colspan']) - 1
		except KeyError:
			self.currentTable.currentRow.extraCols = 0
		newElement = HTMLElement()
		self.currentTable.currentRow.append(newElement)
		self.currentTable.currentRow.currentElement = newElement
		# start remembering the contents of the element
		self.save_bgn()

	def end_td(self):
		self.saveCurrent()
		# fill in blanks for the extra columns
		self.currentTable.currentRow.extend([HTMLElement()] * self.currentTable.currentRow.extraCols)
		self.currentTable.currentRow.currentElement = None

	def saveCurrent(self):
		self.currentTable.currentRow.currentElement.append(self.save_end())

	def checkForExtraRows(self):
		currentColumnNumber = len(self.currentTable.currentRow)
		extraRows = self.currentTable.extraRows
		if extraRows.has_key(currentColumnNumber):
			extraRows[currentColumnNumber] -= 1
			self.currentTable.currentRow.append(HTMLElement())
			if extraRows[currentColumnNumber] == 0:
				del extraRows[currentColumnNumber]
			# Now check again
			self.checkForExtraRows()
