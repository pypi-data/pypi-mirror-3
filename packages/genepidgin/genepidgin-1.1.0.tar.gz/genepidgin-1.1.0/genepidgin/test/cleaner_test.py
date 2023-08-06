from __future__ import nested_scopes

import nose.tools

import os
import os.path

import genepidgin.cleaner

# The expression "alpha omega" is a neutral phrase used to represent
# generic name pieces. It's not actual information from any real gene
# name - it's a neutral placeholder.

DEFNAME = "hypothetical protein"

DATA_ROOT = "./genepidgin/test/data"

# Weird design that nose tests aren't directly yieldable
def assert_equal(*args):
    return nose.tools.assert_equal(*args)
def assert_is_none(*args):
    return nose.tools.assert_is_none(*args)

# http://achinghead.com/nosetests-generators-descriptions.html
def assert_call_yields_none(func, name):
    assert func(name) is None, "%s failed" % name

class TestCleaner():

    def assert_file_equals(self, file1, file2):

        f1 = open(file1, 'r')
        source = f1.read()
        f1.close()

        f2 = open(file2, 'r')
        dest = f2.read()
        f2.close()

        assert_equal(source, dest, "%s != %s" % (file1, file2))

    def testCleanupStartsWithProtein(self):

        # exceptions
        assert_equal(genepidgin.cleaner.cleanupStartsWithProtein("proteinase"), "proteinase")
        assert_equal(genepidgin.cleaner.cleanupStartsWithProtein("protein kinase"), "protein kinase")
        assert_equal(genepidgin.cleaner.cleanupStartsWithProtein("protein phosphatase"), "protein phosphatase")
        assert_equal(genepidgin.cleaner.cleanupStartsWithProtein("protein alpha transport"), "protein alpha transport")
        assert_equal(genepidgin.cleaner.cleanupStartsWithProtein("protein proteinase"), "protein proteinase")

        # the rule
        assert_equal(genepidgin.cleaner.cleanupStartsWithProtein("protein alpha"), "alpha")

    def testNameLength(self):
        name = "hello my good fellow" # 20 characters

        # require short name, should return nothing
        bname = genepidgin.cleaner.BioName(maxNameLength = 10)
        yield assert_call_yields_none, bname.filter, name

        # require longer name, should return nothing
        bname = genepidgin.cleaner.BioName(minNameLength = 30)
        yield assert_call_yields_none, bname.filter, name

        # with no parameters, should return input
        bname = genepidgin.cleaner.BioName()
        assert_equal(bname.filter(name), name)

    def testNameDrop(self):

        # these names should all be shot down
        # (add to this list as bad stuff sneaks through and is repaired)
        suspects = [
            # hypothetical
            "hypothetical protein MG03103.4 [Magnaporthe grisea 70-15]",
            # X Chain X
            "C Chain C, High Resolution Structures Of Scytalone Dehydratase- Inhibitor Complexes Crystallized At Physiological Ph"
            # similar to
            "similar to phosphoprotein phosphatase (EC 3.1.3.16) 1-gamma catalytic chain - mouse [Mus musculus]"
            # fragment
            "histone H3.2 - Tetrahymena furgasoni (fragment)",
            # esang*
            "ESANGP00000020220",

            # like (has temporary green light in filters
            #"ACTZ_NEUCR Actin-like protein (Centractin)",

            # related
            "RAC1_BOVIN Ras-related C3 botulinum toxin substrate 1 (p21-Rac1)",
            # tags
            "SPCC306.01",
            "dJ191N21.2.4",
            "/F14F18_180",
            "OJ000114_01.9",
            "AC000103_31 F21J9.3",
            "OSJNBa0011F23.1",
            "K02A2.6",
            "GM21055p",
            "0710008K08Rik",
            "ID307",
            "Shy25",
            "Rv123a",
            "FTT123a",
            "FTT123",
            "Mb123a",
            "Mb123",
            "U123a",
            "u123a",
            "UreABC",
            # C-125
            "C-125",
            # YALI0*
            "YALI0C24376p",
            # "whole string is crap" tests
            "RIKEN cDNA 0710008K08 gene",
            "cDNA 0710008K08 RIKEN gene",
            # junk
            "ORF ORF ORF",
            "expressed protein",
            # product
            "product 5NUC",
            "product DNA segment",
            "product expressed sequence",
            "product sodium",
            "product leucine-rich repeat",
            "product VNG2075C",
            "product Aedes aegypti 34 kDa salivary secreted protein 34k-2",
            "47 kDa protein",
            "51.5 kDa protein",
            "E Chain E",
            "protein /",
            "uncharacterised conserved protein",
            "conserved fungal family",
            "dubious",
            "mitochondrial precursor",
            "transpoter",
            "putavie",
            "key really important protein",
            "proba ble protein",
            "similarity to something I once saw",
            # whole name deletions (not id or lowConfidence kill triggers)
            "CDS",
            "cds",
            "CDS, putative",
            "small basic protein",
            "small secreted protein",
            "surface antigen protein",
            "large exoprotein",
            "basic protein",
            "protein",
            "trna",
            "precursor",
            "transporter",
            "ribosomal protein",
            "bi-functional protein",
            "bi functional protein",
            "bifunctional protein",
            "domain",
            "domain-containing protein",
            # jcvi bad ids
            "gb|hello",
            "557-2776",
            "BT002689",
            "AF370589",
            "At5g10001",
            "ec 2.1.0.-",
            "(ec-.1.4.-)",
            "[ec  2.-.-.-]",
            "AtRAD17",
            "T1N15.5",
            "F1N21.20",
            # jcvi specific phrase kills
            "from",
            "(photosystem q(a) protein)",
            # partials
            "5'-partial",
            "5-partial",
            "3'-partial",
            "3-partial",
            # software names
            "glimmer", "glimmer3", "glimmer 3",
            "geneid", "gene_id", "gene id",
            "genemark", "genemarkhmm", "genemarkhmmes",
            "conrad",
            "blast",
            "augustus",
            "fgenesh", "fgenesh+",
            "hmmer",
            "metagene",
            "snap",
            "zcurve_b", "zcurve_v", "zcurvev", "zcurveb",
            # orfs
            "ORF",
            "ORF123",
            # Sharvari and Narmada found these names assigned to a broad gene set
            "uncharacterized protein yqel",
            "uncharacterized protein yqeJ",
            "hypothetical protein jggJ",
            "ORF _o284",
            # subunit whole names
            "subunit A",
            "subunit z",
            "subunit 3",
            "UPF0435 protein BCAH187_A0520",
        ]

        bname = genepidgin.cleaner.BioName()
        for suspect in suspects:
            yield assert_call_yields_none, bname.filter, suspect

    # separated out in case we want to test low-confidence separately
    # from immediate drops
    def testLowConfidenceWords(self):

        suspects = [
            "conserved",
            "DUF",
            "dubious",
            "doubtful",
            "fragment",
            "homolog",
            "homologue",
            "hypothetical",
            "key",
            "may",
            "novel",
            "of",
            "open reading frame",
            "partial",
            "possibly",
            "predicted",
            "probable",
            "product",
            "putative",
            "related",
            "similar",
            "similarity",
            "synthetic",
            "uncharacterised",
            "UNCHARACTERIZED", # note the caps, did you miss them?
            "unknown",
            "unnamed",
            "gene_id",
        ]
        notfiltered = "alpha omega protein"
        suspectnames = ["%s %s" % (x, notfiltered) for x in suspects]

        bname = genepidgin.cleaner.BioName()
        for suspect in suspectnames:
            yield assert_call_yields_none, bname.filter, suspect

        # test that manually annotated weakish names are ok
        # (this is probably going to need rewriting)
        lesssuspicious = [
            "conserved hypothetical alpha omega protein",
            "conserved hypothetical protein",
        ]
        for input in lesssuspicious:
            answer, filteroutput = bname.filter(input, isAutogeneratedName=0, getOutput=1)
            yield assert_equal, answer, input


    def testNameReplaceManual(self):
        bname = genepidgin.cleaner.BioName()
        tests = [
          ("xap-5-like protein", "xap-5-like protein", "xap-5-like protein"),
        ]
        for input, manualRes, autoRes in tests:
            yield assert_equal, bname.cleanup(input, 1), manualRes
            yield assert_equal, bname.cleanup(input, 0), autoRes


    def testNameReplace(self):

        # each tuple is a test case, with input and desired output of each name
        # (add to this list as positive behavior is identified)
        tests = [
            # bracket/paren removal
#			("beta tubulin [Penicillium formosanum]",
#            "beta tubulin"),
#			("beta tubulin (symmetrical)",
#            "beta tubulin"),
            # caps and underscore junk at beginning, dash in middle of retained word
            ("TBB4_XENLA TUBULIN BETA-4 CHAIN",
             "tubulin beta-4 chain"),
            # words following dash removal
            ("ubiquitin - fruit fly (Drosophila melanogaster)",
             "ubiquitin"),
            # dump after comma
            ("actin A3, cytosolic - silkworm",
             "actin A3"),
            # ...but retain comma family/superfamily
            ("extracellular solute-binding protein, family 1",
             "extracellular solute-binding protein, family 1"),
            ("extracellular solute-binding protein, superfamily 1",
             "extracellular solute-binding protein, superfamily 1"),
            # dump after dash but preserve parens
            ("actin (clones Ia and IIb) - hydromedusa (Podocoryne carnea)",
             "actin (clones Ia and IIb)"),
            # retain roman numeral case, dump after dash, dump parens
            ("beta-tubulin isotype I - nematode (Haemonchus contortus)",
             "beta-tubulin isotype I"),
            # remove precursor
            ("ubiquitin precursor - chicken",
             "ubiquitin"),
            # dump parens in middle, retain end
            ("phosphoprotein phosphatase (EC 3.1.3.16) bimG - Emericella nidulans",
             "phosphoprotein phosphatase bimG"),
            # Atpase to ATPase, fix capitalization
            (" 70kd Heat Shock Cognate Protein Atpase Domain, K71m Mutant",
             "70kd Heat Shock Cognate protein ATPase Domain"),
            # ACTIN to actin
            ("ACT_CHERU ACTIN",
             "actin"),
            # legitimate caps retained
            ("ADP-ribosylation factor - bovine",
             "ADP-ribosylation factor"),
            # remove trailing punctuation
            ("beta beta /K21C13_21",
             "beta"),
            # XXX pending conflic change
            #("alpha omega [,.", "alpha omega"), # special request from ncvi
            # leading/trailing spaces
            ("  uracil-4  ",
             "uracil-4"),
            # remove leading "the",
            ("The chromate ion transporter",
             "chromate ion transporter"),
            # typos
            ("omega protein protein", "omega protein"),
            ("zootacious protei", "zootacious protein"),
            ("chmomosome", "chromosome"),
            ("alpha transpoter", "alpha transporter"),
            ("alpha transpo_te", "alpha transporter"),
            ("alpha transporte", "alpha transporter"),
            ("putaive", "putative"),
            ("putitave", "putative"),
            ("bindingprotein", "binding protein"),
            ("alpha hypotetical transporter", "alpha hypothetical transporter"),
            ("alpha hhypothetical transporter", "alpha hypothetical transporter"),
            ("alpha hypotehtical transporter", "alpha hypothetical transporter"),
            ("alpha domain signalling protein", "alpha domain signaling protein"),
            ("oligoeptide", "oligopeptide"),
            ("dephosph", "dephospho"),
            ("glycosy", "glycosyl"),
            ("symport", "symporter"),
            ("atpas", "ATPase"),
            # clause replacements
            ("hearty transposase mutator type", "hearty transposase"),
            ("certain motif", "certain domain-containing protein"),
            ("absolute domain", "absolute domain-containing protein"),
            ("unerring domain protein", "unerring domain-containing protein"),
            # involved in
            ("good protein involved in chicanery", "good protein"),
            # bifunctional protein
            ("Bifunctional protein alpha", "alpha"),
            ("zed bifunctional protein", "zed"),
            # low molecular weight clause removal
            ("filter low molecular weight", "filter"),
            ("filter low affinity", "filter"),
            ("filter low-affinity", "filter"),
            # band # protein removal
            #("alpha band 3 protein beta", "alpha beta"),
            ("atpase", "ATPase"),
            ("gtPase", "GTPase"),
            ("gtptest", "gtptest"),
            # kDa / heat shock
            ("18 kDa heat shock protein", "hsp18-like protein"),
            ("heat shock 70 kDa protein", "hsp70-like protein"),
            ("65 kDa virulence protein", "virulence protein"),
            ("40 kDa peptidyl-prolyl cis-trans isomerase", "peptidyl-prolyl cis-trans isomerase"),
            ("hypothetical protein similar to heat shock protein hsp29", "hsp29-like protein"),
            ("hypothetical protein similar to 32 kDA heat shock", "hsp32-like protein"),
            ("52 kDa monster protein", "monster protein"),
            # weak name rules
            ("hypothetical protein similar to protein", DEFNAME),
            ("hypothetical protein similar to ", DEFNAME),
            ("hypothetical protein similar to", DEFNAME),
            ("]bad protein name", "bad protein name"),
            ("]-bad protein name", "bad protein name"),
            ("desaturase desaturase)", "desaturase"),
            ("carboxypeptidase Y inhibitor )", "carboxypeptidase Y inhibitor"),
            ("carbonyl reductase 1 9-reductase)", "carbonyl reductase 1 9-reductase"),
            ("NAD kinase /ATP NAD kinase)", "NAD kinase/ATP NAD kinase"),
            ("seryl-tRNA synthetase synthetase)", "seryl-tRNA synthetase"),
            ("vacuolar calcium ion transporter /H(+) exchanger)",
              "vacuolar calcium ion transporter/H(+) exchanger"),
            ("snorkle mitochondrial precursor", "snorkle"),
            ("cat food precursor", "cat food"),
            ("mRNA export factor crp79  (Poly(A)-binding protein)",
             "mRNA export factor crp79 (Poly(A)-binding protein)"),
            ("leukotriene A-4 hydrolase   hydrolase)", "leukotriene A-4 hydrolase"),
            ("phosphatidylinositol-4-phosphate 5-kinase fab1   (PtdIns(4)P-5-kinase)",
              "phosphatidylinositol-4-phosphate 5-kinase fab1 (PtdIns(4)P-5-kinase)"),
            ("hypothetical protein similar to amino-acid permease [imported]",
              "amino-acid permease"),
            # make plural singular
            ("polymerases", "polymerase"),
            ("enzymes", "enzyme"),
            ("kinases", "kinase"),
            ("systems", "system protein"),
            ("systems action translator", "system action translator"),
            ("factors", "factor"),
            ("regulators", "regulator"),
            ("alpha omega proteins", "alpha omega protein"), # protein alone is a fragment
            ("components", "component"),
            ("phosphonates", "phosphonate"),
            # removing crap punctuation
            ("integral?membrane?protein Ptm1", "integral membrane protein Ptm1"),
            # zapping this knocks out a bunch of good names in swiss-prot too
#			(""" \"2',3'-cyclic nucleotide\" """, "2',3'-cyclic nucleotide"),
            # "-associated region" clause removal
            ("amino acid permease-associated region", "amino acid permease"),
            ("sample protein and inactivated derivatives", "sample protein"),
            ("sample protein and other weird things", "sample protein"),
            ("sample protein associated with other weird things", "sample protein"),
            ("sample protein and 2 protein", "sample protein"),
            # beginning with the word protein is usually not correct, but not always
#			("protein enzyme", "enzyme"),
            ("protein complex subunit", "protein complex subunit"),
            ("protein polymerase", "protein polymerase"),
            # remove any repeats
            ("badger badger", "badger"),
            # and anything that's explicitly called a repeat
            ("alpha omega repeat", "alpha omega"),
            ("alpha omega N repeat", "alpha omega"),
            # subunit clause removal
            ("RNA polymerase:subunit=sigma", "RNA polymerase"),
            ("RNA polymerase:subunit=sigma factor", "RNA polymerase"),
            # subunits is no good
            ("RNA polymerase subunits", "RNA polymerase"),
            # more capitalization
            ("mce-family protein", "MCE-family protein"),
            ("o-methyltransferase", "O-methyltransferase"),
            ("pe family protein", "PE family protein"),
            ("ppe family protein", "PPE family protein"),
            ("mpt01", "MPT01"),
            # nothing truncated
            ("alpha truncated protein", "alpha protein"),
            ("alpha-truncated protein", "alpha protein"),
            # no family protein following ase
            ("alpha polymerase family protein", "alpha polymerase"),
            ("alpha polymerase protein", "alpha polymerase"),
            ("alpha kinase protein", "alpha kinase"),
            # other -ase modifiers
            ("polymerase alpha    chain", "polymerase alpha chain"),
            ("polymerase    beta chain", "polymerase beta chain"),
            ("non-ribosomal peptide synthase", "non-ribosomal peptide synthetase"),
            # transporter lifting
            ("RNA transport", "RNA transporter"),
            ("alpha transport family protein", "alpha transporter"),
            ("alpha transporter family protein", "alpha transporter"),
            ("alpha transport family", "alpha transporter"),
            ("alpha transporter family", "alpha transporter"),
            ("alpha transport protein", "alpha transporter"),
            ("alpha transporter protein", "alpha transporter"),
            ("protein transport protein sec9", "protein transporter sec9"),
            ("RNA transport protein", "RNA transporter"),
            # regulators
            ("transcriptional regulator protein", "transcriptional regulator"),
            ("two-component response regulator", "two-component system response regulator"),
            ("two-component regulator", "two-component system response regulator"),
            # type iv pili
            ("type IV pili", "type IV pili associated protein"),
            ("protease beta chain", "protease beta chain"),
            ("protease alpha chain", "protease alpha chain"),
            # major facilitator superfamily
            ("major facilitator superfamily", "major facilitator superfamily transporter"),
            # if ends in domain but does not have protein in it, switch to domain-containing protein
            ("alpha beta domain", "alpha beta domain-containing protein"),
            # Full=
            ("Full=antigen 6", "antigen 6"),
            ("full=CFP-6", "CFP-6"),
            ("RLMF_PSEPF RecName: Full=Ribosomal RNA large subunit methyltransferase F; AltName: Full=23S rRNA mA1618 methyltransferase; AltName: Full=rRNA adenine N-6-methyltransferase",
             "ribosomal RNA large subunit methyltransferase F"),
            # capitalization
            ("crispr-antigen", "CRISPR-antigen"),
            ("pts system glucose-specific eiicba component", "PTS system glucose-specific EIICBA component"),
            # range of kDa's
            ("Transcription initiation factor TFIID 23-30kDa subunit", "transcription initiation factor TFIID 23-30kDa subunit"),
            # allow an ID followed by "family" or "-like"
            ("Ergot alkaloid biosynthesis AFUA_2G17970 family", "ergot alkaloid biosynthesis AFUA_2G17970 family protein"), # note family protein at end
            ("N2227-like  protein", "N2227-like protein"),
            ("Ydr279p protein family (RNase H2 complex component)",
             "Ydr279p protein family (RNase H2 complex component)"),
            # delete two families in succession
            ("HAD-superfamily subfamily IIA hydrolase, TIGR01456, CECR5", "HAD-superfamily subfamily IIA hydrolase"),
            # allow certain quoted keywords
            ("magical \"chromo\"", "magical \"chromo\""),
            ("mysterious 'chromo' power protein", "mysterious 'chromo' power protein"),
            ("Powerful Porphyrin", "powerful porphyrin"),
            # fix weird kDa abbreviations
            ("RNA polymerases M/15 Kd subunit", "RNA polymerase M/15 kDa subunit"),
            ("NADH-ubiquinone oxidoreductase 11.6 kD subunit", "NADH-ubiquinone oxidoreductase 11.6 kDa subunit"),
            # properly fix small chain to small subunit
            ("Carbamoyl-phosphate synthase small chain, CPSase domain", "carbamoyl-phosphate synthase small chain"),
            # edge case, site motif -> site domain -> site
            ("Phospholipase D Active site motif", "phospholipase D active site-containing protein"),
            # properly handle names that would other wise have two "containing" appear in them
            ("Glycosyltransferase sugar-binding region containing DXD motif", "glycosyltransferase sugar-binding region containing DXD domain"),
            # "X, family Y" typically becomes "Y family X"...
            ("phage portal protein, alpha family", "alpha family phage portal protein"),
            ("transcriptional regulator, TetR family", "TetR family transcriptional regulator"),
            ("acetyltransferase, GNAT family", "GNAT family acetyltransferase"),
            ("Mn2+/Fe2+ transporter, NRAMP family", "NRAMP family Mn2+/Fe2+ transporter"),
            ("transposase, mutator family", "mutator family transposase"),
            # ...however, there are still cases where we want to delete X family
            # such as certain ids
            ("F420-dependent oxidoreductase, Rv2161c family", "F420-dependent oxidoreductase"),
            # some ideas for future naming improvements, our family support is limited thusfar
#			("phage tail tape measure protein, TP901 family, core region", "TP901 phage tail tape measure protein, core region"),
#			("holin, phage phi LC3 family", "??ASd/AD?ASD?ASD"),
            # test capitalization of subunit
            ("ATP synthase j chain", "ATP synthase J chain"),
            ("ATP synthase y chain", "ATP synthase Y chain"),
            ("ATP synthase beta J chain", "ATP synthase beta J chain"),
            ("ATP synthase regulatory chain", "ATP synthase regulatory chain"),
            # terminal domains and wrecked versions of same
            # chains the above test on domain-containing protein
            ("alpha omega N-terminal domain", "alpha omega domain-containing protein"),
            ("alpha omega N-term domain", "alpha omega domain-containing protein"),
            ("alpha omega C-terminal domain", "alpha omega domain-containing protein"),
            ("alpha omega C-term domain", "alpha omega domain-containing protein"),
            ("alpha omega N- domain", "alpha omega domain-containing protein"),
            ("alpha omega C- domain", "alpha omega domain-containing protein"),
            ("alpha omega, N-terminal domain", "alpha omega domain-containing protein"),
            ("alpha omega, N-term domain", "alpha omega domain-containing protein"),
            ("alpha omega, C-terminal domain", "alpha omega domain-containing protein"),
            ("alpha omega, C-term domain", "alpha omega domain-containing protein"),
            # terminus names
            ("alpha omega N-terminus protein", "alpha omega protein"),
            ("alpha omega N terminus protein", "alpha omega protein"),
            ("alpha omega C-terminus protein", "alpha omega protein"),
            ("alpha omega C terminus protein", "alpha omega protein"),
            ("alpha omega n-terminus protein", "alpha omega protein"),
            ("alpha omega n terminus protein", "alpha omega protein"),
            ("alpha omega c-terminus protein", "alpha omega protein"),
            ("alpha omega c terminus protein", "alpha omega protein"),
            # adverb removal
            ("very alpha omega", "alpha omega"),
            # no paralogous families
            ("alpha omega, paralogous family", "alpha omega"),
            # bad punctuation
            ("alpha omega /", "alpha omega"),
            # don't overcorrect capitalization
            ("Holliday junction DNA helicase RuvB", "Holliday junction DNA helicase RuvB"),
            # should never end with "protein, family"
            ("alpha omega protein, family", "alpha omega protein"),
            # should never being with family or superfamily
            ("family alpha omega protein", "alpha omega protein"),
            ("superfamily alpha omega protein", "alpha omega protein"),
            # make sure that trailing family/superfamily is properly renamed
            ("pyridoxamine 5'-phosphate oxidase family", "pyridoxamine 5'-phosphate oxidase family protein"),
            ("pyridoxamine 5'-phosphate oxidase superfamily", "pyridoxamine 5'-phosphate oxidase superfamily protein"),
            # ... but this family shouldn't be touched because it's preceded by protein
            ("universal stress protein family", "universal stress protein family"),
            # capitalize protein names
            ("D-ala adding enzyme", "D-Ala adding enzyme"),
            ("ala adding enzyme", "Ala adding enzyme"),
            # four letter words are not all curse words
            ("MerR", "MerR protein"),
            ("MerR protein", "MerR protein"),
            ("vraX", "vraX protein"),
            ("vraX protein", "vraX protein"),
            # 14-3-3
            ("14-3-3 protein", "14-3-3 family protein"),
            # adding protein
            ("lipopolysaccharide biosynthesis", "lipopolysaccharide biosynthesis protein"),
            # validate
            ("validate alpha omega protein", "alpha omega protein"),
            ("validated alpha omega protein", "alpha omega protein"),
            # unnecessary modification
            ("DNA modification methylase", "DNA methylase"),
            # unnecessary hydrolase
            ("isochorismatase hydrolase", "isochorismatase"),
            # colon separated duplicates
            ("alpha transporter:alpha transporter", "alpha transporter"),
            ("Na+:H+ antiporter", "Na+:H+ antiporter"), # should not be touched
            # no genes
            ("alpha omega gene", "alpha omega"),
            # no truncated
            ("alpha omega truncat", "alpha omega"),
            ("alpha omega truncate", "alpha omega"),
            ("alpha omega truncated", "alpha omega"),
            ("yaaB", "yaaB protein"),
            ("&gamma;-glutamyl:cysteine ligase", "gamma-glutamyl:cysteine ligase"),
            # DNA gyrase is ok when followed by subunit X
            ("DNA gyrase", DEFNAME),
            ("DNA gyrase subunit A", "DNA gyrase subunit A"),
            ("DNA gyrase subunit z", "DNA gyrase subunit Z"), # note capitalization of Z
            ("DNA gyrase subunit 3", "DNA gyrase subunit 3"),
            ("DNA gyrase A subunit", "DNA gyrase A subunit"),
            # american spelling
            ("haemolysin protein", "hemolysin protein"),
            ("haemagglutinin protein", "hemagglutinin protein"),
            # rsh/rsq id removal
            ("rsh:Rsph17029_4156 mandelate racemase/muconate lactonizing protein",
             "mandelate racemase/muconate lactonizing protein"),
            ("rsq:Rsph17025_1193 monooxygenase",
             "monooxygenase"),
            # rsp_1547 bacterioferritin-associated ferredoxin
            ("rsp_1547 bacterioferritin-associated ferredoxin",
             "bacterioferritin-associated ferredoxin"),
            # gi id removal
            ("gi|125654608|ref|YP_001033802.1| ParB-like nuclease",
             "ParB-like nuclease"),
            ("gi|125654672|ref|YP_001033866.1| virC1 gene, ATPase [Rhodobacter sphaeroides 2.4.1]",
             "virC1"),
            # make sure the poster is honest
            ("gi|118703|sp|P17820.3|DNAK_BACSU[118703] Heat shock 70 kDa protein, HSP70, dnaK [Cyanidium caldarium]",
             "hsp70-like protein"),
            ("RecName: Full=ABC TRANSPORT PROTIEN (ATP-binding-cassette)",
             "ABC transporter (ATP-binding-cassette)"),
            # make sure we don't overmatch to heat shock proteins when there's more specific info
            ("RecName: Full=Chaperone protein dnaK; AltName: Full=Heat shock protein 70; AltName: Full=Heat shock 70 kDa protein; AltName: Full=HSP70; AltName: Full=75 kDa membrane protein",
             "chaperone dnaK"),
            ("transcription factor Tfiiib component", "transcription factor TFIIIB component"),
            ("sp|P37821|1A1C_MALDO 1-aminocyclopropane-1-carboxylate synthase",
             "1-aminocyclopropane-1-carboxylate synthase"),
        ]

        testsNotAutogenerated = [
            ("SAM domain (Sterile alpha motif)", "SAM (sterile alpha motif) domain-containing protein"),
            # check capitalization
            ("Tetrapyrrole (Corrin/Porphyrin) Methylases", "tetrapyrrole (corrin/porphyrin) methylase"),
            # allow certain quoted keywords
            ("'chromo' (CHRromatin Organisation MOdifier) domain", "'chromo' (CHRromatin Organisation MOdifier) domain-containing protein"),
        ]

        testNoCommaZapping = [
            ("glutamate synthase (NADPH), homotetrameric",
             "glutamate synthase (NADPH), homotetrameric"),
            ("Aspartate carbamoyltransferase regulatory chain",
             "aspartate carbamoyltransferase regulatory chain"),
            ("hrcV: type III secretion protein, HrcV family",
             "HrcV family type III secretion protein"),
            ("fliQ_rel_III: type III secretion protein, HrpO family",
             "HrpO family type III secretion protein"),
            ("soxB: sarcosine oxidase, beta subunit family",
             "sarcosine oxidase, beta subunit"),
            ("CH482379_1", "hypothetical protein"),
            ("sp|P09832|GLTD_ECOLI Glutamate synthase [NADPH] small chain",
             "glutamate synthase [NADPH] small chain"),
            ("1-(5-phosphoribosyl)-5-[(5-phosphoribosylamino)methylideneamino] imidazole-4-carboxamide isomerase",
             "1-(5-phosphoribosyl)-5-[(5-phosphoribosylamino)methylideneamino] imidazole-4-carboxamide isomerase"),
            ("snorkle [3-methyl-2-oxobutanoate dehydrogenase [lipoamide]] monster",
             "snorkle [3-methyl-2-oxobutanoate dehydrogenase [lipoamide]] monster"),
            ("captain ([S-acetoin forming]) kangaroo",
             "captain ([S-acetoin forming]) kangaroo"),
            ("(3R)-hydroxymyristoyl-[acyl-carrier-protein] dehydratase",
             "(3R)-hydroxymyristoyl-[acyl-carrier-protein] dehydratase"),
            ("(Dimethylallyl)adenosine tRNA methylthiotransferase miaB",
             "(Dimethylallyl)adenosine tRNA methylthiotransferase miaB"),
            ("[citrate [Pro-3S]-lyase] ligase",
             "[citrate [Pro-3S]-lyase] ligase"),
            ("(R,R)-butanediol dehydrogenase",
             "(R,R)-butanediol dehydrogenase"),
            ("metalloprotease eubeli_00972",
             "metalloprotease"),
            ("asparate kinase",
             "aspartate kinase"),
            ("aluminium resistance protein",
             "aluminum resistance protein"),
            ("ethanolamine utilisation protein EutA",
             "ethanolamine utilization protein EutA"),
            ("ABC transporter ATP-binding protein spyM18_0273",
             "ABC transporter ATP-binding protein"),
            ("PTS system",
             "PTS system protein"),
            ("ABC transporter ATP-binding protein SPy_0285/M5005_Spy0242",
             "ABC transporter ATP-binding protein"),
            ("UPF0435 protein",
             "UPF0435 protein"),
        ]

        bname = genepidgin.cleaner.BioName(removeTrailingClauses=1)

        for input, desired in tests:
            answer, filteroutput = bname.cleanup(input, getOutput=1)
            yield assert_equal, answer, desired

        for input, desired in testsNotAutogenerated:
            answer, filteroutput = bname.cleanup(input, isAutogeneratedName=0, getOutput=1)
            yield assert_equal, answer, desired

        bname = genepidgin.cleaner.BioName(removeTrailingClauses=0)

        for input, desired in testNoCommaZapping:
            answer, filteroutput = bname.cleanup(input, getOutput=1)
            yield assert_equal, answer, desired


    def testFilterNop(self):
        bname = genepidgin.cleaner.BioName()

        # these names should be left untouched
        # (add to this list as we find gnarled and yet somehow beautiful names)
        goodexamples = [
            # roman numerals with numbers
            "actin III-12",
            # parens followed by dash is a valid clause
            "23S rRNA (uracil-5-)-methyltransferase RumA",
            # leading ARP2/3 is not touched
            "ARP2/3 complex 20 subunit",
            # DUF0000 is actually meaningful
            "DUF0000",
            # protein followed by certain words is valid
            "protein kinase domain-containing protein",
            "protein phosphatase c2",
            "protein disulfide isomerase NosL",
            "protein methyltransferase hemK",
            "protein export",
            # proteinase is always valid
            "proteinase R",
            # repeats of the word kinase are always valid
            "kinase kinase",
            "kinase kinase kinase",
            # protein in middle of word followed by domain is valid
            "alpha protein beta domain",
            # don't trim -3
            "transporter-3",
            # protein followed by a dash is valid
            "protein-L-isoaspartate O-methyltransferase",
            "protein-L-isoaspartate(D-aspartate) O-methyltransferase",
            "protein-S-isoprenylcysteine O-methyltransferase",
            # acceptable kDa
            "monster protein 52 kDa subunit",
            "kinesin-II 85 kDa subunit",
            "NADH-ubiquinone oxidoreductase 30.4 kDa subunit",
            # upf nop
            "UPF0187 domain membrane protein",
            # bad looking good id names
            "14-3-3 family protein ArtA",
            "14-3-3 family protein epsilon",
            # these special id-looking things are ok, see removeUnderscoreIds for exception list
            "VRR_NUC domain-containing protein",
            "PE_PGRS family protein",
            # proteinase is a good word
            "proteinase alpha",
            # gag-pol is a good word
            "gag-pol",
            # domain-containing proteins
            "SH3 domain-containing protein",
            "WD40 domain-containing protein",
            "EB1 domain-containing protein",
            "oxalyl-CoA decarboxylase",
            # preserve certain domain proteins
            "PE family protein",
            "PPE family protein",
            # transient receptor protein
            "transient receptor potential ion channel protein",
            # Uniprot blesses subunits
            "cytochrome c oxidase subunit 1",
        ]

        for desired in goodexamples:
            answer, filteroutput = bname.cleanup(desired, isAutogeneratedName=0, getOutput=1)
            yield assert_equal, answer, desired

    def testWeakNameAdjustments(self):
        # the target name in each of these test cases is "putative transporter"
        tests = [
            # simple conversions
            "similar to transporter",
            "homolog of transporter",
            "strong similarity to transporter",
            "probable transporter",
            "homolog to transporter",
            # comma conversions
            "transporter, putative",
            "putative transporter, putative",
            # suffix conversions
            "transporter-like",
            "transporter-related",
            # suffix conversions with more leading
            "alpha putative transporter-like",
            "alpha putative transporter-related",
            # multiple putatives
            "putative alpha putative transporter",
            # fragment removal
            "putative transporter [validated]",
            "putative transporter [similarity]",
            "putative transporter (fragment)",
            "putative transporter (imported)",
            # combos
            "similar to probable transporter",
            "alpha similar to transporter, putative",
            "alpha protein similar to transporter, putative",
            "alpha protein homolog of transporter-like",
            "strong similarity to alpha probable transporter-related",
            # the best name ever
            "strong similarity to alpha homolog of probable transporter-like, putative"
        ]
        desired = "putative transporter"
        bname = genepidgin.cleaner.BioName(saveWeakNames=1)
        for input in tests:
            answer, filteroutput = bname.cleanup(input, getOutput=1)
            yield assert_equal, answer, desired


    # these three tests add up to --hmp
    def testWeakNameSpecialCases(self):
        # these don't involve rearranging putative, they're just alternate bits
        tests = [
            ("putative protein", DEFNAME),
            ("unknown transporter", DEFNAME),
            ("protein of unknown function", DEFNAME),
        ]
        bname = genepidgin.cleaner.BioName(saveWeakNames=1)
        for input, desired in tests:
            answer, filteroutput = bname.cleanup(input, getOutput=1)
            yield assert_equal, answer, desired

    def testBaseNames(self):
        # broad settings
        bname = genepidgin.cleaner.BioName()
        assert_equal(bname.cleanup("predicted protein"), DEFNAME)
        assert_equal(bname.cleanup("conserved hypothetical protein"), DEFNAME)
        assert_equal(bname.cleanup("hypothetical protein"), DEFNAME)

    def testTrailingClauses(self):
        basename = "alpha omega"
        withcomma =     basename + ", trailing clause comma"
        withdash =      basename + " - trailing clause dash"
        withsemicolon = basename + "; trailing clause semicolon"

        bname = genepidgin.cleaner.BioName(removeTrailingClauses=1)
        assert_equal(bname.cleanup(withcomma),     basename)
        assert_equal(bname.cleanup(withdash),      basename)
        assert_equal(bname.cleanup(withsemicolon), basename)

        bname = genepidgin.cleaner.BioName(removeTrailingClauses=0)
        assert_equal(bname.cleanup(withcomma),     withcomma)
        assert_equal(bname.cleanup(withdash),      withdash)
        assert_equal(bname.cleanup(withsemicolon), withsemicolon)

    def testReorderFamily(self):
        # note how this combines with "X family protein" rule
        name = "transcriptional regulator, TetR family"

        bname = genepidgin.cleaner.BioName(reorderFamily=1)
        assert_equal(bname.cleanup(name), "TetR family transcriptional regulator")
        bname = genepidgin.cleaner.BioName(reorderFamily=0, removeTrailingClauses=0)
        assert_equal(bname.cleanup(name), "transcriptional regulator, TetR family protein")

    def testRankAndCmpNames(self):
        # the number value attached to some of these lousy names is a decoy
        # to make sure that we never rank crappy names on score
        namePairs = [
                 ("hypothetical protein, panda",200),
                 ("supreme overlord of known material",4),
                 ("hypothetical protein similar to vice overlord",1),
                 ("vice overlord of known material", 2),
                 ("predicted protein",0),
                 ("hypothetical protein similar to supreme overlord",3)
                 ]

        desired  = [
                 ("predicted protein", 0),
                 ("hypothetical protein, panda", 200),
                 ("hypothetical protein similar to vice overlord", 1),
                 ("hypothetical protein similar to supreme overlord", 3),
                 ("vice overlord of known material", 2),
                 ("supreme overlord of known material", 4)
                   ]

        bname = genepidgin.cleaner.BioName()

        namePairs.sort(bname.cmpNamePairs)

        for i in range(0, len(namePairs)):
            yield assert_equal, namePairs[i], desired[i]

    def testCleanupNames(self):
        # tests:
        # default file naming output
        # nop and changing one name
        testinput = os.path.join(DATA_ROOT, "testCleanupNames.txt")
        testoutput = os.path.join(DATA_ROOT, "testCleanupNames_working.txt")
        expected = os.path.join(DATA_ROOT, "testCleanupNames_expected.txt")
        try:
            genepidgin.cleaner.cleanup(inputFileName=testinput, outputFileName=testoutput, silent=1)
            self.assert_file_equals(expected, testoutput)
        finally:
            os.remove(testoutput)


    # note that this doesn't clean up the name, it just takes the part
    # that trails the semicolon and returns it
    def testKeggExtract(self):
        tests = [
            ("rsh:Rsph17029_4104  H+-transporting two-sector ATPase, gamma subunit ; K02115 F-type H+-transporting ATPase subunit gamma [EC:3.6.3.14]",
             "K02115 F-type H+-transporting ATPase subunit gamma [EC:3.6.3.14]"),
            ("rsh:Rsph17029_4176  FMN-binding negative transcriptional regulator ; K07734 transcriptional regulator",
             "K07734 transcriptional regulator"),
        ]
        for input, desired in tests:
            answer = genepidgin.cleaner.extractKEGG(input)
            yield assert_equal, answer, desired

