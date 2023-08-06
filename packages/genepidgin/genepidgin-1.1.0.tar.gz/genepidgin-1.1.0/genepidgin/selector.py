#!/bin/env python

import sys
import re
import genepidgin.cleaner
from genepidgin.util import NOW

bname = genepidgin.cleaner.BioName(removeTrailingClauses=0)

HMMER = "hmmer"
BLAST = "blast"

KEGG = "KEGG"
FIGFAM = "FIGfam"
SWISSPROT = "SwissProt"
ALLGROUP = "AllGroup"    # not publicly supported for naming
NR = "NR"                # not publicly supported for naming
REFSEQ = "RefSeq"
PRK = "PRK"
CDD = "CDD"              # not publicly supported for naming
UNIREF50 = "UniRef50"
UNIREF90 = "UniRef90"

# file types
GPIDGINB = ".pidginb"
GPIDGINH = ".pidginh"
BLASTM8 = ".blastm8"

# Used to control the hierarchy of blast protein libraries.
# Higher is better.
blastRanking = {
    NR: -200,
    ALLGROUP: -10,
    REFSEQ: -5,
    FIGFAM: -3,
    UNIREF50: -2,
    UNIREF90: -1,
    SWISSPROT: 0,
    CDD: 4,
    PRK: 5,
    KEGG: 6,
}
def getBlastSourceNum(name):
    return blastRanking[name]

def getValidBlastSources():
    return [PRK, KEGG, FIGFAM, SWISSPROT, UNIREF90, UNIREF50]

def getAllBlastSources():
    return [CDD, KEGG, PRK, REFSEQ, FIGFAM, SWISSPROT, ALLGROUP, NR]

#
# on etymology, otherwise known as all these += strings:
#
# Most filtering steps in this file generate a string called ety or
# etymology.  This is used in reporting the steps that we took when
# generating a name, and therefore, the ordering of the steps is
# important.
# I couldn't think of a better way to do this, so the strings are just
# built up as they walk through the code.
#

# We don't do a list comprehension here because it's not a filtering
# step.  We're going one by one through the remaining list to find the
# first feasible name.
def chooseBestSourceByName(sources, process):
    bestSource = None
    bestCount = None
    for i, source in enumerate(sources):
        filteredName, filterProcess = bname.filter(source.getName(), getOutput=1)
        if not filteredName:
            continue
        else:
            source.filteredName = filteredName
            source.filterProcess = filterProcess
            bestCount, bestSource = i, source
            break

    ety = ""
    if not bestSource:
        if len(sources) == 1:
            ety = "One %s source had a name that filtered to nothing.\n" % process
        else:
            ety = "All %d %s sources had names that filtered to nothing.\n" % (len(sources), process)
    elif bestCount == 0:
        if len(sources) == 1:
            ety = "One %s source had a good name.\n" % process
        else:
            ety = "The first %s source had a good name.\n" % process
    else:
        ety = "Found an acceptable name in the %s sources. Skipped %d of those sources to get to the one we like because their names filtered to nothing.\n" % (process, bestCount)

    return (bestSource, ety)


def select(files, outNamePrefix="./pidgin_out", nameRefFiles=None):
    """
    files: a list of genepidgin data files
    outputNameFile: where the names will be written
    outputEtymologyFile: if specified, where the collected etymology will be written
    """

    if nameRefFiles:
        print NOW(), "loading name reference files"
        loadNameRefFiles(nameRefFiles)
        print NOW(), "name reference files loaded"

    allSources = []
    print NOW(), "reading sources"
    for fileName in files:
        tSources = getSources(fileName, nameRefFiles)
        allSources.extend(tSources)
        print NOW(), "read %d sources from %s" % (len(tSources), fileName)
    print NOW(), "reads complete"

    print NOW(), "processing %d sources" % len(allSources)
    answers = useSources(allSources)
    print NOW(), "process complete"

    print NOW(), "sorting %d answers" % len(answers)
    answers.sort()
    print NOW(), "sort complete"

    outNameFile = outNamePrefix + ".names.txt"
    outEtymologyFile = outNamePrefix + ".etymology.txt"
    outStatsFile = outNamePrefix + ".stats.txt"

    print NOW(), "writing names and etymology"
    foutNames = open(outNameFile, "w")
    foutEty = open(outEtymologyFile, "w")

    for tag, name, etymology, datasource in answers:
        # id, name, datasource (if good name is found)
        line = "\t".join([tag, name])
        if datasource:
            line += "\t%s" % datasource
        line += "\n"

        foutNames.write(line)

        foutEty.write(etymology)
        foutEty.write("=====\n")

    foutNames.close()
    print NOW(), "%s written" % outNameFile

    foutEty.close()
    print NOW(), "%s written" % outEtymologyFile

    print NOW(), "computing stats"
    nameOriginCount = {}
    nameHist = {}
    for tag, name, etymology, datasource in answers:
        nameOriginCount[datasource] = nameOriginCount.setdefault(datasource, 0) + 1
        nameHist[name] = nameHist.setdefault(name, 0) + 1
    print NOW(), "compute complete"

    print NOW(), "writing stats"

    foutStats = open(outStatsFile, "w")
    foutStats.write("Names by source ('None' means no name assigned):\n\n")
    sortedSourcesByCount = sorted((value, key) for (key, value) in nameOriginCount.items())
    sortedSourcesByCount.reverse()
    for dsCount, ds in sortedSourcesByCount:
        foutStats.write("%4d\t%s\n" % (dsCount, ds))
    foutStats.write("\n\nNames by count (5 or more only):\n\n")
    sortedNamesByCount = sorted((value, key) for (key, value) in nameHist.items() if value >= 5)
    sortedNamesByCount.reverse()
    for nameCount, name in sortedNamesByCount:
        foutStats.write("%4d\t%s\n" % (nameCount, name))
    foutStats.close()
    print NOW(), "%s written" % outStatsFile

    print "genepidgin select done"


# these two functions are separated out for unit testing purposes
def parsePidginbFile(filename):
    assert filename.endswith(GPIDGINB), "looking only for files that end with .pidginb, found: %s" % filename
    sources = []
    for i, line in enumerate(open(filename)):
        sources.append(BlastNameSource(line, filename, i+1))
    return sources

def parsePidginhFile(filename):
    assert filename.endswith(GPIDGINH), "looking only for files that end with .pidginh, found: %s" % filename
    sources = []
    for i, line in enumerate(open(filename)):
        sources.append(HmmerNameSource(line, filename, i+1))
    return sources


def parseBlastM8File(filename, nameRefFiles):
    assert filename.endswith(BLASTM8) or filename.endswith(".csv"), "looking only for files that end with .blastm8 or .csv, found: %s" % filename
    sources = []
    for i, line in enumerate(open(filename)):
        sources.append(BlastM8NameSource(line, filename, i+1, nameRefFiles))
    return sources


# This block is an attempt to load all the names into memory.
# At some point, this approach will fail due to memory contraints.
NAME_REFERENCE = {}
def loadNameRefFiles(filenames):
    if not filenames:
        return
    print NOW(), "reading name ref files into memory"
    for filename in filenames:
        for blastsourcename in getValidBlastSources():
            if blastsourcename.lower() in filename.lower():
                parseNameRefFile(filename, blastsourcename)
def parseNameRefFile(filename, source):
    NAME_REFERENCE[source] = {}
    print NOW(), "reading", filename
    for line in open(filename):
        dbid, name = line.split("\t")
        name = name.strip()
        NAME_REFERENCE[source][dbid] = name
    print NOW(), "read", len(NAME_REFERENCE[source]), "entries, filed as %s" % source


class NameSource:
    """
    A NameSource represents a line of data within a genepidgin data file.

    It keeps track of all the source's information and can compare
    itself to other NameSources. The resulting list will be
    worst-to-best (lowest to highest), so the highest-confidence data
    source will appear at the end of the list.
    """
    def __init__(self):
        self.destId = None
        self.destStart = None
        self.destLen = None
        self.sourceId = None
        self.sourceStart = None
        self.sourceStop = None
        self.sourceLen = None
        self._rawName = None

        self.filteredName = None
        self.filterProcess = None

    def validateInts(self, fields):
        badints = []
        badints = [x for x in fields if not x.isdigit()]
        if badints:
            raise Exception, "%s\nExpected floats, received these: %s" % (self.getFileOrigin(), ", ".join(badints))

    # this isn't the most clever implementation ever, it's just
    # intended to catch horrible failures before retaining the results
    # of the type conversion
    def validateFloats(self, fields):
        badfloats = []
        badfloats = [x for x in fields if float(x) != float(str(float(x)))]
        if badfloats:
            raise Exception, "%s\nExpected floats, received these: %s" % (self.getFileOrigin(), ", ".join(badfloats))

    def validateStrings(self, fields):
        if None in fields or "" in fields:
            raise Exception, "%s\nExpected non-empty fields." % self.getFileOrigin()

    def getFileOrigin(self):
        if self.filename and self.fileline:
            return "%s:%s" % (self.filename, str(self.fileline))
        elif self.filename:
            return "%s" % (self.filename)
        else:
            return ""

    def getName(self):
        return self._rawName

    # When writing child classes, stick to the typical python sorting idiom:
    # Better is "greater" in terms of sorting, so the best (greatest)
    # item will be at the end of the list.
    def __cmp__(self):
        raise Exception, "This function should be overridden."

    def __str__(self):
        return self.getFileOrigin()

    def getDataOrigin(self):
        return self._datasource


class BlastNameSource(NameSource):

    def __init__(self, line=None, filename=None, fileline=None):
        NameSource.__init__(self)
        self.filename = filename
        self.fileline = fileline

        self.sourceAuth = None
        self.numIdentities = None
        #self.numSimilarities = None

        self._datasource = BLAST

        if line:
            self.parseLine(line, filename, fileline)

    # At the end of this process, we need the following fields set:
    # minCoverage, minPctIdentity [not anymore], sourceId, destId, sourceAuth
    # (and filename and fileline, if available)
    def parseLine(self, line, filename=None, fileline=None):
        self.filename = filename
        self.fileline = fileline

        fields = line.split("\t")
        fields = [x.strip() for x in fields]

        if not 12 <= len(fields) <= 13:
            raise Exception, "%s\nExpected twelve or thirteen fields per line, found %d" % (self.getFileOrigin(), len(fields))

        self.destId =     fields[0]
        destStart =       fields[1]
        destStop =        fields[2]
        destLen =         fields[3]
        self.sourceId =   fields[4]
        sourceStart =     fields[5]
        sourceStop =      fields[6]
        sourceLen =       fields[7]
        self.sourceAuth = fields[8]

        if self.sourceAuth not in getValidBlastSources():
            raise Exception, "%s\nExpected sourceAuth to be one of %s; found %s" % (self.getFileOrigin(), ",".join(getValidBlastSources()), self.sourceAuth)

        numIdentities =   fields[9]
        #numSimilarities = fields[10] # unused

        self._rawName =   fields[11]

        self.validateInts([destStart, destStop, destLen,
            sourceStart, sourceStop, sourceLen,	numIdentities])

        destStart = int(destStart)
        destStop = int(destStop)
        destLen = int(destLen)
        sourceStart = int(sourceStart)
        sourceStop = int(sourceStop)
        sourceLen = int(sourceLen)
        numIdentities = int(numIdentities)

        self.pctIdentity = self.computePctIdentity(destLen, numIdentities)
        self.minCoverage = self.computeMinCoverage(destStop, destStart, destLen,
          sourceStop, sourceStart, sourceLen)
        self.lengthDelta = self.computeLengthDelta(destLen, sourceLen)

        if self.sourceAuth == KEGG:
            self._rawName = self.correctForKeggOrthology(self._rawName)

    def computePctIdentity(self, alignmentLen, numIdentities):
        return float(numIdentities) / float(alignmentLen)

    def computeMinCoverage(self, destStop, destStart, destLen,
        sourceStop, sourceStart, sourceLen):

        sourceCoverage = float(sourceStop - sourceStart + 1) / float(sourceLen)
        destCoverage = float(destStop - destStart + 1) / float(destLen)
        return min(sourceCoverage, destCoverage)

    ##
    # Computes the difference in length between the source and destination
    # then divides it by the length of the shorter one.
    #
    def computeLengthDelta(self, destLen, sourceLen):
        return abs(destLen - sourceLen) / float(min(destLen, sourceLen))

    # In some databases, definition and orthology are comangled
    def correctForKeggOrthology(self, name):
        return genepidgin.cleaner.extractKEGG(name)

    # In all of the following comparisons, better is "greater" in
    # terms of sorting. The best item will be at the end of the list.
    def __cmp__(self, other):

        assert other._datasource == BLAST, "can't compare BLAST and HMMER hits directly"

        # using the string->num for sourcing
        res = cmp(getBlastSourceNum(self.sourceAuth), getBlastSourceNum(other.sourceAuth))
        if res != 0:
            return res

        res = cmp(self.pctIdentity, other.pctIdentity)
        if res != 0:
            return res

        return res

    def getDataOrigin(self):
        return "%s/%s" % (self._datasource, self.sourceAuth)


class BlastM8NameSource(BlastNameSource):
    def __init__(self, line=None, filename=None, fileline=None, nameRefFiles=None):
        BlastNameSource.__init__(self)
        self.filename = filename
        if not self.filename:
            raise Exception, "Need a filename here for source ranking. Apologies that it's listed as an optional parameter."
        self.fileline = fileline
        self.sourceAuth = self.getProteinLibraryName(self.filename)

        # when brute-forcing through a plain text file, we need to
        # find our plain-text file
        #self.myNameRefFile = self.findMyNameRefFile(nameRefFiles)

        if line:
            self.parseLine(line, filename, fileline)

    def getProteinLibraryName(self, filename):
        # Right now, we simply detect whether or not a protein library name
        # exists in the filename.
        for bsource in getValidBlastSources():
            if bsource.lower() in filename.lower():
                return bsource
        raise Exception, "Expected filename to contain one of the following strings: " + ",".join(getValidBlastSources())

    # We do a lot of prescreening of alignments before we ever look at
    # the content of the name. By deferring the actual name
    # comparison, we save on file/db queries.
    def getName(self):
        #name = self.getNameFromFlatFile()
        name = NAME_REFERENCE[self.sourceAuth][self.sourceId]

        if self.sourceAuth == KEGG:
            name = self.correctForKeggOrthology(name)

        return name

    # Since blast m8 format doesn't have the protein name in the id
    # field, we need another source to dereference and find the name,
    # if needed.  We determine that file from a simple source match in
    # the filename. Clumsy, I know.
    def findMyNameRefFile(self, nameRefFiles):
        self.myNameRefFile = None
        for nameRefFile in nameRefFiles:
            if self.sourceAuth.lower() in nameRefFile.lower():
                return nameRefFile
        raise Exception, "Could not determine what my name ref file should be: %s / %s" % (self.sourceAuth, ",".join(nameRefFiles))

    # This is a brute-force scan of a flat file. Typically takes 5s
    # per name, which is unacceptable for more than a few names.
    def getNameFromFlatFile(self):
        for line in open(self.myNameRefFile):
            sourceId, sourceName = line.split("\t")
            if self.sourceId != sourceId:
                continue
            sourceName = sourceName.strip()
            print NOW(), "-- retrieved name for %s in %s" % (self.sourceId, self.myNameRefFile)
            return sourceName

    def parseLine(self, line, filename=None, fileline=None):

        self.filename = filename
        self.fileline = fileline

        fields = line.split("\t")
        fields = [x.strip() for x in fields]

        if not len(fields) == 12:
            raise Exception, "%s\nExpected twelve fields per line, found %d" % (self.getFileOrigin(), len(fields))

        # Following is the header produced by blast -m 9, which is the
        # same as -m 8 but has this explanatory header.

        ## BLASTX 2.2.21 [Jun-14-2009]
        # Query: 7000000143106953:1-60000
        # Database: /seq/annotation/prod/data/features/uniref90/sequences.fasta
        # Fields: Query id, Subject id, % identity, alignment length, mismatches, gap openings, q. start, q. end, s. start, s. end, e-value, bit score

        self.destId =          fields[0]
        self.sourceId =        fields[1]

        percentIdentity = fields[2]
        alignmentLength = fields[3]

        mismatches =      fields[4]
        gapOpenings =     fields[5]

        destStart =       fields[6]
        destStop =        fields[7]

        sourceStart =     fields[8]
        sourceStop =      fields[9]

        # unused
        #self.evalue =          fields[10]
        #self.bitscore =        fields[11]

        self.validateStrings([self.destId, self.sourceId])

        self.validateInts([alignmentLength, mismatches, gapOpenings,
            destStart, destStop, sourceStart, sourceStop])

        alignmentLength = int(alignmentLength)
        mismatches =      int(mismatches)
        gapOpenings =     int(gapOpenings)
        destStart =       int(destStart)
        destStop =        int(destStop)
        sourceStart =     int(sourceStart)
        sourceStop =      int(sourceStop)

        #self.validateFloats([self.percentIdentity, self.evalue, self.bitscore])
        self.validateFloats([percentIdentity])
        self.pctIdentity = float(percentIdentity) / 100 # converting 33% to 0.33

        destLen = destStop - destStart + 1
        sourceLen = sourceStop - sourceStart + 1

        # we use identities in our calculations, and blast -m7 provides this.
        # blast -m8 provides (alignment length, mismatches, gaps) from
        # which we can derive identities
        numIdentities = alignmentLength - mismatches - gapOpenings
        self.minCoverage = self.computeMinCoverage(destStop, destStart, destLen, sourceStop, sourceStart, sourceLen)
        self.lengthDelta = self.computeLengthDelta(destLen, sourceLen)


class HmmerNameSource(NameSource):

    def __init__(self, line=None, filename=None, fileline=None):
        NameSource.__init__(self)
        self.filename = filename
        self.fileline = fileline

        self.score = None
        self.familyTrustedCutoff = None
        self.eValue = None

        self._datasource = HMMER

        if line:
            self.parseLine(line, filename, fileline)


    def parseLine(self, line, filename=None, fileline=None):
        self.filename = filename
        self.fileline = fileline

        fields = line.split("\t")
        fields = [x.strip() for x in fields]

        if not 12 <= len(fields) <= 13:
            raise Exception, "%s\nExpected twelve or thirteen fields per line, found %d" % (self.getFileOrigin(), len(fields))

        self.destId =              fields[0]
        self.destStart =           fields[1]
        self.destStop =            fields[2]
        self.destLen =             fields[3]
        self.sourceId =            fields[4]
        self.sourceStart =         fields[5]
        self.sourceStop =          fields[6]
        self.sourceLen =           fields[7]
        self.score =               fields[8]
        self.familyTrustedCutoff = fields[9]
        self.eValue =              fields[10]
        self._rawName =            fields[11]

        # validate numbers
        self.validateInts([
            self.destStart, self.destStop, self.destLen,
            self.sourceStart, self.sourceStop, self.sourceLen,
        ])

        #
        # convert to computational values
        #
        self.destStart = int(self.destStart)
        self.destStop = int(self.destStop)
        self.destLen = int(self.destLen)
        self.sourceStart = int(self.sourceStart)
        self.sourceStop = int(self.sourceStop)
        self.sourceLen = int(self.sourceLen)
        # validate floats
        self.validateFloats([self.familyTrustedCutoff, self.eValue, self.score])
        self.familyTrustedCutoff = float(self.familyTrustedCutoff)
        self.eValue = float(self.eValue)
        self.score = float(self.score)
        # The lowest practical value of e-value is 0.0, but hmmer
        # occasionally emits negative values. We don't particularly care
        # about the result of those negative values.
        self.eValue = max(self.eValue, 0.0)

        # precomputing this for sorting purposes
        if self.score > self.familyTrustedCutoff:
            self.scoreExceedsCutoff = 1
        else:
            self.scoreExceedsCutoff = 0

    # In all of the following comparisons, better is "greater" in
    # terms of sorting.  The best item will be at the end of the list.
    def __cmp__(self, other):

        assert other._datasource == HMMER, "can't compare BLAST and HMMER hits directly"

        # exceeding the trusted family cutoff is better than not doing so
        res = cmp(self.scoreExceedsCutoff, other.scoreExceedsCutoff)
        if res != 0:
            return res

        # a lower evalue is better than a higher one
        res = -cmp(self.eValue, other.eValue)
        if res != 0:
            return res

        # higher score better than lower score
        res = cmp(self.score, other.score)
        if res != 0:
            return res

        res = cmp(self.destLen, other.destLen)
        if res != 0:
            return res

        res = cmp(self.sourceLen, other.sourceLen)
        return res

    def getDataOrigin(self):
        return "%s/%s" % (self._datasource, self.sourceId)


def getSources(filename, nameRefFiles=None):
    """ Reads a genepidgin data file to get data sources. """
    if filename.endswith(GPIDGINH):
        return parsePidginhFile(filename)
    elif filename.endswith(GPIDGINB):
        return parsePidginbFile(filename)
    elif (filename.endswith(BLASTM8) or filename.endswith(".csv")):
        return parseBlastM8File(filename, nameRefFiles)
    else:
        raise Exception, "Don't know what to do with this file: %s" % filename


# Takes in a list of NameSources, returns a map of those sources with the
# id as the keys.
# We keep them segregated because "blast better than hmmer"
# Putting them all in a single pile will require smarter etymology.
#{
#	destId: (hmmersources, blastsources),
#}
def pivotOnIds(sources):
    sourcesById = {}
    for source in sources:
        if source._datasource == HMMER:
            sourcesById.setdefault( source.destId, ([], []) )[0].append(source)
        elif source._datasource == BLAST:
            sourcesById.setdefault( source.destId, ([], []) )[1].append(source)
        else:
            raise Exception, "Don't know what to do with this source: %s" % source
    return sourcesById


def createNamingProcessEtymology(source):
    etymology = "Found an acceptable name in the %s sources. The one we liked best came from:\n%s\n" % (source.getDataOrigin(), source.getFileOrigin())
    if source.filterProcess:
        etymology += "This source's name was modified by genepidgin.cleaner:\n"
        etymology += "%s\n" % source.filterProcess
    else:
        etymology += "This source's name did not need to be cleaned by genepidgin.cleaner.\n"
    return etymology


def useSources(allSources):
    sourcesById = pivotOnIds(allSources)

    answersById = []

    for key in sourcesById:
        hmmerSources, blastSources = sourcesById[key]

        etymology = "%s\n" % key
        bestSource = None
        bestName = ""
        bestDataOrigin = None

        # quick exit if we need one
        if not hmmerSources and not blastSources:
            etymology += "No sources of any kind to process.\n"
            etymology += "Final name: %s\n" % genepidgin.cleaner.DEFAULTNAME
            answersById.append( (key, genepidgin.cleaner.DEFAULTNAME, etymology, bestDataOrigin) )
            continue

        # XXX blast first before hmmer, QZ changed his mind again
        if not bestSource:
            culledBlastSources, blastEtymology = cullBlastSources(blastSources)
            etymology += blastEtymology
            if not culledBlastSources:
                etymology += "No name was derived from blast sources.\n"
            else:
                culledBlastSources.sort()
                culledBlastSources.reverse() # best answer is at the end
                bestSource, nameety = chooseBestSourceByName(culledBlastSources, "blast")
                etymology += nameety

        # XXX blast first before hmmer, QZ changed his mind again
        # first, see if any hmmer has workable input
        # of those, see if any have a decent name
        if not bestSource:
            culledHmmerSources, hmmerEtymology = cullHmmerSources(hmmerSources)
            etymology += hmmerEtymology
            if not culledHmmerSources:
                etymology += "No name was derived from hmmer sources.\n"
            else:
                culledHmmerSources.sort()
                culledHmmerSources.reverse() # best answer is at the end
                bestSource, nameety = chooseBestSourceByName(culledHmmerSources, "hmmer")
                etymology += nameety

        # if we have a winner at this point, dig out and attach the
        # naming filter process
        if bestSource:
            bestName = bestSource.filteredName
            etymology += createNamingProcessEtymology(bestSource)
            bestDataOrigin = bestSource.getDataOrigin()

        else:
            etymology += "No name was ultimately selected from any of the supplied sources.\n"
            bestName = genepidgin.cleaner.DEFAULTNAME

        etymology += "Final name: %s\n" % bestName

        answersById.append( (key, bestName, etymology, bestDataOrigin) )

    return answersById


def removedWord(base, remaining):
    if remaining == 0:
        return "All"
    elif base == remaining:
        return "No"
    return str(base - remaining)


# given two sets of features, with one being a subset of the other,
# yield a noun clause and indeterminate verb describing the difference
# in a form suitable to begin a sentence. Examples:
#
# a set of 6 and a set of 4 would return "2 x sources were"
# a set of 5 and a set of 0 would return "All x sources were"
# a set of 5 and a set of 5 would return "0 x sources were"
# a set of 2 and a set of 1 would return "1 x source was"
def diffClause(set1, set2, identifier):
    if len(set2) == 0:
        return "All %s sources were" % identifier
    if len(set1) == len(set2):
        return "0 %s sources were" % identifier
    if len(set1) - len(set2) == 1:
        return "1 %s source was" % identifier
    return "%d %s sources were" % ( len(set1) - len(set2) , identifier)


# The etymology within this process describes paring down a set of
# hmmer sources
def cullHmmerSources(sources):
    ety = ""
    if not sources:
        ety += "0 hmmer sources found.\n"
        return (None, ety)
    elif len(sources) == 1:
        ety += "1 hmmer source found.\n"
    else:
        ety += "%d hmmer sources found.\n" % len(sources)

    # YYY: I thought that hits who exceeded cutoff were preferred, but
    # if they're the only admissable sources, we don't have to
    # precompute for sorting
    scoreValidSources = [x for x in sources if x.scoreExceedsCutoff]
    subj = diffClause(sources, scoreValidSources, HMMER)
    ety += "%s removed due to not meeting the trusted family score.\n" % subj

    return (scoreValidSources, ety)


# The etymology within this process describes paring down a set of
# blast sources
def cullBlastSources(sources, coverageCutoff=0.7, lengthDeltaCutoff=0.1, identityCutoff=0.7, identityWindow=0.1):
    ety = ""
    if not sources:
        ety += "0 blast sources were found.\n"
        return (None, ety)
    elif len(sources) == 1:
        ety += "1 blast source was found.\n"
    else:
        ety += "%d blast sources were found.\n" % len(sources)

    coveredSources = [x for x in sources if x.minCoverage >= coverageCutoff]
    subj = diffClause(sources, coveredSources, BLAST)
    ety += "%s removed by filtering for low coverage (< %.2f).\n" % (subj, coverageCutoff)

    if not coveredSources:
        return (None, ety)

    similarSources = [x for x in coveredSources if x.lengthDelta <= lengthDeltaCutoff]
    subj = diffClause(coveredSources, similarSources, BLAST)
    ety += "%s removed by filtering for dissimilar lengths (> %.2f).\n" % (subj, lengthDeltaCutoff)

    if not similarSources:
        return (None, ety)

    upperPctIdentity = max([x.pctIdentity for x in similarSources])
    lowestRemainingPctIdentity = min([x.pctIdentity for x in similarSources])

    ety += "The highest percent identity of any remaining blast source is %.3f. The lowest is %.3f.\n" % (upperPctIdentity, lowestRemainingPctIdentity)
    lowerPctIdentity = max(identityCutoff, upperPctIdentity - identityWindow)
    if upperPctIdentity < identityCutoff:
        ety += "No blast sources met the minimum criteria for percent identity (%.2f).\n" % identityCutoff
        return (None, ety)

    pctIdenSources = [x for x in similarSources if x.pctIdentity >= lowerPctIdentity]
    subj = diffClause(similarSources, pctIdenSources, BLAST)
    ety += "%s removed due to not being within the percent identity window (%.03f, %.03f).\n" % (subj, upperPctIdentity, lowerPctIdentity)

    return (pctIdenSources, ety)
