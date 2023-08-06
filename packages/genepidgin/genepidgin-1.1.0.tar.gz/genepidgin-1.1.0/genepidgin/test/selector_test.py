#!/bin/env python

#from __future__ import absolute_import
from nose.tools import *

import os.path
import subprocess

import genepidgin.selector

# common files and paths
DATA_ROOT = "./genepidgin/test/data/"
bfile_dest1Alone = os.path.join(DATA_ROOT, "dest1Alone.pidginb")
hfile_dest1Alone = os.path.join(DATA_ROOT, "dest1Alone.pidginh")
bfile_empty = os.path.join(DATA_ROOT, "empty.pidginb")
hfile_empty = os.path.join(DATA_ROOT, "empty.pidginh")
file_incorrectextension = os.path.join(DATA_ROOT, "incorrect.extension")

bm8_file = os.path.join(DATA_ROOT, "testorg.kegg.blastm8")
bm8_names = os.path.join(DATA_ROOT, "kegg.names.txt")

class TestSelector():

	def blastCompare(self, bsource):
		assert_equal(bsource.destId, "dest")
		assert_equal(bsource.sourceId, "source")
		assert_equal(bsource.sourceAuth, "FIGfam")
		assert_equal(bsource.getName(), "blastsushi")
		assert_equal(bsource.minCoverage, 1.0)
		#assert_equal(bsource.minPctIdentity, 0.5)

	def testBlastSourceByLine(self):
		
		line = "dest	1	10	10	source	2	9	8	FIGfam	5	7	blastsushi	blastcomment"

		bsource = genepidgin.selector.BlastNameSource(line)
		self.blastCompare(bsource)

		bsource = genepidgin.selector.BlastNameSource()
		bsource.parseLine(line)
		self.blastCompare(bsource)

	def hmmerCompare(self, hsource):
		assert_equal(hsource.destId, "dest")
		assert_equal(hsource.destStart, 1)
		assert_equal(hsource.destStop, 10)
		assert_equal(hsource.destLen, 10)
		assert_equal(hsource.sourceId, "source")
		assert_equal(hsource.sourceStart, 2)
		assert_equal(hsource.sourceStop, 9)
		assert_equal(hsource.sourceLen, 8)
		assert_equal(hsource.score, 300)
		assert_equal(hsource.familyTrustedCutoff, 1.0)
		assert_equal(hsource.eValue, 1.03e-16)
		assert_equal(hsource.getName(), "hmmersushi")
		#assert_equal(hsource.comment, "hmmercomment")

	def testHmmerSourceByLine(self):
		
		line = "dest	1	10	10	source	2	9	8	300	1.0	1.03e-16	hmmersushi	hmmercomment"

		hsource = genepidgin.selector.HmmerNameSource(line)
		self.hmmerCompare(hsource)

		hsource = genepidgin.selector.HmmerNameSource()
		hsource.parseLine(line)
		self.hmmerCompare(hsource)

	def testRepairKeggOrthology(self):
		# note that desiredOrthology is a substring the rawName in line1 and the
		# entire name in line2
	
		# test that we repair it when needed
		line1 = "dest	1	10	10	source	2	9	8	KEGG	5	7	rsh:Rsph17029_4104  H+-transporting two-sector ATPase, gamma subunit ; K02115 F-type H+-transporting ATPase subunit gamma [EC:3.6.3.14]	blastcomment"
		desiredOrthology = "K02115 F-type H+-transporting ATPase subunit gamma [EC:3.6.3.14]"
		bsource = genepidgin.selector.BlastNameSource(line1)
		assert_equal(bsource.getName(), desiredOrthology)
	
		# test that we don't screw anything up when not needed
		line2 = "dest	1	10	10	source	2	9	8	KEGG	5	7	K02115 F-type H+-transporting ATPase subunit gamma [EC:3.6.3.14]	blastcomment"
		bsource = genepidgin.selector.BlastNameSource(line2)
		assert_equal(bsource.getName(), desiredOrthology)


	def testBlastSourceByFile(self):
		sources = genepidgin.selector.getSources(bfile_dest1Alone)
		assert_equal(len(sources), 3)

	# BLAST M8

	def blastM8Compare(self, bm8source):
		assert_equal(bm8source.destId, "7000000143106953:1-60000")
		assert_equal(bm8source.sourceId, "7000000108909452")
		#assert_equal(bm8source.numIdentities, 519)
		assert_equal(bm8source.getName(), "alpha omega protein")

	def testBlastM8SourceByFile(self):
		genepidgin.selector.loadNameRefFiles([bm8_names])
		sources = genepidgin.selector.getSources(bm8_file, nameRefFiles=[bm8_names])
		assert_equal(len(sources), 1)
		self.blastM8Compare(sources[0])

	def testBlastM8SourceByLine(self):
		# note that these are tabs in here, not spaces
		line = "7000000143106953:1-60000	7000000108909452	75.11	691	170	2	26627	28693	1	691	0.0	1053"
		genepidgin.selector.loadNameRefFiles([bm8_names])
		bm8source = genepidgin.selector.BlastM8NameSource(filename="source.kegg.blastm8", nameRefFiles=[bm8_names])
		bm8source.parseLine(line)
		self.blastM8Compare(bm8source)

	# HMMER

	# testing that negative evalues are ignored in score comparisons
	def testHmmerMinEValue(self):
		h1name = "tigrfam"
		h2name = "pfam"
		h1 = "dest	1	10	10	%s	2	9	7	300	1.0	-0.01	hmmertigrfam	hmmercomment" % h1name
		h2 = "dest	1	10	10	%s	2	9	7	301	1.0	0.0	hmmertigrfam	hmmercomment" % h2name
		hsource1 = genepidgin.selector.HmmerNameSource(h1)
		hsource2 = genepidgin.selector.HmmerNameSource(h2)
		result = sorted([hsource1, hsource2])
		
		assert_equal(result[1].sourceId, h2name)
		assert_equal(result[0].sourceId, h1name)

	# verify acceptance of empty data files
	def testEmptyNameSourceFile(self):
		sources = genepidgin.selector.getSources(bfile_empty)
		assert_equal(sources, [])
		sources = genepidgin.selector.getSources(hfile_empty)
		assert_equal(sources, [])


	# Verifies that we puke on incorrectly named files
	def testWrongExtension(self):
		assert_raise(Exception, genepidgin.selector.parsePidginbFile, file_incorrectextension)
		assert_raise(Exception, genepidgin.selector.parsePidginhFile, file_incorrectextension)
		assert_raise(Exception, genepidgin.selector.getSources, file_incorrectextension)

	# Verifies that our sorting does what we expect
	def testSort(self):
		h1name = "tigrfam"
		h2name = "pfam"
		h1 = "dest	1	10	10	%s	2	9	7	300	1.0	1.03e-16	hmmertigrfam	hmmercomment" % h1name
		h2 = "dest	1	10	10	%s	2	9	8	300	1.0	1.03e-17	hmmerpfam	hmmercomment" % h2name
		
		b1 = "dest	1	10	10	source	2	9	8	KEGG	5	7	blastkegg	blastcomment"
		b2 = "dest	1	10	10	source	2	9	8	FIGfam	5	7	blastfigfam	blastcomment"
		b3 = "dest	1	10	10	source	2	9	8	SwissProt	5	7	blastswissprot	blastcomment"

		hsource1 = genepidgin.selector.HmmerNameSource(h1, "testh1")
		hsource2 = genepidgin.selector.HmmerNameSource(h2, "testh2")
		
		bsource1 = genepidgin.selector.BlastNameSource(b1, "testb1")
		bsource2 = genepidgin.selector.BlastNameSource(b2, "testb2")
		bsource3 = genepidgin.selector.BlastNameSource(b3, "testb3")

		test1 = [hsource1, hsource2]
		test2 = [bsource1, bsource2, bsource3]
		result1 = sorted(test1)
		result1.reverse() # sorting leaves best result at end
		result2 = sorted(test2)
		result2.reverse()
		
		# The sorting should prefer hmmer to blast universally.
		# the lower e-value should sort better
		assert_equal(result1[0].sourceId, h2name)
		assert_equal(result1[1].sourceId, h1name)
		
		# tests blast protein library catalog preference
		assert_equal(result2[0].sourceAuth, genepidgin.selector.KEGG)
		assert_equal(result2[1].sourceAuth, genepidgin.selector.SWISSPROT)
		assert_equal(result2[2].sourceAuth, genepidgin.selector.FIGFAM)

	def testCLI(self):
		testCLIPrefix = os.path.join(DATA_ROOT, "testSelector.testCLI")

		testCLINameFile =  testCLIPrefix + ".names.txt"
		testCLIEtyFile =   testCLIPrefix + ".etymology.txt"
		testCLIStatsFile = testCLIPrefix + ".stats.txt"

		cmd = "python ./genepidgin/cmdline.py select --output=%s --namefiles=%s %s" % (testCLIPrefix, bm8_names, bm8_file)
		process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
		output, ret = process.communicate()

		assert_true(os.path.exists(testCLINameFile))
		assert_true(os.path.exists(testCLIEtyFile))
		assert_true(os.path.exists(testCLIStatsFile))

		os.remove(testCLINameFile)
		os.remove(testCLIEtyFile)
		os.remove(testCLIStatsFile)

