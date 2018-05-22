import datetime

from django.test import TestCase

from md_analysis.const import MdPrjStatus
from md_analysis.util.status_helper import StatusHelper


class NewDate(datetime.datetime):
    '''
    mock now is 2017,12,25;week 52
    '''
    @classmethod
    def now(cls, tz=None):
        return cls(2017, 12, 25)


class StatusHelperTest(TestCase):

    def setUp(self):
        datetime.datetime = NewDate

    def test_get_prj_status(self):
        # incoming case
        year = "2018"
        week = "02"
        expected_result = MdPrjStatus.INCOMING
        test_result = StatusHelper.get_prj_status(year, week)
        self.assertEqual(expected_result, test_result)

        # incoming over 4 weeks case
        year = "2018"
        week = "09"
        expected_result = None
        test_result = StatusHelper.get_prj_status(year, week)
        self.assertEqual(expected_result, test_result)

        # new case
        year = "2017"
        week = "52"
        expected_result = MdPrjStatus.NEW
        test_result = StatusHelper.get_prj_status(year, week)
        self.assertEqual(expected_result, test_result)

        # ongoing case
        year = "2017"
        week = "01"
        expected_result = MdPrjStatus.ONGOING
        test_result = StatusHelper.get_prj_status(year, week)
        self.assertEqual(expected_result, test_result)

        # null case
        year = ""
        week = ""
        expected_result = None
        test_result = StatusHelper.get_prj_status(year, week)
        self.assertEqual(expected_result, test_result)

        # different year but incoming within 4 weeks
        year = 2018
        week = 2
        expected_result = MdPrjStatus.INCOMING
        test_result = StatusHelper.get_prj_status(year, week)
        self.assertEqual(expected_result, test_result)
