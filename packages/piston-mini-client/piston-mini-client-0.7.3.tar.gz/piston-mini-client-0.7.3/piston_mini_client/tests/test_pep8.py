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

    def test_all_code(self):
        pep8style = pep8.StyleGuide(
            counters=defaultdict(int),
            doctest='',
            exclude=self.exclude,
            filename=['*.py'],
            ignore=[],
            messages={},
            repeat=True,
            select=[],
            show_pep8=False,
            show_source=False,
            max_line_length=79,
            quiet=0,
            statistics=False,
            testsuite='',
            verbose=0,
        )

        for package in self.packages:
            pep8style.input_dir(os.path.dirname(package.__file__))
        self.assertEqual(pep8style.options.report.total_errors, 0)


if __name__ == "__main__":
    unittest.main()
