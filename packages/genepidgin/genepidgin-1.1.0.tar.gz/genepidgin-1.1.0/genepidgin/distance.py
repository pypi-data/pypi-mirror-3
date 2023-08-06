#!/bin/env python

from __future__ import nested_scopes

import operator
import re
import sys

import cleaner
import filters
import stemmer

from UserList import UserList

# A set-like object that preserves order and is compatible with Python
# 2.1.  The object is suitable for iteration and list comprehensions.
class OrderedSet(UserList):

    def __init__(self, coll=None):
        UserList.__init__(self)
        # use keys in this dict to enforce set-ness
        self._guard = {}
        if coll is not None:
            self.addAll(coll)

    def add(self, obj):
        if not self._guard.has_key(obj):
            self._guard[obj] = 1
            self.append(obj)
            return 1
        return 0

    def addAll(self, objs):
        for obj in objs:
            self.add(obj)

    def remove(self, obj):
        if self._guard.has_key(obj):
            del self._guard[obj]
            UserList.remove(self, obj)

    def removeAll(self, objs):
        for obj in objs:
            self.remove(obj)

    # Retains only the elements in this set that are contained in the
    # specified collection In other words, removes from this set all of
    # its elements that are not contained in the specified collection.
    #
    # If the specified collection is also a set, this operation
    # effectively modifies this set so that its value is the
    # intersection of the two sets.
    #
    # @see JDK, that's where I got this doc string
    def retainAll(self, objs):
        toDelete = []
        for el in self:
            if hasattr(objs, "contains"):
                if not objs.contains(el):
                    toDelete.append(el)
            elif (not el in objs):
                toDelete.append(el)

        self.removeAll(toDelete)

    def clone(self):
        return OrderedSet(self.data)

    def contains(self, obj):
        return self._guard.has_key(obj)


# Returns a FilterGroup that includes all lowConfidence filters from
# BioName, as well as a simple FilterRemove object for each word in
# the supplied list
#
# @param wordlist an iterable list of strings
# @note the words in wordlist are convenience-wrapped to form regular expressions.
def lowConfidenceFilterGroup(*wordlist):
    removeGroup = filters.FilterGroup(showPattern=1, outputType=filters.SILENT)
    removeGroup.addAll(cleaner.BioName().getLowConfidenceFilters())
    removeGroup.addAll([filters.FilterRemove(re.compile(r"(?i)\b%s\b" % x)) for x in wordlist])
    return removeGroup

# Returns a FilterGroup that includes all id-removing filters from
# BioName, as well as a simple FilterRemove object for each id in the
# supplied list
# @param wordlist an iterable list of strings.
# @note for IDs unlike words we don't convenience-wrap the strings in \b's or (?i)'s
def idFilterGroup(*idlist):
    removeGroup = filters.FilterGroup(showPattern=1, outputType=filters.SILENT)
    removeGroup.addAll(cleaner.BioName().getIdDeleters())
    removeGroup.addAll([filters.FilterRemove(re.compile(x)) for x in idlist])
    return removeGroup

# Returns a FilterGroup that includes all whitespace-removing filters
# from BioName, as well as a simple FilterRemove object for each
# pattern in the supplied list
#
# @param wordlist an iterable list of strings.
# @note for IDs unlike words we don't convenience-wrap the strings in \b's or (?i)'s
def punctAndWhitespaceFilterGroup(*patlist):
    removeGroup = filters.FilterGroup(showPattern=1, outputType=filters.SILENT)
    removeGroup.addAll([cleaner.FilterRemove(re.compile(x)) for x in patlist])
    removeGroup.add(filters.FilterByFunction(cleaner.cleanupWhitespace, "cleanup whitespace"))
    return removeGroup

# This class strips out tokens (words) that are not generally
# informative when determining the distance between names.
class UninformativeTokenRemover:

    def __init__(self):
        # An incomplete list of non-informative glue words. Remove all
        # these guys and you have an informative yet non-grammatical
        # name skeleton.
        # We don't compare TC#'s and EC#'s in names because other
        # tools do that.
        self.filterGroup = lowConfidenceFilterGroup(
          "an",
          "and",
          "associated",
          "class",
          "component",
          "conserved",
          "consisting",
          "containing",
          "[et]c:*\s*[a\d\.\s]+",
          "family",
          "function",
          "generic",
          "forms",
          "hypothetical",
          "involved",
          "like",
          "in",
          "is",
          "of",
          "or",
          "protein",
          "related",
          "subunit",
          "some",
          "system",
          "the",
          "to",
          "type",
          "with",
        )

        # This group will remove some, but not all, ID's.
        # It also removes some vaguely informative tokens.
        #
        # Note, this group tags more ID's than the default id-matching
        # code because we are less worried, in this context, about
        # overfiltering.
        self.idAndVagueFilterGroup = idFilterGroup(
          # yagI, czrB
          r"\b[cgmnyA-Z][a-z][a-z][A-Z]\b",
          # DUF, UPF and other gremlins
          r"\b(DUF|FIG|NWMN|SERP|UPF)[0-9]*\b",
          # these two should pick up most ID's; may generate FP's
          r"\b[A-Za-z0-9_\.\-]*[A-Z]_*[0-9][A-Za-z0-9_\.\-]*\b",
          r"\b[A-Za-z0-9_\.\-]*[0-9]_*[A-Z][A-Za-z0-9_\.\-]*\b",
          # The following words are "vague" - they only are informative if
          # a. they appear with at least one informative, non-ID token, or
          # b. they appear in both names to be compared.
          # If neither (a) nor (b) holds, the following tokens are ignored.
          r"\benzyme\b",
          r"\binner\b",
          r"\blipoprotein\b",
          r"\bmembrane\b",
          r"\bouter\b",
          r"\bpseudogene\b",
        )

        self.cleanupGroup = punctAndWhitespaceFilterGroup(r"[\.,:;\"\']")

    def __call__(self, name, refName=None):

        # first, get rid of tokens that are never informative
        filtered = self.cleanupGroup.run(self.filterGroup.run(name))

        uniqueIndices = None
        if refName is not None:
            # Only filter out id's and vague terms that are unique to
            # this name.  If both names have an id family or "vague"
            # term in common, keep it.
            qhits = self.idAndVagueFilterGroup.search(name)
            rhits = self.idAndVagueFilterGroup.search(refName)

            uniqueIndices = qhits - rhits

        # this string will be much more heavily modified than filtered is
        stripped = self.cleanupGroup.run(
          self.idAndVagueFilterGroup.run(filtered, indexMask=uniqueIndices))

        if len(stripped) <= 2:
            # After removing weasel words and id's, little is left.
            # This means the name is unreliable and is essentially
            # equivalent to any other unreliable name.
            return ""
        else:
            # Keep all id's and "vague" terms in the name if even
            # one non-weasel word is found.
            return filtered

# Returns a list of all permutations of a list, including itself.
# This implementation makes me wish we were running a more recent Python.
def all_perms(seq):
    sz = len(seq)
    if sz <= 1:
        return [ seq ]

    out = []
    pivot = [seq[0]]

    for sub_perm in all_perms(seq[1:]):
        for i in xrange(0, sz):
            out.append(sub_perm[:i] + pivot + sub_perm[i:])

    return out


# Returns the longest common substring between two strings.
# If there is more than one LCS, returns just one of them.
# This implementation was informed by Wikipedia and Gusfield.
def longestCommonSubstring(s1, s2):

    s2len = len(s2)
    maxlen = 0
    maxstr = ""

    for i in xrange(len(s1)):
        curr = [ 0 ] * s2len
        for j in xrange(s2len):
            if s1[i] == s2[j]:
                if i == 0 or j == 0:
                    score = 1
                else:
                    score = prev[j-1] + 1
                curr[j] = score
                if score > maxlen:
                    maxlen = score
                    maxstr = s1[(i-score)+1:i+1]
        prev = curr
    return maxstr


# Returns the minimum number of insertions, deletions, substitutions,
# and transpositions needed to transform one string into another.
#
# @author Michael Homer
# http://mwh.geek.nz/2009/04/26/python-damerau-levenshtein-distance/
def damerauLevenshteinHomerDistance(seq1, seq2):
    """
    Calculate the Damerau-Levenshtein distance between sequences.

    This distance is the number of additions, deletions, substitutions,
    and transpositions needed to transform the first sequence into the
    second. Although generally used with strings, any sequences of
    comparable objects will work.

    Transpositions are exchanges of *consecutive* characters; all other
    operations are self-explanatory.

    This implementation is O(N*M) time and O(M) space, for N and M the
    lengths of the two sequences.
    """
    # codesnippet:D0DE4716-B6E6-4161-9219-2903BF8F547F
    # Conceptually, this is based on a len(seq1) + 1 * len(seq2) + 1 matrix.
    # However, only the current and two previous rows are needed at once,
    # so we only store those.
    oneago = None
    thisrow = range(1, len(seq2) + 1) + [0]
    for x in xrange(len(seq1)):
        # Python lists wrap around for negative indices, so put the
        # leftmost column at the *end* of the list. This matches with
        # the zero-indexed strings and saves extra calculation.
        twoago, oneago, thisrow = oneago, thisrow, [0] * len(seq2) + [x + 1]
        for y in xrange(len(seq2)):
            delcost = oneago[y] + 1
            addcost = thisrow[y - 1] + 1
            subcost = oneago[y - 1] + (seq1[x] != seq2[y])
            thisrow[y] = min(delcost, addcost, subcost)
            # This block deals with transpositions
            if (x > 0 and y > 0 and seq1[x] == seq2[y-1]
              and seq1[x-1] == seq2[y] and seq1[x] != seq2[y]):
                thisrow[y] = min(thisrow[y], twoago[y-2] + 1)
    return thisrow[len(seq2) - 1]


# Returns a length-normalized edit distance between 0 and 1.  A score of 0
# means the strings are identical. A score of 1 means they are as different
# as can be.
#
# This score can be interpreted as the average number of per-character edits
# needed to transform the longer string into the shorter, even though that's
# not quite what it is.
#
# Strictly speaking, the returned value is the edit distance (or another
# length-dependent distance metric) divided by the longer string's length.
class NormalizedDistance:

    def __init__(self, distanceTool=damerauLevenshteinHomerDistance):
        self.distanceTool = distanceTool

    def __call__(self, s1, s2):
        num = self.distanceTool(s1, s2)
        den = max(len(s1), len(s2))
        try:
            dist = min(1.0, num / float(den))
        except:
            raise "couldn't compare '%s' and '%s'" % (s1, s2)
        return dist


# Returns a "tokenized" edit distance.
#
# A score of 0 means the strings are composed of identical tokens. The
# interpretation of non-zero scores depends on the normalization settings,
# but in all cases, higher scores are worse.
#
# When normalization is off, the scores returned by this class can be
# thought of as the number of per-character edits needed to transform
# one string into the other, when word rearrangements are free.
#
# Strictly speaking, the returned value is the minimal sum of (edit)
# distances of individual space-separated tokens PLUS the sum of any
# remaining tokens' (edit) distance to the empty string.
class TokenizedDistance:

    def __init__(self, distanceTool=damerauLevenshteinHomerDistance,
      normalizePerCharacter=1, normalizePerToken=0, stripUninformativeTokens=1):

        self.distanceTool = distanceTool
        self.normalizePerCharacter = normalizePerCharacter
        self.normalizePerToken = normalizePerToken
        self.stripUninformativeTokens = stripUninformativeTokens

        if self.stripUninformativeTokens:
            self.uninformativeTokenRemover = UninformativeTokenRemover()

        # split, then trim from token edges, whitespace and non-alphanumerics
        self.splitter = re.compile(r'[\s]+')
        self.trimmerF = re.compile(r'^[\s\(\)\[\];,-.\/&]+')
        self.trimmerR = re.compile( r'[\s\(\)\[\];,-.\/&]+$')
        self.stemmer = stemmer.PorterStemmer()

    # If substr is a substring of superstring, partitions superstring
    # into up to three strings: (before, match, after), where match ==
    # substr and before + match + after == superstr. If before or
    # after is empty, it is not returned, so this method will return a
    # list of two or three strings.  Returns None if superstr cannot
    # be split by substr, or if any portion of the split string would
    # contain fewer than 4 characters.
    #
    # If substr is too close to the length of superstr, splitting
    # isn't worth it.
    def splitStringBy(self, superstr, substr, minlen=4, maxratio=0.7):
        substrlen = len(substr)
        if substrlen < minlen:
            # the substring is too short to be interesting
            return None

        if substrlen > maxratio * len(superstr):
            # substr is too big relative to the superstring
            return None

        idx = superstr.find(substr)
        if idx == -1:
            # can't split the superstring
            return None

        ret = []
        ret.append(superstr[:idx])
        ret.append(superstr[idx:idx+substrlen])
        ret.append(superstr[idx+substrlen:])

        ret = [ r for r in ret if r != "" ]
        if len(ret[0]) < minlen or len(ret[-1]) < minlen:
            # the "remainder" on one side is too short
            return None

#		if log.debugEnabled:
#			log.debug("split %s by %s into %s" % (superstr, substr, ret))
        return ret

    def trimToStem(self, word):
        stem = word

        # PorterStemmer over-trims enzyme names (e.g., "synthase" ->
        # "syntha").  Rather than try to modify it, let's just skip it
        # for words ending in "e".  In addition, don't stem short
        # words - they may be gene symbols.
        if len(stem) > 4 and stem[-1] != "e":
            stem = self.stemmer.stem(stem, 0, len(stem)-1)
        return stem

    # Trims leading/trailing punctuation/whitespace from a collection
    # of tokens.  Returns an OrderedSet to preserve ordering while
    # enforcing uniqueness.
    def trimTokens(self, coll):
        ret = OrderedSet()
        for t in coll:
            trimmed = self.trimToStem(
              self.trimmerF.sub("", self.trimmerR.sub("", t)))
            if trimmed:
                ret.add(trimmed)
        return ret

    # Attempts to split elements of toks1 by possible substrings in toks2.
    # @see splitStringBy()
    #
    # @param toks1 an OrderedSet of tokens (informative words in a
    # protein name)
    # @param toks2 another OrderedSet of tokens
    def splitTokensBy(self, toks1, toks2):
        ret = OrderedSet()

        for t1 in toks1:
            if toks2.contains(t1):
                # an exact match already exists
                ret.add(t1)
                continue
            for t2 in toks2:
                splits = self.splitStringBy(t1, t2)
                if splits:
                    ret.addAll(splits)
                    break
            else:
                # fallthrough, t1 could not be split by anything in toks2
                ret.add(t1)

        return ret

    # If a collection has more than length items, the overhangers are
    # joined by spaces to reduce the item count. Returns a jython list.
    def shrinkCollToLen(self, coll, length):
        lst = [ l for l in coll ]
        if len(lst) > length:
            ret = lst[0:length-1]
            ret.append(" ".join(lst[length-1:]))
        else:
            ret = lst

        return ret

    def __call__(self, s1, s2):
        if self.stripUninformativeTokens:
            s1 = self.uninformativeTokenRemover(s1.lower(), s2.lower())
            s2 = self.uninformativeTokenRemover(s2.lower(), s1.lower())

        # Split up the strings into lists of unique tokens.
        # We ignore capitalization, but maybe we shouldn't.
        set_toks1 = self.trimTokens(self.splitter.split(s1.lower()))
        set_toks2 = self.trimTokens(self.splitter.split(s2.lower()))

        # Break up the tokens of one word by the tokens of the other
        # to provide for more exact matches. When these commands complete,
        # "polyvinyl chloride" and "poly vinylchloride" will each be
        # split into [ "poly", "vinyl", "chloride" ].
        set_toks1 = self.trimTokens(self.splitTokensBy(set_toks1, set_toks2))
        set_toks2 = self.trimTokens(self.splitTokensBy(set_toks2, set_toks1))
        set_toks1 = self.trimTokens(self.splitTokensBy(set_toks1, set_toks2))

        # Find the tokens common to both and build two sets of unique tokens.
        common_toks = set_toks1.clone()
        common_toks.retainAll(set_toks2)

        unique_toks1 = OrderedSet(set_toks1)
        unique_toks1.removeAll(common_toks)
        unique_toks2 = OrderedSet(set_toks2)
        unique_toks2.removeAll(common_toks)

        toks1 = self.shrinkCollToLen(unique_toks1, 9)
        toks2 = self.shrinkCollToLen(unique_toks2, 9)

#		if log.debugEnabled:
#			log.debug("common tokens: %s" % common_toks)
#			log.debug("unique s1 tokens: %s" % toks1)
#			log.debug("unique s2 tokens: %s" % toks2)

        # number of tokens in each group
        commonTokenCnt = len(common_toks)
        toks1cnt = len(toks1)
        toks2cnt = len(toks2)
        minTokenCnt = min(toks1cnt, toks2cnt)
        maxTokenCnt = max(toks1cnt, toks2cnt)

        # mumber of chars in each group
        commonTokenLen = reduce(operator.add, [ len(t) for t in common_toks ], 0)
        tokenLens = [
          reduce(operator.add, [ len(t1) for t1 in toks1 ], 0),
          reduce(operator.add, [ len(t2) for t2 in toks2 ], 0) ]
        tokenLens.sort()
        minTokenLen, maxTokenLen = tokenLens

        # Special case 1. Names with no differing tokens are identical.
        if maxTokenCnt == 0:
            return 0.0
        # Special case 2. Names consisting solely of weasel words
        # are infinitely distant from those with non-weasel words.
        if commonTokenCnt == 0 and maxTokenCnt > 0 and minTokenCnt == 0:
            return 1.0

        # Now, build two N * N matrices to hold pairwise distance scores.
        # We compute two sets of scores. The match_grid holds the number
        # of characters in a token when two tokens toks1[i],toks2[j]
        # are identical. If they are not identical, the value is the
        # length of the longest common substring. The score_grid holds
        # the distanceTool's calculated distance for all pairs of tokens.
        # If the names have different numbers of tokens we pad out the
        # shorter one with tokens made of spaces and apply some special
        # handling later on.
        match_grid = []
        score_grid = []

        for i in xrange(0, maxTokenCnt):

            match_grid.append([None] * maxTokenCnt)
            score_grid.append([None] * maxTokenCnt)

            for j in xrange(0, maxTokenCnt):
                try:
                    t1 = toks1[i]
                except IndexError:
                    t1 = ""
                try:
                    t2 = toks2[j]
                except IndexError:
                    t2 = ""

                score_grid[i][j] = self.distanceTool(t1, t2)
                match_grid[i][j] = len(longestCommonSubstring(t1, t2))

        # Now find the lowest mutually-exclusive sum of those scores.
        # The number of permutations is factorial which is quadratic.
        # Then we do O(n) additions per permutation, so there's room
        # for improvement here since the whole thing is cubic. But I
        # can't see an easy way out, as the lowest total distance may
        # be built from the sum of (very) suboptimal token-token
        # comparisons.
        bestDist = sys.maxint
        bestTokenLen = 0

        # First, precompute scores for perfect token-token matches.
        # We will always pair exact matches with each other so we
        # don't need to include the common tokens in the naming grid.
        baseDist = 0
        basePerf = 0
        for t in common_toks:
            baseDist += self.distanceTool(t, t)
            basePerf += len(t)

#		if log.debugEnabled:
#			log.debug("common-token base scores: %s %s" % (baseDist, basePerf))

        for perm in all_perms(range(0, maxTokenCnt)):
            dist = baseDist
            perf = basePerf
            scoredTokenLen = 0
            mismatchScores = []
            mismatchTokens = []

            for i in xrange(0, maxTokenCnt):
                j = perm[i]
                if i < toks1cnt and j < toks2cnt:
                    dist += score_grid[i][j]
                    perf += match_grid[i][j]
                    scoredTokenLen += max(len(toks1[i]), len(toks2[j]))
                else:
                    assert match_grid[i][j] == 0
                    mismatchScores.append(score_grid[i][j])
                    if i < toks1cnt:
                        mismatchTokens.append(toks1[i])
                    if j < toks2cnt:
                        mismatchTokens.append(toks2[j])

            # When there is a mismatched number of tokens, only consider
            # the most severe mismatch and ignore the others. Since a
            # mismatch gets an awful score of 1, multiple such mismatches
            # can over-penalize a name.
            if toks1cnt != toks2cnt:
                penalty = max(mismatchScores)
                penaltyTokenCnt = 1
                penaltyTokenLen = max([ len(t) for t in mismatchTokens ])
            else:
                penalty = 0
                penaltyTokenCnt = 0
                penaltyTokenLen = 0

            # what was the total length of the tokens we actually compared?
            tokenLen = scoredTokenLen + penaltyTokenLen + commonTokenLen

            # Reduce the computed distance in cases where substrings
            # match exactly. A heuristic that seems to work well is
            # len(substring matches) / len(compared tokens).
            adj = 1 - (perf / float(tokenLen))
            adj_dist = adj * (dist + penalty)

            if adj_dist < bestDist:
                bestDist = adj_dist
                bestTokenLen = tokenLen

        if self.normalizePerCharacter:
            dist = min(1.0, bestDist / (float(bestTokenLen)))
        elif self.normalizePerToken:
            dist = min(1.0, bestDist / \
            (float(minTokenCnt + commonTokenCnt + penaltyTokenCnt)))
        else:
            dist = min(1.0, bestDist)

        return dist


# This class will always expose the best-performing distance tool.
class DistanceTool:
    def __init__(self):
        self.dister = TokenizedDistance(NormalizedDistance(), 0, 1)
        # describing the range of results
        self.min = 0.0
        self.max = 1.0

    def distance(self, s1, s2):
        return self.dister(s1, s2)

    def __call__(self, s1, s2):
        return self.dister(s1, s2)
