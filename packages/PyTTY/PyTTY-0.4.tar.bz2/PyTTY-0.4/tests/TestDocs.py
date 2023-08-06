#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''TestDocs for PyTTY

    This test suite scans PyTTY's documentation for code examples and runs
    them checking to ensure the output is as expected.

    See http://docs.python.org/library/doctest.html for details.
'''

__credits__ = '''Copyright (C) 2010,2011,2012 Arc Riley

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with this program; if not, see http://www.gnu.org/licenses
'''


import doctest
import unittest2 as unittest
import pytty


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(
        module = pytty,
        globs = {
            'pytty' : pytty,  # So examples don't need "import pytty"
        },
    ))
    return tests


if __name__ == '__main__':
    unittest.main()
