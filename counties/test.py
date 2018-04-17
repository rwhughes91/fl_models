import unittest
import os
import pandas as pd


from .setup import countiesByPlatform

class TestConstruction(unittest.TestCase):

    def setUp(self):
        self.s = countiesByPlatform

    def test_empty(self):
        self.assertTrue(self.s is not None)

    def test_type(self):
        self.assertTrue(type(self.s) == dict)
        self.assertTrue(type(self.s) != list)
        self.assertFalse(type(self.s) == int)
        self.assertFalse(type(self.s) != dict)

    def test_parts(self):
        self.assertTrue(len(self.s.keys()) == 4)
        self.assertFalse(len(self.s.keys() != 6))
        self.assertTrue("GrantStreet" in self.s.keys())
        self.assertTrue("RealAuction" in self.s.keys())
        self.assertTrue("WFBS" in self.s.keys())
        self.assertTrue("DT" in self.s.keys())

    def test_values(self):
        self.assertTrue(len(self.s['RealAuction']) == 17)
        self.assertTrue(len(self.s['GrantStreet']) == 24)
        self.assertTrue(len(self.s['DT']) == 11)
        self.assertTrue(len(self.s['WFBS']) == 4)

    def spot_check(self):
        self.assertTrue('Levy' in self.s['WFBS'])
        self.assertTrue('Duval' in self.s['RealAuction'])
        self.assertTrue('Gulf' in self.s['DT'])
        self.assertTrue('Miami' in self.s['GrantStreet'])