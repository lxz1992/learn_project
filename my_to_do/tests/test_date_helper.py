import datetime

from django.test import TestCase

from my_to_do.util.date_helper import DateHelper


class NewDate(datetime.datetime):
    '''
    mock now is 2017,12,25 christmas
    '''
    @classmethod
    def now(cls, tz=None):
        return cls(2017, 12, 25)


class DateHelperTest(TestCase):

    def setUp(self):
        datetime.datetime = NewDate

    def test_calculate_mtk_week(self):
        expected_year = 2017
        expected_week = 53
        time = datetime.datetime(2017, 12, 31)

        (test_year, test_week) = DateHelper.calculate_mtk_week(time)
        self.assertEqual(test_year, expected_year)
        self.assertEqual(test_week, expected_week)

        # No input
        expected_year = None
        expected_week = None
        time = None

        (test_year, test_week) = DateHelper.calculate_mtk_week(time)
        self.assertEqual(test_year, expected_year)
        self.assertEqual(test_week, expected_week)

        # Error datetime format input
        expected_year = None
        expected_week = None
        time = '2017-13-13'

        (test_year, test_week) = DateHelper.calculate_mtk_week(time)
        self.assertEqual(test_year, expected_year)
        self.assertEqual(test_week, expected_week)

    def test_get_days_from_specific_date(self):
        submit_date = datetime.datetime(2017, 12, 10)
        expected_reuslt = (datetime.datetime.now().date() -
                           submit_date.date()).days
        test_result = DateHelper.get_days_from_specific_date(submit_date)
        self.assertEqual(test_result, expected_reuslt)

        expected_reuslt = 0
        test_result = DateHelper.get_days_from_specific_date(None)
        self.assertEqual(test_result, expected_reuslt)

        test_result = DateHelper.get_days_from_specific_date("")
        self.assertEqual(test_result, expected_reuslt)

    def test_is_will_kickoff_prj_in_one_mon(self):
        start_date = datetime.datetime(2018, 1, 1)
        expected_result = True
        test_result = DateHelper.is_will_kickoff_prj_in_one_mon(start_date)
        self.assertEqual(test_result, expected_result)

        start_date = datetime.datetime(2019, 1, 1)
        expected_result = False
        test_result = DateHelper.is_will_kickoff_prj_in_one_mon(start_date)
        self.assertEqual(test_result, expected_result)

        start_date = datetime.datetime(2017, 1, 1)
        expected_result = False
        test_result = DateHelper.is_will_kickoff_prj_in_one_mon(start_date)
        self.assertEqual(test_result, expected_result)

    def test_get_year_datetime_for_query(self):
        # with year interval
        from_year = "2014"
        to_year = "2017"
        expected_from_year = datetime.datetime(int(from_year), 1, 1)
        expected_to_year = datetime.datetime(int(to_year), 12, 31, 23, 59, 59)
        (test_from_year, test_to_year) = DateHelper.get_year_datetime_for_query(
            from_year, to_year)

        self.assertEqual(expected_from_year, test_from_year)
        self.assertEqual(expected_to_year, test_to_year)

        # same year, should return that year only in list
        from_year = 2014
        to_year = 2014
        expected_from_year = datetime.datetime(int(from_year), 1, 1)
        expected_to_year = datetime.datetime(int(to_year), 12, 31, 23, 59, 59)
        (test_from_year, test_to_year) = DateHelper.get_year_datetime_for_query(
            from_year, to_year)

        self.assertEqual(expected_from_year, test_from_year)
        self.assertEqual(expected_to_year, test_to_year)

        # not valid input or null, should return []
        from_year = ""
        to_year = 2014
        expected_from_year = None
        expected_to_year = None
        (test_from_year, test_to_year) = DateHelper.get_year_datetime_for_query(
            from_year, to_year)

        self.assertEqual(expected_from_year, test_from_year)
        self.assertEqual(expected_to_year, test_to_year)

        # no input, should return []
        from_year = None
        to_year = None
        expected_from_year = None
        expected_to_year = None
        (test_from_year, test_to_year) = DateHelper.get_year_datetime_for_query(
            from_year, to_year)

        self.assertEqual(expected_from_year, test_from_year)
        self.assertEqual(expected_to_year, test_to_year)

        # to_year is smaller that from_year, should return []
        from_year = 2019
        to_year = 2017
        expected_from_year = None
        expected_to_year = None
        (test_from_year, test_to_year) = DateHelper.get_year_datetime_for_query(
            from_year, to_year)

        self.assertEqual(expected_from_year, test_from_year)
        self.assertEqual(expected_to_year, test_to_year)

    def test_get_current_time_str(self):
        expected_result = "2017-12-25 00:00:00"
        test_result = DateHelper.get_current_time_str()
        self.assertEqual(expected_result, test_result)
