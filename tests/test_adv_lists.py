import unittest
from Florida.adv_methods import homesteadmodifier
from numpy import nan
import math

test_array = ["YES", "NO", "yes", "no", "HX",
              "hx", "TRUE", "True", "true",
              True, False, "False", "FALSE",
              "Pickle", 564648, 1, 0, -69,
              None, nan
              ]


class TestConstruction(unittest.TestCase):

    def setUp(self):
        self.array = test_array
        self.test_func = homesteadmodifier

    def test_empty(self):
        self.assertTrue(self.test_func([]) is not None)
        self.assertFalse(self.test_func([]) is None)
        self.assertEqual(self.test_func([]), [])
        self.assertFalse(id(self.test_func([])) is id([]))

    def test_fill(self):
        self.assertTrue(self.test_func(self.array) is not [])
        self.assertFalse(self.test_func(self.array) is [])
        self.assertEqual(len(self.test_func(self.array)), 20)

    '''testing as single items in an array'''

    def test_single_values_basic(self):
        self.assertEqual(self.test_func([self.array[0]]), ["Yes"])
        self.assertEqual(self.test_func([self.array[1]]), ["No"])
        self.assertEqual(self.test_func([self.array[2]]), ["Yes"])
        self.assertEqual(self.test_func([self.array[3]]), ["No"])
        self.assertEqual(self.test_func([self.array[4]]), ["Yes"])
        self.assertEqual(self.test_func([self.array[5]]), ["Yes"])
        self.assertEqual(self.test_func([self.array[13]]), ["No"])

    def test_single_values_bools(self):
        self.assertEqual(self.test_func([self.array[6]]), ["Yes"])
        self.assertEqual(self.test_func([self.array[7]]), ["Yes"])
        self.assertEqual(self.test_func([self.array[8]]), ["Yes"])
        self.assertEqual(self.test_func([self.array[9]]), ["Yes"])
        self.assertEqual(self.test_func([self.array[10]]), ["No"])
        self.assertEqual(self.test_func([self.array[11]]), ["No"])
        self.assertEqual(self.test_func([self.array[12]]), ["No"])

    def test_single_values_numbers(self):
        self.assertEqual(self.test_func([self.array[14]]), ["Yes"])
        self.assertEqual(self.test_func([self.array[15]]), ["Yes"])
        self.assertEqual(self.test_func([self.array[16]]), ["No"])
        self.assertEqual(self.test_func([self.array[17]]), ["No"])

    def test_single_values_blanks(self):
        self.assertEqual(self.test_func([self.array[18]]), ["Yes"])
        self.assertEqual(self.test_func([self.array[19]]), ["Yes"])

    '''testing as an array'''

    def test_values_basic_strings(self):
        self.assertTrue(self.test_func(self.array)[0] is "Yes")
        self.assertEqual(self.test_func(self.array)[1], "No")
        self.assertEqual(self.test_func(self.array)[2], "Yes")
        self.assertEqual(self.test_func(self.array)[3], "No")
        self.assertEqual(self.test_func(self.array)[4], "Yes")
        self.assertEqual(self.test_func(self.array)[5], "Yes")
        self.assertEqual(self.test_func(self.array)[6], "Yes")
        self.assertEqual(self.test_func(self.array)[7], "Yes")
        self.assertEqual(self.test_func(self.array)[8], "Yes")
        self.assertEqual(self.test_func(self.array)[11], "No")
        self.assertEqual(self.test_func(self.array)[12], "No")
        self.assertEqual(self.test_func(self.array)[13], "No")

    def test_values_booleans(self):
        self.assertEqual(self.test_func(self.array)[9], "Yes")
        self.assertEqual(self.test_func(self.array)[10], "No")

    def test_values_numbers(self):
        self.assertEqual(self.test_func(self.array)[14], "Yes")
        self.assertEqual(self.test_func(self.array)[15], "Yes")
        self.assertEqual(self.test_func(self.array)[16], "No")
        self.assertEqual(self.test_func(self.array)[17], "No")

    def test_values_empty_values(self):
        self.assertEqual(self.test_func(self.array)[18], "Yes")
        self.assertEqual(self.test_func(self.array)[19], "Yes")


if __name__ == "__main__":
    unittest.main()
