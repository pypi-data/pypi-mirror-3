#!/bin/env python

#
# If you are a python fan and are wondering why BioName python code
# seems stuck in 2001 idioms, it is because we are using jython, which
# -- while a wonderful development experience -- is currently holding
# tight at python language version 2.1 (released in 2001). We are very
# much looking forward to the upcoming jython 2.5 release, so that we
# can jump forward to 2006.
#

from __future__ import nested_scopes

import codecs
import re

import filters
import util

from filters import FilterByFunction
from filters import FilterGroup
from filters import FilterRemove
from filters import FilterReplace

#
# In the large beginning section of this file, we have some functions and
# regular expressions. They're outside of the objects/functions because
# we should only compile them once (on import) and then use them as
# many times as we like.
#
# Later on, there are objects and interfaces to make these interfaces
# palatable.
#

NOTAUTOGEN = "not automatically assigned"
RETAINWEAK = "retains weak names"
REORDERFAMILY = "reorder family predicates"
REMOVETRAILING = "remove trailing clauses"

# the following regular expressions are used in the name sorter
predictedProteinRe = re.compile(
  r"^\s*predicted\s+protein\s*$", re.I)
hypotheticalProteinRe = re.compile(
  r"^\s*hypothetical\s+protein(\s*|,.*)$", re.I)
weakPredictionRe = re.compile(
  r"^\s*hypothetical\s+protein\s+similar\s+to\s*(.*)$", re.I)

# the name we give when we can't find a name
DEFAULTNAME = "hypothetical protein"

ecRe = re.compile(r"\(?EC +([0-9\.]+)\)?")
def cleanupEC(name):
    """
    Eliminate EC names for now. The goal is to be smarter about this in the future.
    """
    if ecRe.search(name) is not None:
        name = ecRe.sub("", name)
    return name


sevenBitRe = re.compile(r"[^\w\-_.,;:'+-/\\()\[\]]")
def asciiify(name):
    """
    Make sure that the name is exportable 7-bit ascii.
    """
    try:
        name = codecs.ascii_encode(name)[0]
    except UnicodeError:
        # force it into compliance by replacing weird chars with spaces
        name = sevenBitRe.sub(" ", name)
        name = codecs.ascii_encode(name)[0]
    return name


secondaryParenRe = re.compile(r"(.*\).*)\([^)]*\(.*")
def cleanupNestedSecondaryParentheses(name):
    """
    If a name has nested parentheses after regular parentheses, which
    are separated from the rest of the name by whitespace, strike them.

    23S rRNA (U5-)-transferase rumA (23S rRNA(M-5-)-transferase) ...
                                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    """
    name = secondaryParenRe.sub(lambda x: x.group(1), name)

    #
    # Find the first unmatched close parenthesis, bracket and/or brace,
    # then trim the name so that it no longer contains it.
    #
    for puncts in [ ("(", ")"), ("[", "]"), ("{", "}") ]:
        numOpen = name.count(puncts[0])
        numClosed = name.count(puncts[1])
        if numClosed > numOpen:
            i = 0
            pos = 0
            while i < numOpen + 1:
                pos = name.find(puncts[1], pos) + 1
                i += 1
            name = name[:pos-1]

    return name


hspRe = re.compile(r"heat\s+shock|\bhsp[\b0-9]", re.I)
hspWeightRe = re.compile(r"(?:([\d\.]+) kDa)|(?:\bhsp(\d+))", re.I)
def cleanupHeatShockNames(name):
    """
    If a name indicates a heat-shock protein, isolate and standardize
    the relevant part of it.
    """
    if hspRe.search(name):
        match = hspWeightRe.search(name)
        if match:
            weight = match.group(1) or match.group(2)
            corename = "hsp" + weight
            return "%s-like protein" % corename

    return name


endsDomainRe = re.compile(r"\bdomain\s*$", re.I)
hasDoubleContainsRe = re.compile(r"\bcontaining\s+([A-Z0-9]+)\s+domain-containing\s*(protein)?")
containsProteinRe = re.compile(r"\bprotein\b", re.I)
def cleanupDomainEnd(name):
    """
    If a name ends in "domain" but does not have protein anywhere else
    in it, switch to "domain-containing protein".
    If a name has the word "containing" twice, try to clean it up.
    """
    if hasDoubleContainsRe.search(name):
        name = hasDoubleContainsRe.sub(lambda x: "containing %s domain" % x.group(1), name)

    # If ends in domain and doesn't contain protein...
    elif endsDomainRe.search(name) and not containsProteinRe.search(name):
        name = endsDomainRe.sub("domain-containing protein", name)

    return name


proteinFriendlyWordList = [
    "phosphatase",
    "kinase",
    "transport",
    "proteinase",
    "export",
    "disulfide",
    "isomerase",
    "methyltransferase",
]
startsWithProteinRe = re.compile(r"^\s*protein\s+")
hasValidProteinPredicateRe = re.compile(r"|".join(proteinFriendlyWordList))
def cleanupStartsWithProtein(name):
    """
    If a name begins with "protein", the remainder of the name
    determines whether or not to remove that word.
    (This is a separate function because we can't have
    variable-width lookaheads)
    """
    if startsWithProteinRe.match(name) and not hasValidProteinPredicateRe.search(name):
        name = startsWithProteinRe.sub("", name)
    return name


repeatRe = re.compile(r"(\w{3,})\s+\1")
def cleanupRepeats(name):
    """
    Clean up all sequential repeated words except for those
    in a given list.
    """
    acceptableRepeats = ["kinase"]

    mRe = repeatRe.search(name)
    if not mRe:
        return name
    word = mRe.group(1)
    if word:
        for okWord in acceptableRepeats:
            if word == okWord:
                return name
        name = repeatRe.sub(lambda x: x.group(1), name)
    return name


multiWhitespaceRe = re.compile(r"\s+")
def cleanupWhitespace(name):
    "Like strip(), but moreso."
    name = name.strip()
    if multiWhitespaceRe.search(name):
        name = multiWhitespaceRe.sub(" ", name)
    return name


# Underscores typify ids, except in certain baffling cases.
# Negative lookbehinds can't accept variable width characters, so we just
# do it a little more deliberately. Probably reads better, too.
underscoreFriendlyWordList = [
    "PE_PGRS",
    "VRR",
]
underscoreIdsRe = re.compile(r"\b([A-Z0-9]{2,5}_[A-Z0-9]{3,5})\b")
underscoreExceptionsRe = re.compile(r"|".join(underscoreFriendlyWordList))
def removeUnderscoreIds(name):
    mRe = underscoreIdsRe.search(name)
    if not mRe or not mRe.groups():
        return name
    potentialIdMatch = mRe.group(1)
    if underscoreExceptionsRe.match(potentialIdMatch):
        return name
    else:
        return re.sub(potentialIdMatch, "", name)


# This is not used in BioName.
keggExtractRe = re.compile(r"(.*?)\s;\s(.*)")
def extractKEGG(name):
    """
    If a name is a unified KEGG field in the form:

    definition ; orthology

    ...then return just the orthology.
    Otherwise, return the whole name.
    """
    m1 = keggExtractRe.search(name)
    if m1:
        return m1.group(2)
    else:
        return name



###
# BioName is a collection of filters, originally intended to obtain decent
# information from blast/NR.
#
# The overarching philosophy is: the names coming in aren't high
# quality. Most of the rules are designed to find ways to throw the
# entire name away. The rest are reformatted in an attempt to create
# a standard format.
#
class BioName:
    """
    A utility class that cleans up gene names.

    @param saveWeakNames binary: attempt to recreating hmp-style retention of weak names
    @param removeTrailingClauses binary: kill predicates hidden behind punctuation
    @param reorderFamily binary: make "X, family Y" into "Y family X"
    @param hmp binary: if 1, override the other variables to "the hmp experience"
    """
    def __init__(self, minNameLength=3, maxNameLength=100,
        saveWeakNames=0, removeTrailingClauses=0, reorderFamily=1, hmp=0):

        self.minNameLength = minNameLength
        self.maxNameLength = maxNameLength
        self.saveWeakNames = saveWeakNames
        self.removeTrailingClauses = removeTrailingClauses
        self.reorderFamily = reorderFamily

        self.hmp = hmp
        if self.hmp:
            self.removeTrailingClauses = 0
            self.reorderFamily = 0
            self.saveWeakNames = 1

        self._compileFilters()
        self._createFilterGroup()

    def _createFilterGroup(self):

        fgroup = FilterGroup(showPattern=1, outputType=filters.TEXT)

        fgroup.addAll(self.killWholeNameList)

        fgroup.add(FilterByFunction(cleanupWhitespace, "cleanup whitespace"))
        fgroup.add(FilterByFunction(asciiify, "cleanup non-ascii characters"))
        fgroup.add(FilterByFunction(cleanupEC, "cleanup EC numbers"))
        fgroup.addAll(self.initialDistillationList)
        fgroup.addAll(self.typoList)

        fgroup.add(FilterByFunction(cleanupHeatShockNames, "cleanup heat shock names"))
        fgroup.addAll(self.clauseRemovalList)
        fgroup.addAll(self.allClauseRemovalList)
        fgroup.addAll(self.weakNameSaveList)
        fgroup.addAll(self.idDeletionList)
        fgroup.addAll(self.clauseReplaceList)
        fgroup.addAll(self.organismNameList)
        fgroup.addAll(self.punctuationList)
        fgroup.add(FilterByFunction(cleanupNestedSecondaryParentheses, "remove nested secondary parens"))
        fgroup.addAll(self.automaticPunctuationList)
        fgroup.add(FilterByFunction(cleanupWhitespace, "cleanup whitespace"))
        fgroup.addAll(self.cleanupList)
        fgroup.add(FilterByFunction(cleanupRepeats, "cleanup repeats within names"))
        # this rule is too strict when applied to swiss-prot - reactivate for NR
#		fgroup.add(FilterByFunction(cleanupStartsWithProtein, "cleanup names that begin with protein"))
        fgroup.add(FilterByFunction(cleanupDomainEnd, "cleanup domain at end of name"))
        fgroup.add(FilterByFunction(cleanupWhitespace, "cleanup whitespace"))
        fgroup.addAll(self.wholeNameModificationList)
        fgroup.addAll(self.capitalizeList)
        fgroup.addAll(self.punctuationList)		# clean up punctuation a second time

        # not external because the lengths are variable and coding around it
        # would be globally awkward, rather than locally awkward
        fgroup.add(FilterByFunction(
            lambda x: (self.minNameLength <= len(x) <= self.maxNameLength) and x or None,
            "names that are too short or too long",
            skipif=[NOTAUTOGEN]
        ))

        self.fgroup = fgroup


    #
    # Filtering rules for filter() and cleanup().
    # The order of processing is determined by _createFilterGroup().
    #
    def _compileFilters(self):

        #
        # These patterns trigger whole name deletions via a simple
        # substring match, typically from a list of bad substrings.
        #
        self.killWholeNameList = []
        killList = []

        #
        # Low confidence words indicate that whoever named the protein we're using for
        # evidence was not sure of the name. Since we're not sure the protein
        # we're annotating is the same as the evidence, we should be extra
        # careful. Names with any of the following low confidence words are ignored.
        #
        lowConfidenceList = [
            (r"dubious", None),
            (r"DUF", None),
            (r"doubtful", None),
            (r"fragment", None),
            (r"homolog[ue]*?", "homolog"),
            (r"key", None),
#			(r"like", None),
            (r"may", None),
            (r"novel", None),
            (r"of", None),
            (r"open\s+reading\s+frame", "open reading frame"),
            (r"partial", None),
            (r"po[s]+ibl[ey]", "possibly"),
            (r"predicted", None),
            (r"proba\s*ble", "probable"),
            (r"product", None),
            (r"putative", None),
            (r"putavie", None),
            (r"related", None),
            (r"similar", None),
            (r"similarity", None),
            (r"synthetic", None),
            (r"UPF", None),
            (r"un[cs]haracteri[zs]ed", "uncharacterized"),
            (r"unknow[n]?", "unknown"),
            (r"unnamed", None),
        ]
        # Low confidence words must appear alone: enclosing them in \b matches "may"
        # but not "mayflower", "DUF protein" but not "DUF9001 protein".
        for (pat, desc) in lowConfidenceList:
            killList.append(
                FilterRemove(
                    re.compile(r".*\b%s\b.*" % pat, re.I),
                    desc = "killed by inclusion of [%s]" % (desc or pat),
                    skipif=[RETAINWEAK]
                )
            )
        # the following low confidence words are ok if manually assigned
        # for example, "conserved hypothetical protein" is valid
        # (this is going to need rewriting if one more tiny layer of complexity is added)
        lowConfidenceNotAutogen = [
            (r"conserved", None),
            (r"hypothetical", None),
        ]
        for (pat, desc) in lowConfidenceNotAutogen:
            killList.append(
                FilterRemove(
                    re.compile(r".*\b%s\b.*" % pat, re.I),
                    desc = "killed by inclusion of [%s]" % (desc or pat),
                    skipif=[RETAINWEAK, NOTAUTOGEN]
                )
            )

        #
        # use these names a second time for removeLowConfidence()
        #
        self.lowConfidenceRemoval = []
        for (pat, desc) in lowConfidenceList:
            self.lowConfidenceRemoval.append(
                FilterRemove(
                    re.compile(r"\b%s\b" % pat, re.I),
                    desc = "removed low confidence word [%s]" % (desc or pat),
                )
            )


        #
        # The following additions to the drop list indicate specific names that
        # are not trustworthy.
        #
        dropList = [
            # got 400 of these on CNA1
            (r"expressed\s+protein", None),
            # not valid reference
            (r"ORF\d*?", None),
            (r"([A-Z])\s+(CHAIN|Chain|chain)\s+\1", "A Chain A names are always wrong"),
            (r"^(CHAIN|Chain|chain)$", "names that are simply the word Chain are suspect"),
            (r"ink\ 76", None),
            (r"^(e_){0,1}gw1|^est_|^fge1_", "spurious aspergilli"),
            (r"\.$", "names ending in period are bad"),
            (r"\\", "names containing a backslash are suspect"),
            #(r"\)\)|\(\(", "double parens are usually in bad names"),
            (r"RIKEN", "RIKEN is a tag name, toss whole name"),
        ]
        for pat, desc in dropList:
            killList.append(FilterRemove(re.compile(r".*\b%s\b.*" % pat, re.I), desc))

        #
        # The presence of a software names invalidates a name
        #
        softwareNames = [
            (r"glimmer(\s*3)?", "glimmer"),
            (r"gene(_|\s+)?id", "geneid"),
            (r"genemark(hmm|hmmes)?", "genemark"),
            (r"conrad", "conrad"),
            (r"blast", "blast"),
            (r"augustus", "augustus"),
            (r"fgenesh(\++)?", "fgenesh"),
            (r"hmmer", "hmmer"),
            (r"metagene", "metagene"),
            (r"snap", "snap"),
            (r"zcurve[_]?[bv]?", "zcurve"),
        ]
        for sName, desc in softwareNames:
            killList.append(FilterRemove(re.compile(r".*\b%s\b.*" % sName, re.I), "software title %s" % desc))

        self.killWholeNameList = killList

        #
        # Capitalization rules.
        #
        self.capitalizeList = []
        capList = []

        capList.append(FilterReplace(
            re.compile(r"(?:(?<=similar to )|^)([A-Z])(?=[a-z][a-z]+([ /,-]|$))"),
            lambda x: x.group(0).lower(),
            "protein names should not start with a capital letter"
        ))
        capList.append(FilterReplace(
            re.compile(r".*[A-Z]{6,}.*"),
            lambda x: x.group(0).lower(),
            "6+ consecutive capital letters: make the whole string lowercase"
        ))
        capList.append(FilterReplace(
            re.compile(r"\bactin\b", re.I),
            lambda x: x.group(0).lower(),
            "replace ACTIN with actin, it's short and doesn't get caught"
        ))
        capList.append(FilterReplace(
            re.compile(r"\brifin\b", re.I),
            lambda x: x.group(0).lower(),
            "replace RIFIN with rifin, it's short and doesn't get caught"
        ))
        capList.append(FilterReplace(
            re.compile(r"\b(rieske|mur|cullin)\b", re.I),
            lambda x: x.group(0).title(),
            "recapitalize people / place names"
        ))

        # decapitalize other names - any surviving low confidence words should be
        # lower case, including "conserved hypothetical" and "lowConfidence protein"
        for ww, desc in lowConfidenceList:
            capList.append(FilterReplace(
                re.compile(r"\b%s\b" % ww, re.I),
                lambda x: x.group(0).lower(),
                "make low confidence words lowercase"
            ))
        for ww in ["conserved", "protein"]:
            capList.append(FilterReplace(
                    re.compile(r"\b%s\b" % ww, re.I),
                    lambda x: x.group(0).lower(),
                    "lowercase %s" % ww
            ))

        capList.append(FilterReplace(
            re.compile(r"\bFamily\b\s*$"),
            "family",
            "lowercase family/superfamily when last word"
        ))
        capList.append(FilterReplace(
            re.compile(r"\bSuperfamily\b\s*$"),
            "superfamily",
            "lowercase family/superfamily when last word"
        ))
        capList.append(FilterReplace(
            re.compile(r"\b[ivx]+\b", re.I),
            lambda x: x.group(0).upper(),
            "uppercase roman numerals"
        ))
        capList.append(FilterReplace(
            re.compile(r"[dr]na\b", re.I),
            lambda x: x.group(0).upper(),
            "uppercase DNA/RNA"
        ))
        capList.append(FilterReplace(
            re.compile(r"([ag]tp)(\b|ase)", re.I),
            lambda x: x.group(1).upper() + x.group(2).lower(),
            "uppercase ATP/GTP"
        ))
        capList.append(FilterReplace(
            re.compile(r"nad\w*h\b", re.I),
            lambda x: x.group(0).upper(),
            "uppercase NADPH/NADH"
        ))
        capList.append(FilterReplace(
            re.compile(r"\bmce-family\b", re.I),
            "MCE-family",
            "repair MCE-family"
        ))
        capList.append(FilterReplace(
            re.compile(r"\bo-(\w+)\b", re.I),
            lambda x: "O-" + x.group(1).lower(),
            "lowercase O-* (example: o-methyltransferase)"
        ))
        capList.append(FilterReplace(
            re.compile(r"\b(p{1,2}e) family protein", re.I),
            lambda x: x.group(1).upper() + " family protein",
            "repair PE family protein or PPE family protein"
        ))
        # the following names are erroneously capitalized in some hmmer entries
        hmmerToLower = (
            "Methylase",
            "Corrin",
            "Porphyrin",
            "Active",
        )
        capList.extend(
            [FilterReplace(
                re.compile(r"\b%s\b" % htl, re.I),
                lambda x: x.group(0).lower(),
                "%s erroneously capitalized in some hmmer entries" % htl)
            for htl in hmmerToLower]
        )
        capList.append(FilterReplace(
            re.compile(r"\bHolliday\b", re.I),
            lambda x: x.group(0).title(),
            "fix some errors from earlier filter"
        ))
        capList.append(FilterReplace(
            re.compile(r"\bpts\b", re.I),
            lambda x: x.group(0).upper(),
            "uppercase PTS"
        ))
        capList.append(FilterReplace(
            re.compile(r"\bclp|ppx|ras\b", re.I),
            lambda x: x.group(0).title(),
            "title-case Clp, Ppx and Ras"
        ))
        capList.append(FilterReplace(
            re.compile(r"\bei*cba|TFI*B\b", re.I),
            lambda x: x.group(0).upper(),
            "uppercase EI*CBA and TFI*B"
        ))
        capList.append(FilterReplace(
            re.compile(r"\bmpt\d{2}\b", re.I),
            lambda x: x.group(0).upper(),
            "uppercase MPT##"
        ))
        capList.append(FilterReplace(
            re.compile(r"\bcrispr\b", re.I),
            lambda x: x.group(0).upper(),
            "uppercase CRISPR"
        ))
        capList.append(FilterReplace(
            re.compile(r"\babc\b", re.I),
            lambda x: x.group(0).upper(),
            "uppercase ABC"
        ))
        # title-cap all amino acid names
        proteinNames = ["ala", "arg", "asn", "asp", "cys", "gln", "glu", "gly", "his",
            "ile", "leu", "lys", "met", "phe", "pro", "ser", "thr", "trp", "tyr", "val"]
        for pname in proteinNames:
            capList.append(FilterReplace(
                re.compile(r"\b%s\b" % pname, re.I),
                lambda x: x.group(0).lower().capitalize(),
                "title-capitalize amino acid names (%s)" % pname.capitalize()
            ))

        self.capitalizeList = capList

        #
        # Initial distillation/extraction rules.
        # (Sometimes, people upload their excel spreadsheet to NCBI. Before major
        # improvement can occur, we have to extract the relevant part of the name.)
        # This list has to be before clause/punctuation cleanup, because such cleanup
        # would likely leave the wrong part of the string as the main name
        #
        self.initialDistillationList = []
        self.initialDistillationList.append(FilterReplace(
            re.compile(r".*?[Ff]ull\=(.*?)(?:;|$).*"),
            lambda x: x.group(1),
            "extract useful info from database dumps including Full="
        ))

        #
        # These rules fix typographical errors and are applied to all names.
        #
        self.typoList = []
        # simple replacements
        typos = [
            # (why is transporter so frequently misspelled?)
            (r"trans[p]?o[_r]?te[r]?", "transporter"),
            (r"chmomosome", "chromosome"),
            (r"put[aitv]+e", "putative"),
            (r"protei\b", "protein"),
            (r"prot[ei]+n\b", "protein"),
            (r"ised\b", "ized"), # true especially for jazzercise
            (r"bindingprotein", "binding protein"),
            (r"[h]?hy[p]?ot[h]?etical", "hypothetical"),
            (r"hypotehtical", "hypothetical"),
            (r"signalling", "signaling"),
            (r"oligoeptide", "oligopeptide"),
            (r"dephosph\b", "dephospho"),
            (r"glycosy\b", "glycosyl"),
            (r"symport\b", "symporter"),
            (r"asparate", "aspartate"),
            (r"\bKd[a]?\b", "kDa"),
            (r"\batpas\b", "ATPase"),
            # prefer American English spelling
            (r"\bhaemolysin\b", "hemolysin"),
            (r"\bhaemagglutinin\b", "hemagglutinin"),
            (r"aluminium", "aluminum"),
            (r"utilis", "utiliz"),
            (r"phosphopantethiene", "phosphopantetheine"),
            (r"resistence", "resistence"),
        ]
        self.typoList.extend(
            [FilterReplace(
                re.compile(pat, re.I),
                repl,
                "typo: %s" % repl)
             for pat, repl in typos]
        )

        #
        # These clauses are not informative when automatically assigned.
        # However, manual annotators can assign them from a file or annotation.
        #
        self.clauseRemovalList = []
        removals = []
        removals.append(FilterRemove(
            re.compile(r"\b[Bb]ifunctional\s+protein\b"),
            "trim: bi functional protein",
            skipif=[NOTAUTOGEN]
        ))
        removals.append(FilterRemove(
            re.compile(r"low\s+molecular\s+weight"),
            "trim: low molecular weight",
            skipif=[NOTAUTOGEN]
        ))
        removals.append(FilterRemove(
            re.compile(r"low[-|\s]affinity"),
            "trim: low affinity",
            skipif=[NOTAUTOGEN]
        ))
        removals.append(FilterRemove(
            re.compile(r"\bDNA\s+gyrase\b(?!.*subunit.*)", re.I),
            "trim: DNA gyrase when not followed by subunit",
            skipif=[NOTAUTOGEN]
        ))
        removals.append(FilterRemove(
            re.compile(r"\b[\-]?truncated\b"),
            "trim: truncated",
            skipif=[NOTAUTOGEN]
        ))
        removals.append(FilterRemove(
            re.compile(r"\bsubunits\b", re.I),
            "trim: subunits",
            skipif=[NOTAUTOGEN]
        ))
        removals.append(FilterRemove(
            re.compile(r"involved\s+in\s+.*"),
            "trim everything following: involved in",
            skipif=[NOTAUTOGEN]
        ))
        removals.append(FilterRemove(
            re.compile(r"[\d\-\.]+\s+kDa\s+(?!subunit)"),
            "delete 70 kDa but allow 70 kDa subunit",
            skipif=[NOTAUTOGEN]
        ))
        removals.append(FilterRemove(
            re.compile(r"\b(mitochondrial\s*)?precursor\b"),
            'trim: "precursor" and "mitochondrial precursor"',
            skipif=[NOTAUTOGEN]
        ))
        removals.append(FilterRemove(
            re.compile(r"\-associated\s+region\b"),
            "trim: -associated region",
            skipif=[NOTAUTOGEN]
        ))
        removals.append(FilterRemove(
            re.compile(r"\:subunit=.*"),
            "trim everything following: :subunit=",
            skipif=[NOTAUTOGEN]
        ))
        removals.append(FilterRemove(
            re.compile(r"\band\s+inactivated\s+derivatives\b"),
            "trim: and inactivated derivatives",
            skipif=[NOTAUTOGEN]
        ))
        removals.append(FilterRemove(
            re.compile(r"\band other.*"),
            "trim everything following: and other",
            skipif=[NOTAUTOGEN]
        ))
        removals.append(FilterRemove(
            re.compile(r"\bassociated with.*"),
            "trim everything following: associated with",
            skipif=[NOTAUTOGEN]
        ))
        removals.append(FilterRemove(
            re.compile(r"\band\s+\d\s+protein"),
            "trim: and # protein",
            skipif=[NOTAUTOGEN]
        ))
        removals.append(FilterRemove(
            re.compile(r"\bfrom\b"),
            "trim: from",
            skipif=[NOTAUTOGEN]
        ))
        removals.append(FilterRemove(
            re.compile(r"\(?photosystem\s+q\(a\)\s+protein\)?"),
            "trim: photosystem q(a) protein",
            skipif=[NOTAUTOGEN]
        ))
        # this is here because the low confidence filters are not active
        # all the time
        removals.append(FilterRemove(
            re.compile(r"(5\'|3\'|5|3)-partial"),
            "trim all partials referring to start and stop codons",
            skipif=[NOTAUTOGEN]
        ))
        removals.append(FilterRemove(
            re.compile(r"\s*[nNcC][ -]terminus"),
            "trim all occurances of terminus when preceded by n or c",
            skipif=[NOTAUTOGEN]
        ))
        removals.append(FilterRemove(
            re.compile(r"(\s+N)?\s+repeat$"),
            "trim all repeat or N repeat",
            skipif=[NOTAUTOGEN]
        ))
        #removals.append(FilterRemove(
        #	re.compile(r"(?:\,)?\s+?paralogous\s+family"),
        #	"trim paralogous families",
        #	skipif=[NOTAUTOGEN]
        #))
        removals.append(FilterRemove(
            re.compile(r"\bvery\b", re.I),
            "trim: very",
            skipif=[NOTAUTOGEN]
        ))
        removals.append(FilterRemove(
            re.compile(r"\bvalidate[d]?\b", re.I),
            "trim: validate",
        ))
        removals.append(FilterRemove(
            re.compile(r"\bgene\b", re.I),
            "trim: gene",
        ))
        removals.append(FilterRemove(
            re.compile(r"\btruncat[ed]*\b", re.I),
            "trim: truncate",
        ))
        self.clauseRemovalList.extend(removals)


        #
        # These clauses are never informative, no matter how assigned.
        #
        self.allClauseRemovalList = []
        self.allClauseRemovalList.append(FilterRemove(
            re.compile(r"[([]predicted[\])]", re.I),
            "trim predicted and immediate surrounding parens"
        ))
        self.allClauseRemovalList.append(FilterRemove(
            re.compile(r"[([]imported[\])]", re.I),
            "trim imported and immediate surrounding parens"
        ))


        #
        # Clause replacement - try to enforce consistent terminology.
        # try to keep these clauses universally true, not just at beginning
        # or end of string.
        #
        self.clauseReplaceList = []
        replacers = []
        replacers.append(FilterReplace(
            re.compile(r"SAM\s+domain\s+[(]Sterile\s+alpha\smotif[)]"),
            "SAM (sterile alpha motif) domain",
            "special case from hmmer"
        ))
        replacers.append(FilterReplace(
            re.compile(r"\bsubunit\s+family\b"),
            "subunit",
            "subunit family -> subunit"
        ))
        replacers.append(FilterReplace(
            re.compile(r"^(.*?):\1", re.I),
            lambda x: x.group(1),
            "keep only half of duplicated strings"
        ))
        replacers.append(FilterReplace(
            re.compile(r"protein\s+product"),
            "protein",
            "protein product -> product"
        ))
        replacers.append(FilterReplace(
            re.compile(r"\bdomain\s+protein\b"),
            "domain-containing protein",
            "standardize to domain-containing protein"
        ))
        replacers.append(FilterReplace(
            re.compile(r"\bdomain\s+containing\s+protein\b"),
            "domain-containing protein",
            "standardize to domain-containing protein"
        ))
        replacers.append(FilterReplace(
            re.compile(r"\bmotif\b(?!\))"),
            "domain-containing protein",
            "motif -> domain-containing protein (unless motif in parens)"
        ))
        replacers.append(FilterReplace(
            re.compile(r"\btransposase\s+mutator\s+type\b"),
            "transposase",
            "transposase mutator type to transposase"
        ))
        replacers.append(FilterReplace(
            re.compile(r"\bdiacylglycerol\s+kinase\s+catalytic\s+region\b"),
            "diacylglycerol kinase",
            "diacylglycerol kinase catalytic region to diacylglycerol kinase"
        ))
        # remove "family protein" or "protein" following any "-ase" word
        # shortest valid one I can think of is "kinase"
        replacers.append(FilterReplace(
            re.compile(r"\b(\w{3,}ase)(\s+family)?\s+protein"),
            lambda x: x.group(1),
            "remove protein or family protein following any -ase"
        ))
        # the following rules were too picky for swiss-prot
#		replacers.append(FilterReplace(
#			re.compile(r"\b(.*?ase)\s+(.)\s+chain\b"),
#			lambda x: "%s subunit %s" % (x.group(1), x.group(2)),
#			"Xase Y chain -> Xase subunit Y"
#		))
#		replacers.append(FilterReplace(
#			re.compile(r"\b(.*?ase)\s+(.*?[^y])\s+chain\b"),
#			lambda x: "%s subunit %s" % (x.group(1), x.group(2)),
#			"Xase alpha Z chain -> Xase subunit alpha Z, but not regulatory chain"
#		))
        replacers.append(FilterReplace(
            re.compile(r"\bsubunit\s+([a-z])\b"),
            lambda x: "subunit %s" % x.group(1).upper(),
            "subunit lowercase_letter -> subunit uppercase_letter"
        ))
        replacers.append(FilterReplace(
            re.compile(r"\bchain\s+([a-z])\b"),
            lambda x: "chain %s" % x.group(1).upper(),
            "chain lowercase_letter -> chain uppercase_letter"
        ))
        replacers.append(FilterReplace(
            re.compile(r"\b([a-z])\s+subunit\b"),
            lambda x: "%s subunit" % x.group(1).upper(),
            "lowercase_letter subunit -> uppercase_letter subunit"
        ))
        replacers.append(FilterReplace(
            re.compile(r"\b([a-z])\s+chain\b"),
            lambda x: "%s chain" % x.group(1).upper(),
            "lowercase_letter chain -> uppercase_letter chain"
        ))
        replacers.append(FilterReplace(
            re.compile(r"\bsubunit\s+(small|large)"),
            lambda x: "%s subunit" % (x.group(1)),
            "subunit (small, large) -> (small, large) subunit"
        ))
        replacers.append(FilterReplace(
            re.compile(r"\bnon-ribosomal\s+peptide\s+synthase\b"),
            "non-ribosomal peptide synthetase",
            "synthase -> synthetase ... only in some situations"
        ))
        # type iv pili is special
        replacers.append(FilterReplace(
            re.compile(r"\btype\s+IV\s+pili(?!\sassociated\sprotein)\b"),
            "type IV pili associated protein",
            "standardize type IV pili"
        ))

        # make plural singular -- note that "subunits" should not appear here; it is weak
        replacers.append(FilterReplace(re.compile(r"\b(.*?ase)s\b"), lambda x: x.group(1), "singular -ases"))
        replacers.append(FilterReplace(re.compile(r"\bproteins\b"), "protein", "singular protein"))
        replacers.append(FilterReplace(re.compile(r"\bcomponents\b"), "component", "singular component"))
        replacers.append(FilterReplace(re.compile(r"\benzymes\b"), "enzyme", "singular enzyme"))
        replacers.append(FilterReplace(re.compile(r"\bsystems\b"), "system", "singular system"))
        replacers.append(FilterReplace(re.compile(r"\bfactors\b"), "factor", "singular factor"))
        replacers.append(FilterReplace(re.compile(r"\bregulators\b"), "regulator", "singular regulator"))
        replacers.append(FilterReplace(re.compile(r"\bkinases\b"), "kinase", "singular kinase"))
        replacers.append(FilterReplace(re.compile(r"\bpolymerases\b"), "polymerase", "singular polymerase"))
        replacers.append(FilterReplace(re.compile(r"\bphosphonates\b"), "phosphonate", "singular phosphonate"))

        # make transport -> transporter, but only in certain cases
        # (the order of these is deliberate, more specific to more general)
        replacers.append(FilterReplace(
            re.compile(r"\btransport$", re.I),
            "transporter",
            "transport -> transporter"
        ))
        replacers.append(FilterReplace(
            re.compile(r"\btransport(er)?\s+family\s+protein\b", re.I),
            "transporter",
            "transport family protein -> transporter"
        ))
        replacers.append(FilterReplace(
            re.compile(r"\btransport(er)?\s+family\b", re.I),
            "transporter",
            "transport family -> transporter"
        ))
        replacers.append(FilterReplace(
            re.compile(r"\btransport(er)?\s+protein\b", re.I),
            "transporter",
            "transport protein -> transporter"
        ))

        replacers.append(FilterReplace(
            re.compile(r"\btranscriptional\s+regulator\s+protein\b", re.I),
            "transcriptional regulator",
            "transcriptional regulator protein -> transcriptional regulator"
        ))
        replacers.append(FilterReplace(
            re.compile(r"\bchaperone\s+protein\b", re.I),
            "chaperone",
            "chaperone protein -> chaperone"
        ))
        replacers.append(FilterReplace(
            re.compile(r"\btwo-component\s+(response\s+)?regulator", re.I),
            "two-component system response regulator",
            "two-component (response) regulator -> two-component system response regulator"
        ))
        replacers.append(FilterReplace(
            re.compile(r"\bmajor\s+facilitator\s+superfamily\b", re.I),
            "major facilitator superfamily transporter",
            "major facilitator superfamily -> major facilitator superfamily transporter"
        ))
        # all cases of "N-terminal protein" "C-terminal protein",
        #   "N- protein" "C- protein" -- optionally preceded by comma space
        # terminal is optional because other words can be pruned before this point
        replacers.append(FilterReplace(
            re.compile(r"(?:,\s)?[NC]-(?:term(inal)?)? domain"),
            " domain",
            "N-terminal or C-terminal domain -> domain"
        ))
        replacers.append(FilterReplace(
            re.compile(r"\bsite\s+domain\b"),
            "site",
            "site domain -> site"
        ))
        # X, Y family -> Y family X
        # - only on end of string for now, there's more thought needed on what
        #   X, Y family Z becomes
        # - note the exception; this should become a list if it gets too complicated
        replacers.append(FilterReplace(
            re.compile(r"(.*)\,\s+((?!paralogous).*?)\s+(superfamily|family)\s*$"),
            lambda x: "%s %s %s" % (x.group(2), x.group(3), x.group(1)),
            "X, Y family -> Y family Z",
            skipif=[REORDERFAMILY]
        ))
        # replace X family with X family protein
        # - this could be smarter still about nouns that appear earlier in the string
        # - also note relationship with filter directly above
        replacers.append(FilterReplace(
            re.compile(r"(.*(?<!protein)\s+(family|superfamily)\s*$)"),
            lambda x: "%s protein" % x.group(1),
            "X family -> X family protein (end of string only)"
        ))
        replacers.append(FilterReplace(
            re.compile(r"^\s*\b([A-Za-z][a-z]{2}[A-Z])\s*$"),
            lambda x: "%s protein" % x.group(1),
            "four letter protein abbreviations should be followed by 'protein'"
        ))
        replacers.append(FilterReplace(
            re.compile(r"\b14-3-3\s+protein\b"),
            "14-3-3 family protein",
            "14-3-3 protein -> 14-3-3 family protein"
        ))
        replacers.append(FilterReplace(
            re.compile(r"biosynthesis\s*$"),
            "biosynthesis protein",
            "add protein to biosynthesis when at end of string"
        ))
        replacers.append(FilterReplace(
            re.compile(r"system\s*$"),
            "system protein",
            "add protein to system when at end of string"
        ))
        replacers.append(FilterReplace(
            re.compile(r"DNA\s+modification\s+methylase"),
            "DNA methylase",
            "unnecessary word: modification"
        ))
        replacers.append(FilterReplace(
            re.compile(r"isochorismatase\s+hydrolase"),
            "isochorismatase",
            "unnecessary word: hydrolase"
        ))
        self.clauseReplaceList = replacers

        #
        # ID deletions - remove words that look like database identifiers
        #
        # despite our best efforts, this step frequently leaves fragments
        # which are cleaned up later
        #
        self.idDeletionList = []
        idList = []
        # some ids are retained or deleted based on whether they have a
        # a family-ish predicate
        # - these strings are modifiers to other patterns, not filters in themselves
        familyPattern = r"\s*(kD(a)?|-like|family|protein\s+family)"
        exceptWhenFollowedByFamilyPat = r"(?!%s)" % familyPattern
        includingFollowingFamilyPat = r"(%s)?" % familyPattern

        # delete gi database fields
        # keep this one early as it has subfields left in it
        idList.append(re.compile(r"gi\|\S+\|\S+\b"))
        # strike swiss-prot headers
        idList.append(re.compile(r"sp\|[\S\|]+\b"))
        # delete UPF/DUF proteins of the form UPFxxx protein XXXXX_XXXXX
        idList.append(re.compile(r"(DUF|UPF)[0-9]+.*protein.*[A-Za-z0-9]+_[A-Za-z0-9]+"))

        # delete any word like XLCGF9.1 or 25D9-6 or L25599_2 or T1N15.5, but not 14-3-3,
        # as long as the first alphanumeric block contains at least one letter followed
        # by at least one number, and there is a number delim number sequence somewhere in there.
        # Oh, and not followed by a certain predicate.
        # - note the escaped dash in the punctuation selector, prevents range of punctuation
        #   from period to underscore
        # - that expression (?!-?\d+) fixes the undesirable greedy/negative lookahead behavior,
        #   which took a comical amount of time to solve, so please don't touch it
        # - also, this might be too many comments for one regex
        # - but while we're here, how are you doing?
        idList.append(re.compile(r"\b[A-Z0-9]*[A-Z]\d+([.\-_]\d+){1,}(?!-?\d+)" + exceptWhenFollowedByFamilyPat))
        # delete also AAAA0.0.0
        idList.append(re.compile(r"\b[A-Z0-9a-z]+\d+[._]\d+[._]\d+\b"))
        # delete ec 0.-.0.1, also optional parens around
        idList.append(re.compile(r"\[?\(?ec\s*([0-9\-]+\.){3}([0-9\-]+)\)?\]?"))
        # delete Zgc: prefixes:
        idList.append(re.compile(r"\bZgc:\w*\b"))
        # delete ids like OSJNBa0001M07.2
        idList.append(re.compile(r"\b[A-Z]{4,}[A-Za-z]*[0-9]{4,}[A-Za-z0-9]+\.\d+\b"))
        # delete munged yeast abbreviations: Yaa000aa, unless in a family
        idList.append(re.compile(r"Y[A-Za-z]{2}\d{3}[a-zA-Z]{1,2}" + exceptWhenFollowedByFamilyPat))
        # delete any word that ends in .00c
        idList.append(re.compile(r"\b.*?\.\d{2}c\b"))
        # delete AAA000Cp and AAA000Wp
        idList.append(re.compile(r"[A-Z]{3}\d{3}[C|W]p"))
        # delete any word that has dual versions at end, like: NN0000000_00.0
        idList.append(re.compile(r"\b(OJ)\d{6}_\d{2}\.\d\b"))
        # delete any word like: NN00000p
        idList.append(re.compile(r"\b(SD|RE|GM|IP|LD)\d+?p\b"))
        # delete any word like: Nnnnnnn.000 or Nnnnnnn_0, optionally preced by Em:
        idList.append(re.compile(r"\b([A-Za-z:]+)?(Y|Z|H|LD|B|H|F|K|AC|R)\S{4,7}[._]\d{1,3}\b"))
        # delete any word that is: SI:
        idList.append(re.compile(r"\bSI:\b"))
        # delete rice sequence names: OSJNBnnnnn.0
        idList.append(re.compile(r"\bOSJNB.*?\.\d$\b"))
        # delete Riken tag names: 0000000A00Rik
        idList.append(re.compile(r"\d{7}\w\d{2}Rik"))
        # delete old Broad-style locus numbers
        idList.append(re.compile(r"\b[A-Z]{1,2}[A-Z0-9][TG]_\d{5}\b"))
        # delete SCI0000a
        idList.append(re.compile(r"SCI\d{4}[a-z]"))
        # delete SLV.0
        idList.append(re.compile(r"SLV.\d"))
        # delete A0A0A.00 optional TIGR
        idList.append(re.compile(r"\b[A-Za-z0-9]+\.\d{2,}( TIGR)?\b"))
        # delete A0A0A0000 optional TIGR, as long as the first part isn't DUF0000 or UPF0000
        # -- if this exception list gets too long, just refactor and put some if/then logic in
        idList.append(
            re.compile(r"\b[A-Za-z0-9]+\d{4,}(?<!\b(?:DUF|UPF)\d{4})\b" + exceptWhenFollowedByFamilyPat))
        # delete AAAA0000-AAAA
        idList.append(re.compile(r"\b[A-Z]+\d{4,}-[A-Z]+\b"))
        # delete AE000000_0000
        idList.append(re.compile(r"\bA[EF]\d{6,}_\d+\b"))
        # delete any bit that ends with <space>TIGR
        idList.append(re.compile(r"\sTIGR\b"))
        # drop esangp ids
        idList.append(re.compile(r"\ben?sangp[0-9]+\b"))
        # never valid
        idList.append(re.compile(r"DEHA0"""))
        # delete Shy0*
        idList.append(re.compile(r"\bShy\d+\b"))
        # delete ID0*
        idList.append(re.compile(r"\bID\d+\b"))
        # delete RHA* tags
        idList.append(re.compile(r"\bRHA\d.*?\b"))
        # delete Rv0*a
        idList.append(re.compile(r"\bRv\d+[a-zA-Z]\b" + includingFollowingFamilyPat))
        # delete FTT0+a
        idList.append(re.compile(r"\bFTT\d+[a-zA-Z]?\b"))
        # delete Mb0+a
        idList.append(re.compile(r"\bMb\d+[a-zA-Z]?\b"))
        # delete U0+a
        idList.append(re.compile(r"\b[Uu]\d+[a-z]\b"))
        # delete IDs from Eubacterium eligens ATCC 27750
        idList.append(re.compile(r"\bEUBELI_\d+\b", re.I))
        # delete all spy id's that have at least one underscore somewhere in them
        idList.append(re.compile(r"\bspy[a-z/0-9]*_[a-z/0-9_]+\b", re.I))
        # delete UreABC
        idList.append(re.compile(r"\bUreABC\b"))
        # delete AFUA, unless it's part of a family
        idList.append(re.compile(r"\bAFUA_[A-Z0-9]+\b" + exceptWhenFollowedByFamilyPat))
        # delete CECR5
        idList.append(re.compile(r"\bCECR5\b"))
        # delete gb|* and gb-like identifiers
        idList.append(re.compile(r"\b[a-z]+\|\w+", re.I))
        # delete words that look like phone numbers
        # jcvi killed words that are entirely numbers and dashes, but there are
        # names which are parts of otherwise valid names
        idList.append(re.compile(r"(?:^|\s+)\d{3}\-\d{4}(?:\s+|$)"))
        # delete At0+g0+*
        idList.append(re.compile(r"At\d+g\d+\S*"))
        # AtRAD#+
        idList.append(re.compile(r"AtRAD\d+"))
        # YALI0*
        idList.append(re.compile(r"\bYALI0.*?\b"))
        # C-125
        idList.append(re.compile(r"\bC\-125\b"))
        # SAZ genes and friends
        idList.append(re.compile(r"\bSA[A-Z]*[0-9_]+\b"))
        idList.append(re.compile(r"\bUSA[A-Z0-9_]+\b"))

        # delete AA0+*
        # - This is commented to remind me that this is a bad idea; it
        #   takes out too many legitimate weirdo abbreviations.
        #idList.append(re.compile(r"\b[A-Z]{2}\d+\S*"))
        # delete rsh:*  [rsh followed by colon followed by anything]
        idList.append(re.compile(r"\brs[hq]:\S.*?\b"))
        # rsp_1547
        idList.append(re.compile(r"\brsp_\d+\b"))

        self.idDeletionList.extend([FilterRemove(idre, "delete id") for idre in idList])
        self.idDeletionList.append(FilterByFunction(removeUnderscoreIds, "remove underscore ids"))

        # delete everything before a colon and a space (probably an ID we missed)
        # so 'NADH:reductase' makes it through, but 'dhf94123: protein' doesn't
        self.idDeletionList.append(FilterRemove(
            re.compile(r"^.*: +"),
            "delete everything before colon and space--so 'NADH:reductase' is ok, but 'dhf94123: protein' isn't"
        ))

        #
        # These rules clean up punctuation.
        #
        self.punctuationList = []
        puncList = []

        greekLetters = ["alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta",
          "theta", "iota", "kappa", "lambda", "mu", "nu", "xi", "omicron", "pi", "rho",
          "sigma", "tau", "upsilon", "phi", "chi", "psi", "omega"]
        for gletter in greekLetters:
            puncList.append(FilterReplace(
                re.compile(r"\&(%s)\;" % gletter, re.I),
                lambda x: x.group(1).lower(),
                "un-escape the greek alphabet (%s)" % gletter
            ))
        greekLettersReText = "\(:" + "|".join(greekLetters) + "\)"

        # delete all occurances of & > <
        puncList.append(FilterRemove(
            re.compile(r"[\&\>\<]"),
            "delete all & > <"
        ))
        # delete spaces before (semi)colons and commas
        # (whitespace followed by a lookahead assertion that matches a colon or a space)
        puncList.append(FilterRemove(
            re.compile(r"\s+(?=[\:|\;|\,])"),
            "delete spaces before (semi)colons and commas"
        ))
        # delete spaces at beginning or end of name
        puncList.append(FilterRemove(re.compile(r"^\s+"), "delete spaces at beginning of name"))
        puncList.append(FilterRemove(re.compile(r"\s+$"), "delete spaces at end of name"))
        # replace all whitespace padded parens with just the paren, so ( abc  ) becomes (abc)
        puncList.append(FilterReplace(
            re.compile(r"\s+\)"),
            ")",
            "replace whitespace padded close paren with just the paren"
        ))
        puncList.append(FilterReplace(
            re.compile(r"\(\s+"),
            "(",
            "replace whitespace padded open paren with just the paren"
        ))
        puncList.append(FilterReplace(
            re.compile(r"\s+\]"),
            "]",
            "replace whitespace padded close bracket with just the bracket"
        ))
        puncList.append(FilterReplace(
            re.compile(r"\[\s+"),
            "[",
            "replace whitespace padded open bracket with just the bracket"
        ))
#		# delete closing brackets at the end of a name, even if unmatched
#		puncList.append(FilterRemove(
#			re.compile(r"(?:\[[^]]*)\]\s*$"),
#			"delete closing brackets at end of name"
#		))
        # delete unbalanced parentheses and brackets (open without a close)
        puncList.append(FilterRemove(
            re.compile(r"\([^)]*$"),
            "delete unbalanced parens (open without close)"
        ))
        puncList.append(FilterRemove(
            re.compile(r"\[[^]]*$"),
            "delete unbalanced brackets (open without close)"
        ))
        # delete unbalanced parentheses and brackets (close without an open)
        puncList.append(FilterReplace(
            re.compile(r"^([^(]*)\)[))-]*"),
            lambda x: x.group(1),
            "delete unbalanced parens (close without open)"
        ))
        puncList.append(FilterReplace(
            re.compile(r"^([^[]*)\][))-]*"),
            lambda x: x.group(1),
            "delete unbalanced brackets (close without open)"
        ))
        # delete empty parentheses and brackets
        puncList.append(FilterRemove(
            re.compile(r"\[\s*\]"),
            "delete empty brackets"
        ))
        puncList.append(FilterRemove(
            re.compile(r"\(\s*\)"),
            "delete empty parens"
        ))
        # replace multiple spaces and embedded tabs/newlines with a single space
        puncList.append(FilterReplace(
            re.compile(r"[ \t\n]+"),
            " ",
            "replace tabs, newlines, and multiple spaces with one space"
        ))
        # replace double or longer hyphen with single hyphen
        puncList.append(FilterReplace(
            re.compile(r"--+"),
            "-",
            "replace double hyphen with single"
        ))
        # replace spaces surrounding a /
        puncList.append(FilterReplace(
            re.compile(r"\s?/\s?"),
            "/",
            "delete spaces surrounding a /"
        ))
        # delete "(a.k.a..*)"
        puncList.append(FilterRemove(
            re.compile(r"\.?\s+\(a\.k\.a\.\s*[^)]*\)"),
            "delete (a.k.a.)"
        ))
        # delete abandoned leading or trailing punctuation, likely due to deleted ids
        # ex: /K21C13_21 becomes / and should be removed
        puncList.append(FilterRemove(
            re.compile(r"^[-\/.*]"),
            "delete leading punctuation"
        ))
        puncList.append(FilterRemove(
            re.compile(r"[-\/.*]$"),
            "delete trailing punctuation"
        ))
        # replace any combination of comma period or double comma with comma
        puncList.append(FilterReplace(
            re.compile(r"([\.\,][\.\,]+)"),
            ",",
            "replace any weird combination of comma and period with comma"
        ))
        # delete isolated period
        puncList.append(FilterReplace(
            re.compile(r"\s+\.\s+"),
            " ",
            "delete isolated period"
        ))
        self.punctuationList = puncList


        #
        # These rules really clean up punctuation - more than the annotators like.
        # So, we apply these extra cleaners only to automatically assigned names.
        #
        autoPuncList = []
        # (this is rough and will need refinement)
        autoPuncList.append(FilterRemove(
            re.compile(r"[,;]\s+(?!family)(?!superfamily).*"),
            "delete notes after commas and semicolons -- except when followed by family or superfamily",
            skipif=[NOTAUTOGEN, REMOVETRAILING]
        ))
        # (this is rough and will need refinement)
        autoPuncList.append(FilterRemove(
            re.compile(r"\s+[-]\s+(?!family)(?!superfamily).*"),
            "delete notes after dashes surrounded by spaces -- except when followed by family or superfamily",
            skipif=[NOTAUTOGEN, REMOVETRAILING]
        ))
#       autoPuncList.append(FilterRemove(
#           re.compile(r"(?<![\w\-\(])\[[^\]]*\](?![\w\-\)])$"),
#           "delete brackets and their contents at the end of names, except in cases like AD(P) or (3,5)-word",
#           skipif=[NOTAUTOGEN]
#       ))
#       autoPuncList.append(FilterRemove(
#           re.compile(r"(?<![\w\-\[])\([^\)]*\)(?![\w\-\]])$"),
#           "delete parentheses and their contents at the end of names, except in cases like AD[P] or [3,5]-word",
#           skipif=[NOTAUTOGEN]
#		))
        autoPuncList.append(FilterRemove(
            re.compile(r"^[\.\,]"),
            "delete initial periods or commas -- usually gremlins from previous rules",
        ))

        self.automaticPunctuationList = autoPuncList

        #
        # Clean up fragments and bad punctuation
        #
        self.cleanupList = []
        # delete leading "the"
        self.cleanupList.append(FilterRemove(
            re.compile(r"^\s*(T|t)he\b\s*"),
            "delete leading 'the'"
        ))
        # names should begin with a letter, numeral or quote
        self.cleanupList.append(FilterRemove(
            re.compile(r"^[^a-zA-Z0-9\'\"\[(]+"),
            "names should begin with a letter, numeral, quote, or opening paren/bracket"
        ))
        # names should end with a letter, numeral, quote, or closing parenthesis/bracket
        self.cleanupList.append(FilterRemove(
            re.compile(r"[^a-zA-Z0-9\'\"\])]+$"),
            "names should end with a letter, numeral, quote, or closing paren/bracket"
        ))
        # question marks indicate a unicode gremlin, change to a space
        self.cleanupList.append(FilterReplace(
            re.compile(r"\?"),
            " ",
            "change question marks (unicode) to whitespace"
        ))
        # if something was removed above and leaves the trailing fragment "similar to", remove that fragment
        self.cleanupList.append(FilterRemove(
            re.compile(r"similar\s+to\s*$", re.I),
            "remove 'similar to' fragment"
        ))
        # names should not end with a conjunction
        self.cleanupList.append(FilterRemove(
            re.compile(r"\b(the|and|or|with)\s*$", re.I),
            "names should not end with a conjunction"
        ))
        # hypothetical protein similar to protein, usually caused by removing id
        # (for example, "hyp protein similar to ID protein")
        self.cleanupList.append(FilterReplace(
            re.compile(r"^hypothetical\s+protein\s+similar\s+to\s+?(protein)?$", re.I),
            "hypothetical protein",
            "hypothetical protein similar to protein -> hypothetical protein"
        ))
        # this is a remnant of protein, ID family
        self.cleanupList.append(FilterReplace(
            re.compile(r"protein,\s+family(?!\s+\d)"),
            "protein",
            "protein, family -> protein"
        ))
        # names should never start with family or superfamily
        self.cleanupList.append(FilterRemove(
            re.compile(r"^(family|superfamily)"),
            "remove leading family or superfamily"
        ))

        #
        # Some institutes don't discard names with low confidence words (above).
        # This list is an attempt to implement the spirit of their name saving policies.
        # 99% of the time, the only acceptable weak name is "putative".
        #
        weakNameList = []

        # First, convert every acceptable low-confidence term to putative X
        #   similar to Y putative X-like -> putative Y putative putative X
        #   similar to X, putative -> putative putative X
        # then wipe out the duplication:
        #   putative Y putative putative X -> putative Y putative X
        # then retain only the rightmost one:
        #   putative Y putative X -> putative X

        # anything that's "protein of unknown function" is not that strong
        weakNameList.append(FilterReplace(
            re.compile(r".*protein\s+of\s+unknown\s+function.*"),
            "hypothetical protein",
            "anything that's 'protein of unknown function' is not that good",
            runif=[RETAINWEAK]
        ))
        # first we convert all other weak names to putative
        weakNameList.append(FilterReplace(
            re.compile(r"(similar\s+to|strong\s+similarity\s+to|probable|homolog[ue]*?\s+of|homolog[ue]*?\s+to)", re.I),
            "putative",
            "convert other weak names to putative",
            runif=[RETAINWEAK]
        ))
        # replace all "putative X, putative" with putative X
        # (you could combine the following two patterns,
        #  but it would be deep magic and not as readable)
        weakNameList.append(FilterReplace(
            re.compile(r".*putative\s*(.*?),\s+putative", re.I),
            lambda x: "putative %s" % x.group(1),
            "putative X, putative -> putative X",
            runif=[RETAINWEAK]
        ))
        # replace all "X, putative" with putative X
        weakNameList.append(FilterReplace(
            re.compile(r"(.*)\,\s+putative", re.I),
            lambda x: "putative %s" % x.group(1),
            "X, putative -> putative X",
            runif=[RETAINWEAK]
        ))
        # replace all "putative X-like" with putative X
        # (there might be a way to combine the following two patterns,
        #  but it would be deep magic and not as readable)
        weakNameList.append(FilterReplace(
            re.compile(r".*putative\s*(.*?)-(like|related)", re.I),
            lambda x: "putative %s" % x.group(1),
            "putative X-like -> putative X",
            runif=[RETAINWEAK]
        ))
        # replace all "X-like" with putative X
        weakNameList.append(FilterReplace(
            re.compile(r"(.*)-(like|related)", re.I),
            lambda x: "putative %s" % x.group(1),
            "X-like -> putative X",
            runif=[RETAINWEAK]
        ))
        # remove all occurances of similarity, validated, fragment, imported
        # and the brackets or parens that surround them
        weakNameList.append(FilterRemove(
            re.compile(r"\(?\[?(similarity|validated|fragment|imported)\)?\]?", re.I),
            "remove all occurances of similarity, validated, fragment, imported",
            runif=[RETAINWEAK]
        ))
        # eliminate duplicates likely created by above steps
        weakNameList.append(FilterReplace(
            re.compile(r"putative\s+putative", re.I),
            "putative",
            "putative putative -> putative",
            runif=[RETAINWEAK]
        ))
        # retain only rightmost putative clause
        # in the case of multiple clauses, keep only the rightmost one
        weakNameList.append(FilterReplace(
            re.compile(r".*putative.*?(putative.*?)$", re.I),
            lambda x: x.group(1),
            "retain only the rightmost putative clause",
            runif=[RETAINWEAK]
        ))
        # in the case of only one clause, keep only that one
        weakNameList.append(FilterReplace(
            re.compile(r".*(putative.*?)$", re.I),
            lambda x: x.group(1),
            "in the case of only one clause, keep just that one",
            runif=[RETAINWEAK]
        ))

        # special cases
        weakNameList.append(FilterRemove(
            re.compile(r".*unknown.*"),
            "kill: unknown",
            runif=[RETAINWEAK]
        ))
        weakNameList.append(FilterRemove(
            re.compile(r"predicted\s+protein"),
            "delete predicted protein",
            runif=[RETAINWEAK]
        ))
        weakNameList.append(FilterRemove(
            re.compile(r"putative\s+protein"),
            "delete putative protein",
            runif=[RETAINWEAK]
        ))
        weakNameList.append(FilterReplace(
            re.compile(r"putative\s+conserved\s+hypothetical\s+protein"),
            "hypothetical protein",
            "putative conserved hypothetical protein -> hypothetical protein",
            runif=[RETAINWEAK]
        ))
        self.weakNameSaveList = weakNameList

        #
        # Organism names
        #
        # put more specific names before less specific names, for example "mouse-ear cress"
        # before "mouse", or else you'd end up with "-ear cress"
        #
        # note that there is a protein called "armadillo protein"
        organismNames = [
            r"arabidopsis\s+thaliana",
            r"arabidopsis",
            r"oryza\s+sativa",
            r"rice",
            r"maize",
            r"tomato",
            r"potato",
            r"spinach",
            r"rye",
            r"liver",
            r"brain",
            r"adult",
            r"child",
            r"lycopersicum\s+esculentum",
            r"carrot",
            r"drosophila\s+melanogaster",
            r"human",
            r"mouse-ear\s+cress",
            r"mouse",
            r"chlamydomonas\s+reinhardtii",
            r"common\s+tobacco",
            r"tobacco",
            r"boreogadus\s+saida",
            r"garden\s+petunia",
            r"fission\s+yeast",
            r"alfalfa",
            r"proso\s+millet",
            r"sorghum",
            r"long-staminate\s+rice",
            r"mung\s+bean",
            r"fava\s+bean",
            r"wheat",
            r"barley",
            r"avocado",
            r"garden\s+pea",
            r"bacillus\s+halodurans",
            r"curled-leaved\s+tobacco",
            r"E[\.]?\s*coli",
            r"salmonella",
            r"S[\.]?\s*typhi",
        ]
        # also take care of preceding "in" and enclosing parens because jcvi did
        organismNamesRe = r"-?\s*(?:\bin)?\s*\[?\(?(%s)\)?\]?"
        self.organismNameList = []
        for orgname in organismNames:
            reorg = re.compile(organismNamesRe % orgname, re.I)
            self.organismNameList.append(FilterRemove(reorg, "delete organism names"))

        #
        # Whole name deletion
        #
        # Distinct from keyword deletion and phrase deletion (and the rest) in
        # that these names are likely to be the output of the entire filtering
        # process. These names as part of a word are fine, but alone are not
        # worth keeping.
        # This should always remain last in the filter list.
        self.wholeNameModificationList = []
        wholeNameDeletions = [
            "CDS",
            "CDS,\s+putative",
            "small\s+basic\s+protein",
            "small\s+secreted\s+protein",
            "surface\s+antigen\s+protein",
            "large\s+exoprotein",
            "basic\s+protein",
            "protein",
            "trna",
            "precursor",
            "transporter",
            "ribosomal\s+protein",
            "bi[-\s]?functional\s+protein",
            "unknown\s+protein",
            "unknown",
            "subunit\s+[A-Za-z0-9]",
            "domain",
            "domain-containing\s+protein",
        ]
        wndList = [FilterRemove(
                        re.compile(r"^%s$" % x, re.I),
                        "insufficient whole name")
                   for x in wholeNameDeletions]
        self.wholeNameModificationList = wndList


    ##
    # Subjects a name to a full-court press of name fixes, cleanups
    # and rearrangements. Callers should expect a None value if the name is
    # filtered to nothingness.
    #
    # @param isAutogeneratedName When 1, name can be outright rejected
    #  for using low confidence words. In addition, more regular
    #  expressions are applied to transform the name. If this is set to 1,
    #  callers must be prepared for a null return value.
    # @param getOutput When 1, return a tuple rather than just the filtered
    #  name: (filteredName, filterProcess)
    # @see filters.FilterGroup
    def filter(self, name, isAutogeneratedName=1, getOutput=0):
        # no need to be fancy if this isn't a string
        if name:
            name = name.strip()
        if not name or name == "":
            if getOutput:
                return (None, None)
            else:
                return None

        origName = name

        # translate any option into filter skipif/runif for self-selecting
        skipif = []
        runif = []
        # skip if not automatically generated
        if not isAutogeneratedName:
            skipif.append(NOTAUTOGEN)
        # there are filters that don't run if we're skipping weak names
        # and others that run only if we are
        if self.saveWeakNames:
            skipif.append(RETAINWEAK)
            runif.append(RETAINWEAK)
        # skip if not reordering family
        if not self.reorderFamily:
            skipif.append(REORDERFAMILY)
        # skip if not removing trailing clauses
        if not self.removeTrailingClauses:
            skipif.append(REMOVETRAILING)

        name, filterprocess = self.fgroup.run(name, skipif=skipif, runif=runif)

        if not name or name == "":
            if origName:
                print "didn't like source name '%s' at all - filtered to nothing" % origName
            name = None

        if getOutput:
            return (name, filterprocess)
        else:
            return name


    # @see filter
    def cleanup(self, name, isAutogeneratedName=1, getOutput=0):
        """
        Like filter(), but retains generic names.
        """
        answer = None
        filterprocess = None
        rank = self.rankName(name)
        if rank == 0 or rank == 1:
            pass
        elif rank == 3:
            suffix = weakPredictionRe.match(name).group(1)
            newname, filterprocess = self.filter(suffix, isAutogeneratedName, getOutput=1)
            if newname:
                answer = newname
        else:
            answer, filterprocess = self.filter(name, isAutogeneratedName, getOutput=1)
        # if we have not derived a decent name by now, stick with the
        # defaults
        if not answer:
            answer = DEFAULTNAME

        if getOutput:
            return (answer, filterprocess)
        else:
            return answer


    def getLowConfidenceFilters(self):
        return [x for x in self.lowConfidenceRemoval]


    def getIdDeleters(self):
        return [x for x in self.idDeletionList]


    def scoreNamePair(self, namePair):
        """
        Input:
            A tuple: (name, weight), where the first item is a string and the
            second item is a number indicating confidence (higher is better).

        Output:
            A tuple: (name, rank, weight)
            The first grade (rank) is more important than the second grade
            (weight), which is only given as a way to delineate between names
            of equal rank.
        """
        name = namePair[0]
        weight = namePair[1]

        if name is None:
            return (name, -1, 0)
        # no variation in these first three names, so no need for second score
        elif predictedProteinRe.match(name):
            return (name, 0, None)
        elif hypotheticalProteinRe.match(name):
            return (name, 1, None)
        # from here on, variations introduced, and need second score to measure
        # confidence in each name.
        elif weakPredictionRe.match(name):
            return (name, 3, weight)
        else:
            # can't recognize it as bad, presumably it is pretty good
            return (name, 4, weight)

    def rankName(self, name):
        """
        Returns the first grade (rank) from scoreNamePair().

        used by geneCmp
        """
        return self.scoreNamePair([name, 0])[1]

    def isGenericName(self, name):
        """
        Returns 1 if the name is generic, i.e., nonspecific.
        """
        return self.rankName(name) <= 2

    def isWeakName(self, name):
        """
        Returns 1 if the name is generic or low confidence.
        """
        return self.rankName(name) <= 3

    def cmpNamePairs(self, lhs, rhs):
        lname, lrank, lscore = self.scoreNamePair(lhs)
        rname, rrank, rscore = self.scoreNamePair(rhs)
        if lrank == rrank:
            return cmp(lscore, rscore)
        else:
            return cmp(lrank, rrank)


##
# Front end commands
#


def cleanup(inputFileName, outputFileName=None,
            populate_default=0, retain=0, silent=0):
    """ Take a filename, filter names found within, print output. """
    if not silent:
        print "Cleaning up names found in: " + str(inputFileName)
    if not outputFileName:
        outputFileName = util.addPredicateToFileName(inputFileName, "_bioname")
        if not silent:
            print "Writing results to: " + str(outputFileName)
    fields = util.simpleNamesFileReader(inputFileName)
    bname = BioName(hmp=retain)
    filteredfields = []
    func = None
    if populate_default:
        func = bname.cleanup
    else:
        func = bname.filter

    for id, name in fields:
        filtered, filterprocess = func(name, getOutput=1)
        if not silent and name != filtered:
            print id, filterprocess
        filteredfields.append((id, filtered))
    if not silent:
        print "Filtered %d names" % len(filteredfields)
    util.simpleNamesFileWriter(filteredfields, outputFileName)
