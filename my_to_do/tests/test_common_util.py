import datetime

from django.test import TestCase

from my_to_do.util.common_util import binary_search


class CommonUtilTest(TestCase):

    def setUp(self):
        pass

    def test_binary_search(self):
        # test if value exists
        ary = ["ALPS00022972",
               "ALPS00022982",
               "ALPS00026740",
               "ALPS00028049",
               "ALPS00028172",
               "ALPS00028254",
               "ALPS00029991",
               "ALPS00030192",
               "ALPS00030787",
               "ALPS00031045",
               "ALPS00033204", ]
        target = "ALPS00033204"
        test_result = binary_search(ary, target)
        
        self.assertEqual(test_result, ary.index(target))
        
        # test if value doesn't exist
        target = "ALPS00033299"
        test_result = binary_search(ary, target)
        self.assertEqual(test_result, -1)
