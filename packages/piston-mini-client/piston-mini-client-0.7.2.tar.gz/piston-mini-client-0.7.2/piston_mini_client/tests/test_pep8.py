# -*- coding: utf-8 -*-
# Copyright 2010-2012 Canonical Ltd.  This software is licensed under the
# GNU Lesser General Public License version 3 (see the file LICENSE).

import os
import pep8
import unittest
from collections import defaultdict

import piston_mini_client


class PackagePep8TestCase(unittest.TestCase):
    maxDiff = None
    packages = [piston_mini_client]
    exclude = ['socks.py']  # Leave 3rd party dep. alone.

    def message(self, text):
        self.errors.append(text)

    def setUp(self):
        self.errors = []

        class Options(object):
            exclude = self.exclude
            filename = ['*.py']
            testsuite = ''
            doctest = ''
            counters = defaultdict(int)
            messages = {}
            verbose = 0
            quiet = 0
            repeat = True
            show_source = False
            show_pep8 = False
            select = []
            ignore = []
            max_line_length = 79
        pep8.options = Options()
        pep8.message = self.message
        Options.physical_checks = pep8.find_checks('physical_line')
        Options.logical_checks = pep8.find_checks('logical_line')

    def test_all_code(self):
        for package in self.packages:
            pep8.input_dir(os.path.dirname(package.__file__))
        self.assertEqual([], self.errors)

if __name__ == "__main__":
    unittest.main()
