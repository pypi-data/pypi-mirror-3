#!/bin/env python

import re

# command parameters
TEXT = "text"
HTML = "html"
SILENT = "silent"

#
# Filters are text modification tools which have an extended
# description to describe their intent. Thus far, there are three
# subclasses based on extended regular expressions (FilterReplace,
# FilterRemove, FilterKill) and one based on a callable function or
# class (FilterByFunction). They are paper-thin shells around simple
# functions, with only a standard calling method and a description of
# what the filter in question does.
#
# These descriptions are used in aggregate by FilterGroup to generate
# nice summaries of what happens to a name as it passes through a
# large number of filters.
#
# Filters have only two requirements:
# 1) desc string providing a one-line summary of the Filter's function
# 2) _filterImpl() function that takes in a string and returns a modified
# string
#
# Optionally, a Filter may define a third method:
# 3) _searchImpl() function that takes in a string and returns 1 if the
# string has some quality, 0 if not
#
# Each filter can also have a number of tags attached to it via __init__
# (skipif, runif), to assist in sorting out whether to run a given filter
# on a given input.
#
# skipif: a list of one or more tags (strings). When FilterGroup.run()
# is called with skipif populated, any exact string match between an
# element in the set supplied at invocation and an element in the set
# supplied at creation will prevent the filter from running.
#
# runif: a list of one more tags (strings). If runif is set when
# FilterGroup.run() is called, an exact string match is required between
# an element in the set supplied at invocation and an element in the set
# supplied at creation in order for this filter to run.
#
# In the case when there is a match of both skipif and runif, skipif
# takes priority; that is, the filter will be skipped.
#
# In the genepidgin distribution, these tags are a controlled
# vocabulary and are defined in cleaner.py. However this is not
# currently enforced and any string may be supplied via skipif or
# runif.
#
# For example, to create a filter that you want to run on only on
# names that were automatically generated (as opposed to assigned by
# an annotator), you would declare it as follows:
#
# fr = FilterReplace(pattern, replacement, desc, skipif=[cleaner.NOTAUTOGEN])
#
# Then, call this filter on manually annotated names as follows:
#
# fgroup.run(inputtext, skipif=[cleaner.NOTAUTOGEN])
#
# And call it on automatically assigned names as follows:
#
# fgroup.run(inputtext)
#
# Any filter tagged with NOTAUTOGEN will be skipped for manually
# assigned names.
#
# @see FilterGroup
#
class Filter:
    def __init__(self, skipif=[], runif=[]):
        self.skipif = skipif
        self.runif = runif
    # return 1 if should execute this filter
    # only execute when the given tag aligns with this filters conditions
    def runCheck(self, runif):
        # if no flag is set, run always
        if not self.runif:
            return 1
        # else run, only on match
        for run in runif:
            if run in self.runif:
                return 1
        return 0
    # return 1 if should skip this filter (not run it)
    # only execute when none of the given conditions align with this filter
    def skipCheck(self, skipif):
        for skip in skipif:
            if skip in self.skipif:
                return 1
        return 0
    # This function should not be overridden. It does the tag-checking
    # and then calls on the subclass-implementation to do the actual
    # filtering.
    def filter(self, name, skipif=[], runif=[]):
        if self.skipCheck(skipif):
            return name
        if not self.runCheck(runif):
            return name
        return self._filterImpl(name)

    def search(self, name, skipif=[], runif=[]):
        if self.skipCheck(skipif):
            return name
        if not self.runCheck(runif):
            return name
        return self._searchImpl(name)

    def _filterImpl(self, name):
        raise "This method should never be called; it must be overridden by the subclass."

    def _searchImpl(self, name):
        raise "This method should never be called; it must be overridden by the subclass."

##
# @brief A regular expression that has an extended description.
#
# This class is an extended regex compile/sub pattern.
#
# The automated descriptions won't mean much to a user, as it's based
# on regex strings.
#
# @param pattern A compiled regular expression.
# @param replace A replacement string that would fit well in pattern.sub() method.
#
# @see Filter
class FilterReplace(Filter):
    '''
    replace can be either a string or a function, it feeds
    directly into the re.sub field
    '''
    def __init__(self, pattern, replace, desc=None, skipif=[], runif=[]):
        Filter.__init__(self, skipif, runif)
        self.pattern = pattern
        self.replace = replace
        self.desc = desc or "replace /%s/ with /%s/" % (self.pattern.pattern, self.replace)

    def _filterImpl(self, name):
        return self.pattern.sub(self.replace, name)

    def _searchImpl(self, name):
        return self.pattern.search(name)

##
# @brief When filtering, replace all matches of a given pattern with an empty string
#
# A convenience class built on FilterReplace that has appropriate
# generated descriptions.
#
# @see FilterReplace
class FilterRemove(FilterReplace):
    def __init__(self, pattern, desc=None, skipif=[], runif=[]):
        FilterReplace.__init__(self,
            pattern,
            "",
            desc or "trimmed per /%s/" % pattern.pattern,
            skipif,
            runif
        )

##
# @brief Given a function, run that given function on an object
#
# @see Filter
class FilterByFunction(Filter):
    def __init__(self, customFunction, desc, skipif=[], runif=[]):
        Filter.__init__(self, skipif, runif)
        self.customFunction = customFunction
        self.desc = desc
        if not self.desc:
            raise "a useful description must be provided to FilterByFunction"

    def _filterImpl(self, name):
        return self.customFunction(name)

    def _searchImpl(self, name):
        # if the function changes the name, presumably it matches something in it
        return name != self.customFunction(name)

##
# @brief Runs a string/name through a series of Filters, optionally generating summary of changes.
#
# @param outputType One of TEXT, HTML, or SILENT. Modifies the return value of run().
# If SILENT, return only the filtered name.
# If TEXT, return a text block describing the modifications (if any)
# to the given name.
# If HTML, return html code describing the modifications (if any) to
# the given name.
# @param showPattern If 1, insert a line with the coded pattern. Useful when
# your description doesn't include the pattern.
#
class FilterGroup:
    def __init__(self, outputType=SILENT, showPattern=0):
        self.outputType = outputType
        self.filterList = []
        if self.outputType != TEXT and self.outputType != HTML and self.outputType != SILENT:
            raise "outputType format [%s] not supported" % self.outputType
        self.showPattern = showPattern
        pass

    def add(self, filter):
        self.filterList.append(filter)
    def addAll(self, filterList):
        self.filterList.extend(filterList)

    ##
    # Run the name through this object's currently stored Filters.
    #
    # @param name Name to be filtered.
    # @param skipif If any string in this list matches any string in a given
    #  Filter's skipif, that filter WILL NOT be run on the name.
    # @param runif If any string in this list matches any string in a given
    #  Filter's runif field, that filter WILL be run on the name.
    # @param indexMask If not None, must be a set or list of integers.
    #  (Preferably a set.) Only those Filters whose indices are in indexMask
    #  will be run.
    #
    # @see Filter
    #
    def run(self, name, skipif=[], runif=[], indexMask=None):
        originalName = name
        modSet = []
        for i in xrange(0, len(self.filterList)):
            if indexMask is not None and (i not in indexMask):
                continue

            tf = self.filterList[i]
            # get filtered name
            newName = tf.filter(name, skipif, runif)
            # store modification data, if necessary
            # (only the Filters that were used)
            if newName != name:
                localpattern = None
                if hasattr(tf, "pattern"):
                    localpattern = tf.pattern.pattern
                else:
                    localpattern = "custom function"
                mod = [newName, tf.desc, localpattern]
                modSet.append(mod)
            # continue the filtering process
            name = newName

        # format and return
        if self.outputType == TEXT:
            if name == originalName:
                return (name, None)
            return (name, self.generateText(originalName, modSet))
        elif self.outputType == HTML:
            if name == originalName:
                return (name, None)
            return (name, self.generateHtml(originalName, modSet))
        elif self.outputType == SILENT:
            return name

    ##
    # Searches a name against this object's currently stored Filters.
    #
    # @return a Set of integers indicating the index of the Filters
    #  that match the name.
    #
    # @param name Name to be searched.
    # @param skipif If any string in this list matches any string in a given
    #  Filter's skipif, that filter WILL NOT be run on the name.
    # @param runif If any string in this list matches any string in a given
    #  Filter's runif field, that filter WILL be run on the name.
    #
    # @see Filter
    #
    def search(self, name, skipif=[], runif=[]):
        ret = set()
        for i in xrange(0, len(self.filterList)):
            tf = self.filterList[i]
            if tf.search(name, skipif, runif):
                ret.add(i)

        return ret

    '''
    filtered name in X steps
    0) original:
    1)   reason:
        pattern:
       filtered:
    2)   reason:
        pattern:
       filtered:
    '''
    def generateText(self, originalName, modSet):
        lines = []
        steps = len(modSet) == 1 and "step" or "steps"
        lines.append("filtered name in %d %s:" % (len(modSet), steps))
        lines.append("0) original: %s" % originalName)
        for mod, i in zip(modSet, range(1, len(modSet)+1)):
            name, desc, pattern = mod
            lines.append("%d)   reason: %s" % (i, desc))
            if self.showPattern:
                lines.append("    pattern: %s" % pattern)
            lines.append("   filtered: %s" % name)
        return "\n".join(lines)

