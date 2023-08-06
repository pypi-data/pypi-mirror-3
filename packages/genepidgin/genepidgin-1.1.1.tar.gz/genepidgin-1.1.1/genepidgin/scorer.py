#!/bin/env python

import os.path
import sys

import distance
import util

_dist_tool = distance.DistanceTool()
DIST_METHOD = _dist_tool.distance
DIST_MIN, DIST_MAX = _dist_tool.min, _dist_tool.max


#
# Reports on the distance between protein names contained in flat file(s).
#
# Given a reference and one or more query files, generate one scoring
# comparison per query file. In the case of multiple query files,
# generate a summary showing the best query file. See the
# documentation for details.
#
# Each line in the two-way comparison result will consist of the following
# tab-separated fields:
#
# 0.  ID. The first field of an entry from the reference file.
# 1.  Reference name. The reference name used for the comparison.
# 2.  Query name. The query name used for the comparison.
# 3.  Score. The distance between the two names.
#
# If a summary file is generated, each line in that file will consist of
# the following tab-separated fields:
#
# 0.  ID. The first field of an entry from the reference file.
# 1.  Reference name. The reference name used for the comparison.
# 2.  Best query name. Of all the query names supplied,
#     this name most closely matched the reference name.
# 3.  Score. The distance between the two names.
# 4.  Best query source. The basename of the file from which the best
#     query name came. In some cases there will be a tie for best
#     query name; in that case, multiple basenames will be in this
#     column, separated by spaces.
#
def compareFiles(refFile, qryFiles):

    refList = util.simpleNamesFileReader(refFile)
    refMap = dict( (nid, name) for nid, name in refList )
    print("read %s" % refFile)

    qryMaps = {}    # { file: { id: name } }
    scoreMaps = {}  # { file: { id: score } }

    # read/score everything in one go, so that we write nothing in the case of error
    for qryFile in qryFiles:
        qryMap = dict( (nid, name) for nid, name in util.simpleNamesFileReader(qryFile) )
        print("read %s" % qryFile)
        qryMaps[qryFile] = qryMap
        print("scoring %s vs %s" % (refFile, qryFile))
        scoreMaps[qryFile] = scoreNames(refMap, qryMap)

    # write all comparisons in one go
    for qryFile in qryFiles:
        outputFile = qryFile + ".compared"
        print("writing %s" % outputFile)
        writeNamesAndScores(refList, qryMaps[qryFile], scoreMaps[qryFile], outputFile)

    # no best needed if only one comparison
    if len(qryFiles) == 1:
        return

    print("collecting best names and scores of all queries")
    bestScoreMap, bestSourceMap, bestNameMap = getBestScoresAndSources(refList, qryFiles, qryMaps, scoreMaps)
    outputFile = refFile + ".summary"
    print("writing %s" % outputFile)
    writeNamesAndScores(refList, bestNameMap, bestScoreMap, outputFile, bestSourceMap)


#
# Given a referenceList [( id, name ), ...], a list of query files,
# a dictionary containing queryNameMaps { { queryFile: { id: name } },
# and a dictionary containing scoreMaps { { queryFile: { id: score } },
# generate and return three new dictionaries:
#
# - a best score dictionary:  { id: best score }
# - a best source dictionary: { id: best source }
# - a best name dictionary:   { id: best name }
#
# In the case of multiple names scoring equally, the first such name
# is used and the best source is a semicolon-joined list of all query
# files containing a name of that score.
#
def getBestScoresAndSources(refList, qryFiles, qryMaps, scoreMaps):

    bestScoreMap = {}
    bestSourceMap = {}
    bestNameMap = {}

    for nid, refName in refList:
        bestScore = sys.maxint
        bestName = ""
        bestSources = []

        for qryFile in qryFiles:
            if nid not in qryMaps[qryFile]:
                continue
            score = scoreMaps[qryFile].get(nid)
            if score < bestScore:
                bestScore = score
                bestSources = [os.path.basename(qryFile)]
                # explictly not get() because we should have a good name here
                bestName = qryMaps[qryFile][nid]
            elif score == bestScore:
                bestSources.append(os.path.basename(qryFile))

        bestScoreMap[nid] = bestScore
        bestSourceMap[nid] = ";".join(bestSources)
        bestNameMap[nid] = bestName

    return bestScoreMap, bestSourceMap, bestNameMap


#
# Given a referenceList [( id, name ), ...], a queryNameMap { id: name
# }, and a scoreMap { id: score }, write a comparison of the names in
# the reference list against the names and scores found in their
# corresponding maps.
#
# Each line will have the following tab-joined fields:
#	name id, score, referenceName, queryName
#
# If a sourceMap { id: source } is provided, that information is made
# into a fifth field.
#
def writeNamesAndScores(refList, nameMap, scoreMap, outputFile, sourceMap=None):
    fout = open(outputFile, 'w')
    for nid, refName in refList:
        qName = nameMap.get(nid, "")
        score = scoreMap.get(nid, DIST_MAX)
        line = "\t".join([nid, "%.02f" % score, refName, qName ])
        if sourceMap:
            line += "\t%s" % sourceMap.get(nid, "")
        fout.write(line + "\n")
    fout.close()


# Given a reference and query dictionary { id: name }, generate and
# return a dictionary of scores { id: score } using DIST_METHOD.
# Every name in the reference map will have an entry in the results.
# If no entry is found, a score of DIST_MAX is assigned.
def scoreNames(referenceNames, queryNames):
    scores = {}
    for nid in referenceNames.keys():
        score = None
        #print("scoring %s\nr: %s\nq: %s" % (nid, referenceNames.get(nid), queryNames.get(nid))
        if nid in queryNames.keys():
            score = DIST_METHOD(referenceNames[nid], queryNames[nid])
        else:
            score = DIST_MAX
        #print("score: %s" score)
        scores[nid] = score
    return scores


#
# a couple of side tools to help in data analysis
#


# prints all the identical names
def identicalNames(filename, minCount=5, outputFile=None, filtered=None):

    fields = util.simpleNamesFileReader(filename)
    names = [x[1] for x in fields]

    if filtered:
        import cleaner
        pc = cleaner.BioName()
        names = [pc.filter(x) for x in names]

    counts = {}
    for name in names:
        counts[name] = counts.setdefault(name, 0) + 1

    for name in counts.keys():
        if counts[name] < minCount:
            continue
        msg = "%d\t%s" % (counts[name], name)
        if outputFile:
            outputFile.write(msg + "\n")
        else:
            print(msg)


# reads score files and yields an array of numbers (scores)
def getScores(filename):
    scores = []
    for line in open(filename):
        id, score, ref, qry = line.split("\t")
        scores.append(float(score))
    return scores


#
# Assuming the default distance tool, we've applied the following
# unscientific descriptions to the scores:
#
# 0.0 = functionally identical
#     } excellent
# 0.1
#     } good
# 0.3
#     } possibly useful, but the correlation is unlikely
# 0.5
#     } not useful; a miss
# 1.0 = completely different
#

#
# In our internal analysis, we categorize results based on
# these ranges. The easiest way to do this is:
#
# If you have numpy
#
# import numpy
# import genepidgin.scorer
# scores = genepidgin.scorer.getScores(filename)
# numpy.histogram(scores, genepidgin.scorer.bins_numpy)
#
# If you don't have numpy, get numpy. If you don't want to:
#
# import genepidgin.scorer
# scores = genepidgin.scorer.getScores(filename)
# genepidgin.scorer.distanceBin(scores)
#

bins = [0.0, 0.1, 0.3, 0.5, 1.0]

# I like capturing the 0.0 and 1.0 hits in their own bins.
# The following bin settings result in the following bins:
# 0.0-0.0, 0.0-0.1, 0.1-0.3, 0.3-0.5, 0.5-1.0, 1.0-1.0
bins_numpy = [0.0, 0.0, 0.1, 0.3, 0.5, 1.0, 1.0]

# take the output of the distance algorithm, bin it, print it
# if you have numpy, use that instead, as this sucks
def distanceBin(filename):

    scores = getScores(filename)

    counts = simpleBin(scores, bins)

    print("dist\tcount\tpct")
    for level in bins:
        percentage = float(counts[level]) / float(len(scores))
        print("\t".join([str(level), str(counts[level]), str("%.2f" % percentage)]))
    print("sum\t%d\t1.0" % len(scores))


# numbers = [1, 1, 1, 2, 3, 4, 5, 6, 7, 8]
# categories = [3, 6, 8]
# output = {3: 5, 6: 3, 8: 2}
#
# there are five numbers x <= 3
# there are three numbers 3 < x <= 6
# and two 6 < x <= 8
def simpleBin(numbers, categories):
    categories.sort()
    counts = {}
    for number in numbers:
        for cat in categories:
            if number <= cat:
                counts[cat] = counts.setdefault(cat, 0) + 1
                break
    return counts
