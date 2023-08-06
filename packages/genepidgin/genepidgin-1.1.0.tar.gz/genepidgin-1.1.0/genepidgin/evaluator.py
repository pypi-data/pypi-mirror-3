#!/bin/env python

import cleaner, util
import time

def simpleCategories(filename, timeIt=False):
    fields = util.simpleNamesFileReader(filename)
    names = [x[1] for x in fields]

    print "Loaded %d names from file %s." % (len(names), filename)

    untouchedCount = 0
    filteredCount = 0
    weakCount = 0
    genericCount = 0
    poorCount = 0

    pc = cleaner.BioName()

    print "Loaded genepidgin.cleaner filters."
    print "Running filters on names."

    if timeIt:
        startTime = time.time()

    for name in names:
        filtered = pc.filter(name)

        # good names
        if filtered is not None:
            if filtered == name:
                untouchedCount += 1
            else:
                filteredCount += 1
        # bad names
        else:
            if pc.isGenericName(name):
                genericCount += 1
            elif pc.isWeakName(name):
                weakCount += 1
            else:
                poorCount += 1

    usefulCount = untouchedCount + filteredCount
    unusableCount = genericCount + weakCount + poorCount
    print "-----"
    print "For %d names in file: %s" % (len(names), filename)
    print "%d (%.03f%%) useful names:" % (usefulCount, float(usefulCount)/len(names) * 100)
    print "- %d (%.03f%%) untouched names" % (untouchedCount, float(untouchedCount)/len(names) * 100)
    print "- %d (%.03f%%) filtered names" % (filteredCount, float(filteredCount)/len(names) * 100)
    print "%d (%.03f%%) unusable names" % (unusableCount, float(unusableCount)/len(names) * 100)
    print "- %d (%.03f%%) generic names" % (genericCount, float(genericCount)/len(names) * 100)
    print "- %d (%.03f%%) weak names" % (weakCount, float(weakCount)/len(names) * 100)
    print "- %d (%.03f%%) poor names" % (poorCount, float(poorCount)/len(names) * 100)

    if timeIt:
        stopTime = time.time()
        runTime = stopTime - startTime
        nameRate = len(names)/float(runTime)
        print "-----"
        print "%d names in %.2f seconds (%.2f/s)" % (len(names), runTime, nameRate)
