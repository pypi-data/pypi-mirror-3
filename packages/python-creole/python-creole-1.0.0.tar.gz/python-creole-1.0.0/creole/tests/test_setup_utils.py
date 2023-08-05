#!/usr/bin/env python
# coding: utf-8

"""
    unittest for setup_utils
    ~~~~~~~~~~~~~~~~~~~~~~~~
    
    https://code.google.com/p/python-creole/wiki/UseInSetup

    :copyleft: 2011 by python-creole team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import division, absolute_import, print_function, unicode_literals

import unittest
import os

import creole
from creole.setup_utils import get_long_description
from creole.tests.utils.base_unittest import BaseCreoleTest


CREOLE_PACKAGE_ROOT = os.path.abspath(os.path.join(os.path.dirname(creole.__file__), ".."))


class SetupUtilsTests(BaseCreoleTest):
    def test_creole_package_path(self):
        self.assertTrue(
            os.path.isdir(CREOLE_PACKAGE_ROOT),
            "CREOLE_PACKAGE_ROOT %r is not a existing direcotry!" % CREOLE_PACKAGE_ROOT
        )
        filepath = os.path.join(CREOLE_PACKAGE_ROOT, "README.creole")
        self.assertTrue(
            os.path.isfile(filepath),
            "README file %r not found!" % filepath
        )

    def test_get_long_description_without_raise_errors(self):
        long_description = get_long_description(CREOLE_PACKAGE_ROOT, raise_errors=False)
        self.assertIn("=====\nabout\n=====\n\n", long_description)
        # Test created ReSt code
        from creole.rest2html.clean_writer import rest2html
        html = rest2html(long_description)
        self.assertIn("<h1>about</h1>\n", html)

    def test_get_long_description_with_raise_errors(self):
        long_description = get_long_description(CREOLE_PACKAGE_ROOT, raise_errors=True)
        self.assertIn("=====\nabout\n=====\n\n", long_description)

    def test_wrong_path_without_raise_errors(self):
        self.assertEqual(
            get_long_description("wrong/path", raise_errors=False).replace("u'", "'"),
            "[Error: [Errno 2] No such file or directory: 'wrong/path/README.creole']\n"
        )

    def test_wrong_path_with_raise_errors(self):
        self.assertRaises(IOError, get_long_description, "wrong/path", raise_errors=True)


if __name__ == '__main__':
    unittest.main()
