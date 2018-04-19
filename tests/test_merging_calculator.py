import unittest
from Florida.flwrangler import FloridaWrangler
import pandas as pd

advfilelocation = r"C:\Users\rhughes\Documents\Al test fl.xlsx"
tsrfilelocation = r"C:\Users\rhughes\Documents\al tsr.xlsx"
lumfilelocation = r"C:\Users\rhughes\Documents\Alachua Lumentum 2017.xlsx"

class TestConstruction_Merging_Calc(unittest.TestCase):
    def setUp(self):
        f = FloridaWrangler("Alachua", advfilelocation, tsrfilelocation, lumfilelocation)
        self.f = f

    def test_set_up(self):
        self.assertTrue(self.f.county == "Alachua")
        self.assertTrue(self.f._county == "Alachua")

        self.assertTrue(self.f.platform == "GrantStreet")
        self.assertTrue(self.f._platform == "GrantStreet")

        self.assertTrue(type(self.f.fl_model) == pd.DataFrame)
        self.assertTrue(type(self.f._fl_model) == pd.DataFrame)

    def test_calc(self):
        self.assertTrue(type(self.f.merging_calc()) == dict)

if __name__ == "__main__":
    unittest.main()