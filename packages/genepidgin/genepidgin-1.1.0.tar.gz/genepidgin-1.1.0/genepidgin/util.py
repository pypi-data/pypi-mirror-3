#!/bin/env python

import os.path
import re
import time

COMMENT_RE = re.compile("\A#")

def tabDelimitedFilenameToListOfTuples(filename):
	"""
	This method reads in a tab-delimited file and returns a list of lists.
	Each inner list represents a row in the file, and each element in that
	list represents a column in that row, where rows are delimited by tabs.
	Two or more adjacent tabs are considered to delimit empty strings.
	Lines beginning with a # are ignored as comments.
	"""
	fd = open(filename, "r")
	ret = []

	for line in fd:
		if COMMENT_RE.match(line):
			continue
		toks = line.split("\t")
		ret.append(toks)

	fd.close()
	return ret

def simpleNamesFileReader(filename):
	"""
	This function reads in files which follow a simple format:

	one feature id per line, at the head of the line, then a tab character,
	the rest of the line is the name.

	Lines beginning with # are ignored as comments
	
	For example, given the following input:
	
	id1	name1
	id2 name2
	#comment
	id3	name3
	
	This function returns a list of tuples:
	
	[(id1, name1), (id2, name2), (id3, name3), ...]
	"""
	try:
		fin = open(filename, "rU")
		lines = fin.readlines()
		fin.close()
	except:
		raise Exception, "could not read from file %s" % filename

	re1 = re.compile("\A#")
	re2 = re.compile("\A(\S+)\s+(.*)")

	fields = []
	for line in lines:
		if re1.match(line):
			continue
		m2 = re2.search(line)
		if m2 is None:
			continue
		nid, name = m2.groups()
		# do not retain whatever follows a tab character
		name = name.split("\t")[0]
		fields.append( (nid, name) )
	return fields

def simpleNamesFileWriter(fields, foutname):
	""" see simpleNamesFileReader for format """
	fout = open(foutname, "w")
	for id, name in fields:
		if not name:
			name = ""
		fout.write("%s\t%s\n" % (id, name))
	fout.close()

def addPredicateToFileName(filename, predicate):
	"""
	/path/foo.txt becomes /path/foopredicate.txt
	"""
	before, after = os.path.splitext(filename)
	return before + predicate + after

def NOW():
	return time.strftime("%H:%M:%S", time.localtime())
