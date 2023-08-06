#!/bin/env python

from nose.tools import *

import subprocess

# http://achinghead.com/nosetests-generators-descriptions.html
class RunInBlob:
    def __call__(self, x, blob):
        self.description = 'test membership with %s' % n
        assert x in blob, '%s failed'

class TestCLI(object):

    def test_help_messages(self):
        cmd = "python ./genepidgin/cmdline.py"
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        output, ret = process.communicate()
        commands = ["cleaner", "compare", "select"]
        for command in commands:
            yield RunInBlob(), command, output

    def test_help_select(self):
        cmd = "python ./genepidgin/cmdline.py select"
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        output, ret = process.communicate()
        if "select" not in output:
            raise Exception, "Could not find 'pidgin select' in select help output"

    def test_help_compare(self):
        cmd = "python ./genepidgin/cmdline.py compare"
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        output, ret = process.communicate()
        if "compare" not in output:
            raise Exception, "Could not find 'pidgin compare' in compare help output"

    def test_help_cleaner(self):
        # map to same file
        cmd = "python ./genepidgin/cmdline.py cleaner"
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        outputCleanup, ret = process.communicate()
        if "cleanup" not in outputCleanup:
            raise Exception, "Could not find 'cleaner' in cleaner help output"

