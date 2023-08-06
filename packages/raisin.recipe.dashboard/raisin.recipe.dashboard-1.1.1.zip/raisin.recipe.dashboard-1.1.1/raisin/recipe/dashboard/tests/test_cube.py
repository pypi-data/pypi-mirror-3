"""
Test for cube.py
"""

import unittest
import sqlite3
from pkg_resources import get_provider

from raisin.recipe.dashboard.cube import Cube

PROVIDER = get_provider('raisin.recipe.dashboard')
DATABASE = PROVIDER.get_resource_filename("", 'tests/workspace/database.db')


class CubeTests(unittest.TestCase):
    """
    Tests for the Cube class
    """

    def test_cube(self):
        """
        Fill the cube with some empty values and call all methods once.
        """
        accessions = {'rows': ['cell'],
                      'cols': ['rnaExtract'],
                      'dbconn': sqlite3.connect(DATABASE)
                      }
        cube = Cube(accessions, "experiments")
        self.failUnless(cube.get_rows() == ['cell'])
        self.failUnless(cube.get_cols() == ['rnaExtract'])
        self.failUnlessRaises(KeyError, cube.get_dim_values, None)
        self.failUnless(cube.get_row_values() == [(u'NHEK',)])
        self.failUnless(list(cube.get_col_product()) == [(u'LONGPOLYA',)])


def test_suite():
    """
    Run test suite
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
