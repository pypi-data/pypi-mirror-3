#!/bin/env python

import sys, os
sys.path.insert(0, os.path.join(sys.path.pop(0), ".."))

import sys
req_version = (2,5)
cur_version = sys.version_info
if not (cur_version >= req_version):
    raise "genepidgin requires python 2.5 or greater. Please consider upgrading: www.python.org"

from genepidgin import version

import argparse

def compare(reference, query=None):
    """
    statistical analysis of one set of names versus another

    :param: reference: absolute path to file with names serving as refernce
    :param: query: absolute path to file with names to be compared against reference
    """

    query = [query]

    import genepidgin.scorer
    genepidgin.scorer.compareFiles(reference, query)


def select(output="./pidgin.out", refs=None, name_files=[]):
    """
    given a series of files containing names from different sources, select
    the most informative, uniprot-compliant name
    
    :param: output: absolute path to file where output will be stored
    :param: refs: XXX 
    :param: name_files: absolute path to files containing names to be used as input
    """
    if not name_files:
        print "Need more files to select from."
        sys.exit(1)

    if refs:
        refs = refs.split(",")

    import genepidgin.selector
    genepidgin.selector.select(name_files, output, refs)


def cleaner(input=None,
            output=None,
            default=False,
            hmp=False,
            silent=False):
    """
    take homology-derived name from anywhere, get uniprot-compatible name,
    or no name at all

    :param: input_file: absolute path to file containing names to be cleaned
    :param: output_file: absolute path to file to receive the output
    :param: populate_default: when true, populate useless names with default name instead of blank
    :param: hmp: custom behavior for HMP project
    :param: silent: no output to terminal
    """
    import genepidgin.cleaner
    genepidgin.cleaner.cleanup(inputFileName=input,
                               outputFileName=output,
                               populate_default=default,
                               retain=hmp,
                               silent=silent)

DESC = """genepidgin is a suite tools to assist in homology-based naming and analysis"""

def main():

    # create the top-level parser
    parser = argparse.ArgumentParser(version=version,
                                     description=DESC)

    subparsers = parser.add_subparsers(help='commands')

    cleaner_parser = subparsers.add_parser('cleaner',
                                           help='clean a file containing names')

    cleaner_parser.add_argument('input',
                                action='store',
                                help='filename with names to clean')
    cleaner_parser.add_argument('output',
                                action='store',
                                default=None,
                                help='output file')
    cleaner_parser.add_argument('--silent', '-s',
                                action='store_true',
                                default=False,
                                help='display etymology to stdout during compute')
    cleaner_parser.add_argument('--default', '-d',
                                action='store_true',
                                default=False,
                                help='return default name "hypothetical project" when names filter to nothing, else return emptry string')
    cleaner_parser.set_defaults(func=cleaner)

    compare_parser = subparsers.add_parser('compare', help='compare names in multiple files')
    compare_parser.add_argument('reference',
                                action='store',
                                help='file with names to use as a base for comparison')
    compare_parser.add_argument('query',
                                default=None,
                                action='store',
                                help='file with names to compare to reference names')
    compare_parser.set_defaults(func=compare)

    select_parser = subparsers.add_parser('select', help='choose name from multiple sources')
    select_parser.add_argument('--output',
                               action='store',
                               default="./pidgin.out",
                               help='file to store execution results in')
    select_parser.add_argument('--refs',
                               default=None,
                               action='store',
                               help='comma-separated list of files with name keys for alignments (used with .blastm8 only)')
    select_parser.add_argument('name_files',
                               default=[],
                               nargs='+',
                               help='files containing names')
    select_parser.set_defaults(func=select)

    args = parser.parse_args()

    # omg !@#$%^& argparse
    command = args.func
    arguments = vars(args)
    del arguments['func']
    command(**arguments)

if __name__ == '__main__':
    main()
