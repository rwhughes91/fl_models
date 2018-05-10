import unittest
from Florida.adv_methods import homesteadmodifier
from numpy import nan
import pandas as pd
import math


standard_answer = ["Yes"]*4 + ["No"]*6
standard_answer_2 = ["Yes"]*4 + ["No"]*6 + ["Yes"]*2

test_array = ["YES", "NO", "yes", "no", "HX",
              "hx", "TRUE", "True", "true",
              True, False, "False", "FALSE",
              "Pickle", 564648, 1, 0, -69,
              None, nan
              ]

test_array_hx = ["Hx", "hx", "HX", "hX", nan, nan, nan, nan, "Hx"]
test_array_hx_2 = ['Hx']*4 + [nan]*6
test_array_bools = [True]*4 + [False]*6
test_array_y_and_n = ['y']*4 + ['n']*6
test_array_yes_and_no = ['Yes']*4 + ['No']*6
test_array_nums = [456]*4 + [0]*6
test_array_nums_2 = [4]*2 + [3]*2 + [nan]*2



class TestConstruction_Homestead(unittest.TestCase):

    def setUp(self):
        self.array = pd.Series(test_array)
        self.test_func = homesteadmodifier
        self.array_hx = test_array_hx
        self.array_hx_2 = pd.Series(test_array_hx_2)
        self.array_bools = pd.Series(test_array_bools)
        self.array_y_and_n = pd.Series(test_array_y_and_n)
        self.array_yes_and_no = pd.Series(test_array_yes_and_no)
        self.array_nums = pd.Series(test_array_nums)

        self.array_hx_adv = pd.Series(test_array_hx + [nan]*2)
        self.array_hx_2_adv = pd.Series(test_array_hx_2 + [nan] * 2)

        self.array_bools_adv = pd.Series(test_array_bools + [nan] * 2)
        self.array_y_and_n_adv = pd.Series(test_array_y_and_n + [nan] * 2)
        self.array_yes_and_no_adv = pd.Series(test_array_yes_and_no + [nan] * 2)
        self.array_nums_adv = pd.Series(test_array_nums + [nan]*2)

    def test_empty(self):
        self.assertTrue(self.test_func(pd.Series([])) is not None)
        self.assertFalse(self.test_func(pd.Series([])) is None)
        self.assertEqual(self.test_func(pd.Series([])), [])
        self.assertFalse(id(self.test_func(pd.Series([]))) is id([]))

    def test_fill(self):
        self.assertTrue(self.test_func(self.array) is not [])
        self.assertFalse(self.test_func(self.array) is [])
        self.assertEqual(len(self.test_func(self.array)), len(self.array))

    '''testing as single items in an array'''

    def test_single_values_basic(self):
        self.assertEqual(self.test_func(pd.Series(self.array[0:6]))[0], "Yes")
        self.assertEqual(self.test_func(pd.Series(self.array[0:6]))[1], "No")
        self.assertEqual(self.test_func(pd.Series(self.array[0:6]))[2], "Yes")
        self.assertEqual(self.test_func(pd.Series(self.array[0:6]))[3], "No")
        self.assertEqual(self.test_func(pd.Series(self.array[0:6]))[4], "Yes")
        self.assertEqual(self.test_func(pd.Series(self.array[0:6]))[5], "Yes")

    def test_single_values_bools(self):
        self.assertEqual(self.test_func(pd.Series(self.array[6:13]))[0], "Yes")
        self.assertEqual(self.test_func(pd.Series(self.array[6:13]))[1], "Yes")
        self.assertEqual(self.test_func(pd.Series(self.array[6:13]))[2], "Yes")
        self.assertEqual(self.test_func(pd.Series(self.array[6:13]))[3], "Yes")
        self.assertEqual(self.test_func(pd.Series(self.array[6:13]))[4], "No")
        self.assertEqual(self.test_func(pd.Series(self.array[6:13]))[5], "No")
        self.assertEqual(self.test_func(pd.Series(self.array[6:13]))[6], "No")
        self.assertEqual(self.test_func(pd.Series(self.array[6:14]))[7], "No")

    def test_single_values_numbers(self):
        self.assertEqual(self.test_func(pd.Series(self.array[14:18]))[0], "Yes")
        self.assertEqual(self.test_func(pd.Series(self.array[14:18]))[1], "Yes")
        self.assertEqual(self.test_func(pd.Series(self.array[14:18]))[2], "No")
        self.assertEqual(self.test_func(pd.Series(self.array[14:18]))[3], "No")

    def test_single_values_blanks(self):
        self.assertEqual(self.test_func(pd.Series(self.array[16:20]))[2], "Yes")
        self.assertEqual(self.test_func(pd.Series(self.array[16:20]))[3], "Yes")

    def test_hx_and_blanks(self):
        self.assertEqual(self.test_func(pd.Series(self.array_hx)), ["Yes", "Yes", "Yes", "Yes",
                                                                    "No", "No", "No", "No",
                                                                    "Yes"])
        self.assertEqual(self.test_func(self.array_hx_2), standard_answer)


    def test_array_bools(self):
        self.assertEqual(self.test_func(self.array_bools), standard_answer)
        self.assertEqual(self.test_func(self.array_bools_adv), standard_answer_2)

    def test_array_yes_and_no(self):
        self.assertEqual(self.test_func(self.array_y_and_n), standard_answer)
        self.assertEqual(self.test_func(self.array_yes_and_no), standard_answer)

        self.assertEqual(self.test_func(self.array_y_and_n_adv), standard_answer_2)
        self.assertEqual(self.test_func(self.array_yes_and_no_adv), standard_answer_2)

    def test_nums(self):
        self.assertEqual(self.test_func(self.array_nums), standard_answer)
        self.assertEqual(self.test_func(self.array_nums_adv), standard_answer_2)

    '''testing as an array'''

    @unittest.skip('skipping')
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

    @unittest.skip('skipping')
    def test_values_booleans(self):
        self.assertEqual(self.test_func(self.array)[9], "Yes")
        self.assertEqual(self.test_func(self.array)[10], "No")

    @unittest.skip('skipping')
    def test_values_numbers(self):
        self.assertEqual(self.test_func(self.array)[14], "Yes")
        self.assertEqual(self.test_func(self.array)[15], "Yes")
        self.assertEqual(self.test_func(self.array)[16], "No")
        self.assertEqual(self.test_func(self.array)[17], "No")

    @unittest.skip('skipping')
    def test_values_empty_values(self):
        self.assertEqual(self.test_func(self.array)[18], "Yes")
        self.assertEqual(self.test_func(self.array)[19], "Yes")


if __name__ == "__main__":
    unittest.main()
