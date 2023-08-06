#!/bin/env python

from nose.tools import *

import os
import os.path
import subprocess

import genepidgin.scorer

DATA_ROOT = "./genepidgin/test/data/"

refFile =    os.path.join(DATA_ROOT, "scoreref.txt")
# this file is missing an entry vs the ref file
queryFile1 = os.path.join(DATA_ROOT, "scorequery1.txt")
# this file has an entry with no match in the ref file
queryFile2 = os.path.join(DATA_ROOT, "scorequery2.txt")

# generated files
refFileSummary =     os.path.join(DATA_ROOT, "scoreref.txt.summary")
queryFile1Compared = os.path.join(DATA_ROOT, "scorequery1.txt.compared")
queryFile2Compared = os.path.join(DATA_ROOT, "scorequery2.txt.compared")

# note that we don't actually test what the scores are for these
# tests; that's the domain of the scoring function, which for us
# is distance.py

class TestScorer():

    # testing the result of genepidgin compare ref vs queryfile1, above
    def verifyQueryCompare1(self):
        # can't use full strip() because it takes extra \t
        lines = [x.strip("\n") for x in open(queryFile1Compared)]

        # make sure that we write out all reference lines, despite the fact
        # that this query file is missing a reference entry
        assert_equal(len(lines), 3)

        cmp1 = lines[0].split("\t")
        assert_equal(len(cmp1), 4)
        assert_equal(cmp1[0], "100")
        assert_equal(cmp1[2], "DSBA oxidoreductase")
        assert_equal(cmp1[3], "DSBA-like thioredoxin domain-containing protein")

        cmp2 = lines[1].split("\t")
        assert_equal(len(cmp2), 4)
        assert_equal(cmp2[0], "101")
        assert_equal(cmp2[2], "traD, TraG")
        assert_equal(cmp2[3], "type IV secretion-system coupling protein DNA-binding domain")

        # this is the missed query line
        cmp3 = lines[2].split("\t")
        assert_equal(len(cmp3), 4)
        assert_equal(cmp3[0], "102")
        assert_equal(cmp3[1], "1.00") # comparing against nothing should always be 1.0
        assert_equal(cmp3[2], "GTP1/OBG family protein")
        assert_equal(cmp3[3], "")

        os.remove(queryFile1Compared)

    # testing the result of genepidgin compare ref vs queryfile2, above
    def verifyQueryCompare2(self):
        # can't use full strip() because it takes extra \t
        lines = [x.strip("\n") for x in open(queryFile2Compared)]

        # make sure that we write out only the reference comparisons
        # and not the extra one
        assert_equal(len(lines), 3)

        cmp1 = lines[0].split("\t")
        assert_equal(len(cmp1), 4)
        assert_equal(cmp1[0], "100")
        assert_equal(cmp1[2], "DSBA oxidoreductase")
        assert_equal(cmp1[3], "DSBA oxidoreductase [Rhodobacter sphaeroides 2.4.1]")

        cmp2 = lines[1].split("\t")
        assert_equal(len(cmp2), 4)
        assert_equal(cmp2[0], "101")
        assert_equal(cmp2[2], "traD, TraG")
        assert_equal(cmp2[3], "hypothetical protein RSP_3905 [Rhodobacter sphaeroides 2.4.1]")

        cmp3 = lines[2].split("\t")
        assert_equal(len(cmp3), 4)
        assert_equal(cmp3[0], "102")
        assert_equal(cmp3[2], "GTP1/OBG family protein")
        assert_equal(cmp3[3], "Obg family GTPase CgtA")

        os.remove(queryFile2Compared)

    def verifySummary(self):
        lines = [x.strip("\n") for x in open(refFileSummary)]

        # three reference entries, three summary lines
        assert_equal(len(lines), 3)

        cmp1 = lines[0].split("\t")
        assert_equal(len(cmp1), 5)
        assert_equal(cmp1[0], "100")
        assert_equal(cmp1[2], "DSBA oxidoreductase")
        assert_equal(cmp1[3], "DSBA oxidoreductase [Rhodobacter sphaeroides 2.4.1]")
        assert_equal(cmp1[4], "scorequery2.txt")

        cmp2 = lines[1].split("\t")
        assert_equal(len(cmp2), 5)
        assert_equal(cmp2[0], "101")
        assert_equal(cmp2[2], "traD, TraG")
        assert_equal(cmp2[3], "type IV secretion-system coupling protein DNA-binding domain")
        assert_equal(cmp2[4], "scorequery1.txt")

        cmp3 = lines[2].split("\t")
        assert_equal(len(cmp3), 5)
        assert_equal(cmp3[0], "102")
        assert_equal(cmp3[2], "GTP1/OBG family protein")
        assert_equal(cmp3[3], "Obg family GTPase CgtA")
        assert_equal(cmp3[4], "scorequery2.txt")

        os.remove(refFileSummary)

    def testCLIDualCompare(self):
        cmd = "python ./genepidgin/cmdline.py compare %s %s" % (refFile, queryFile1)
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        output, ret = process.communicate()
        assert_equal(ret, None)
        self.verifyQueryCompare1()

    def testProgDualCompare(self):
        genepidgin.scorer.compareFiles(refFile, [queryFile1])
        self.verifyQueryCompare1()

    def testCLIMultiCompare(self):
        cmd = "python ./genepidgin/cmdline.py compare %s %s %s" % (refFile, queryFile1, queryFile2)
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        output, ret = process.communicate()
        assert_equal(ret, None)
        self.verifyQueryCompare1()
        self.verifyQueryCompare2()
        self.verifySummary()

    def testProgMultiCompare(self):
        genepidgin.scorer.compareFiles(refFile, [queryFile1, queryFile2])
        self.verifyQueryCompare1()
        self.verifyQueryCompare2()
        self.verifySummary()

