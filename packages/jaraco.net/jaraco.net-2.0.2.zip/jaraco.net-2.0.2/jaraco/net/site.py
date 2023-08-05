from __future__ import print_function

from path import path
from jaraco.util.string import local_format as lf

def make_index_cmd():
	"""
	Generate an index file for each directory that itself has an
	index.htm file
	"""
	root = path('.')
	print('<ul>')
	for dir in sorted(root.dirs()):
		if not (dir/'index.htm').exists(): continue
		dir = dir.basename()
		print(lf('<li><a href="{dir}/index.htm">{dir}</a></li>'))
	print('</ul>')
