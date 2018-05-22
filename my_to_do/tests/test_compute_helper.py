import datetime

from django.test import TestCase

from my_to_do.util.compute_helper import ComputeHelper


class ComputeHelperTest(TestCase):

    def setUp(self):
        pass

    def test_update_none_or_empty_to_zero(self):
        # test if value is none, should be 0
        test_value = None
        expected_result = 0
        test_result = ComputeHelper.update_none_or_empty_to_zero(test_value)
        self.assertEqual(test_result, expected_result)

        # test if value is empty, should be 0
        test_value = ""
        expected_result = 0
        test_result = ComputeHelper.update_none_or_empty_to_zero(test_value)
        self.assertEqual(test_result, expected_result)

        # test if value has value, should be the value
        test_value = 3
        expected_result = 3
        test_result = ComputeHelper.update_none_or_empty_to_zero(test_value)
        self.assertEqual(test_result, expected_result)

    def test_check_list_subset(self):
        # check_list is more than valid_list
        check_list = ['A', 'C', 'B']
        valid_list = ['A', 'B']
        expected_result = True
        test_result = ComputeHelper.check_list_subset(check_list, valid_list)
        self.assertEqual(test_result, expected_result)

        # check_list is not all contains valid_list
        check_list = ['A', 'C']
        valid_list = ['A', 'B']
        expected_result = False
        test_result = ComputeHelper.check_list_subset(check_list, valid_list)
        self.assertEqual(test_result, expected_result)

        # check_list is the same as valid_list
        check_list = ['A', 'B']
        valid_list = ['A', 'B']
        expected_result = True
        test_result = ComputeHelper.check_list_subset(check_list, valid_list)
        self.assertEqual(test_result, expected_result)

        # check_list is null
        check_list = []
        valid_list = ['A', 'B']
        expected_result = False
        test_result = ComputeHelper.check_list_subset(check_list, valid_list)
        self.assertEqual(test_result, expected_result)
