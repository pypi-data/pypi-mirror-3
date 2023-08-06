#!/bin/env python

from nose.tools import *

import os
import os.path

import genepidgin.distance

DATA_ROOT = "./genepidgin/test/data/"

namePairs = os.path.join(DATA_ROOT, "testDistanceIn.txt")
scoredNamePairs = os.path.join(DATA_ROOT, "testDistanceOut.txt")
dt = genepidgin.distance.DistanceTool()

class TestDistance(object):

	def assert_file_equals(self, file1, file2):

		f1 = open(file1, 'r')
		source = f1.read()
		f1.close()
		
		f2 = open(file2, 'r')
		dest = f2.read()
		f2.close()

		assert_equal(source, dest, "%s != %s" % (file1, file2))

	def testPairwiseDistances(self):
		testfilename = os.path.join(DATA_ROOT, "testDistancesWorking.txt")
		fd = open(namePairs)
		ofd = open(testfilename, "w")

		for line in fd:

			if len(line) <= 1:
				continue
			if line.startswith("#"):
				continue

			line.strip()
			s1, s2 = line.split("\t")

			ofd.write("%.02f // %s /// %s" % (dt(s1, s2), s1, s2))

		ofd.close()
		self.assert_file_equals(testfilename, scoredNamePairs)
		os.remove(testfilename)

