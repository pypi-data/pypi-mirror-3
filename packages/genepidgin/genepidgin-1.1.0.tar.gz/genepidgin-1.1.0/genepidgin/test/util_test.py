#!/bin/env python

from nose.tools import *

import os.path

import genepidgin.util

DATA_ROOT = "./pidgin/test/data/"

class TestUtil():

	def testSimpleNamesFileReader(self):
		file1 = os.path.join(DATA_ROOT, "testSimpleNamesFileReader.txt")
		lines = genepidgin.util.simpleNamesFileReader(file1)
		assert_equal(len(lines), 2)
		assert_equal(lines[0], ("885", "kinase kinase"))
		assert_equal(lines[1], ("890", "alpha transport family protein"))

	def testAddPredicateToFilename(self):
		input = "/path/foo.txt"
		predicate = "predicate"
		desired = "/path/foopredicate.txt"
		output = genepidgin.util.addPredicateToFileName(input, predicate)
		assert_equal(output, desired)

