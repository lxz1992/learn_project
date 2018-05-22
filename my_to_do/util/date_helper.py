from datetime import timedelta
import datetime
import time

from django.utils import timezone
from pytz import tzinfo
import pytz

from cr_review_sys.errors import DateTimeFormatInvalid


class DateHelper(object):

    @staticmethod
    def calculate_mtk_week(time):
        '''
        Get MTK week for now,
        Return type is int or None
        '''
        try:
            if time:
                temp_result = time.isocalendar()
                now_year = temp_result[0]
                final_week = temp_result[1]
                return (now_year, final_week + 1) if temp_result[2] == 7 else (now_year, final_week)
            else:
                return (None, None)
        except Exception:
            return (None, None)

    @staticmethod
    def get_days_from_specific_date(submit_date):
        '''
        Calculate day intervals between now and particular date, ex. submit date/resolved date, etc,
        Return type is int
        (add if check to in case of sync data exception from WITS(CQ)
        '''
        return (datetime.datetime.now().date() - submit_date.date()).days if submit_date else 0

    @staticmethod
    def is_will_kickoff_prj_in_one_mon(start_date):
        '''
        Calculate start date with now to check whether this prj belongs to will kick off prj or not
        Return boolean, True is the prj will kick off in one month (31 days)
        '''
        day_interval = (start_date.date() -
                        datetime.datetime.now().date()).days
        return True if 0 < day_interval < 32 else False

    @staticmethod
    def get_year_datetime_for_query(from_year, to_year):
        '''
        Transfer year to datetime for query condition,
        Ex. From year: 2014, To year: 2017,
            return result will be
                from_datetime = datetime.datetime(2014, 1, 1, 00, 00, 00)
                to_datetime = datetime.datetime(2017, 12, 31, 23, 59, 59)
        Return (from_datetime, to_datetime)
        '''
        from_datetime = None
        to_datetime = None

        if not(from_year and to_year) or from_year > to_year:
            return (from_datetime, to_datetime)
        int_from_year = int(from_year)
        int_to_year = int(to_year)

        from_datetime = datetime.datetime(int_from_year, 1, 1)
        to_datetime = datetime.datetime(int_to_year, 12, 31, 23, 59, 59)

        return (from_datetime, to_datetime)

    @staticmethod
    def get_new_sync_job_id(db):
        new_sync_job_id = db + time.strftime("%Y%m%d%H%M%S")
        return new_sync_job_id

    @staticmethod
    def get_local_time(time):
        local_time = None
        if time:
            local_time = timezone.template_localtime(time)
            return local_time
        return time

    @staticmethod
    def get_current_time_str():
        cur_time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return cur_time_str

    @staticmethod
    def get_gmt_for_input_time(input_time, tz=None):
        '''
        transfer str to datetime with timezone
        str format: %Y-%m-%d %H:%M:%S
        default is use GMT-8, setup tz if needed
        '''
        result = None
        tz = tz if tz else "Etc/GMT-8"
        tzinfo = pytz.timezone(tz)

        try:
            result = datetime.datetime.strptime(
                input_time, "%Y-%m-%d %H:%M:%S").replace(tzinfo=tzinfo)
        except Exception:
            raise DateTimeFormatInvalid()

        return result

    @staticmethod
    def get_localtime_from_db(db_time, tz=None, str_format=None):
        '''
        transfer db datetime to str
        str_format could define format, default is "%Y-%m-%d %H:%M:%S"
        '''
        result = None
        str_format = str_format if str_format else "%Y-%m-%d %H:%M:%S"
        loca_time_delta = timedelta(hours=8)
        new_time = db_time + loca_time_delta

        try:
            result = new_time.strftime(str_format)
        except Exception:
            raise Exception()

        return result

    @staticmethod
    def get_today(str_format=None):
        result = None
        str_format = str_format if str_format else "%Y%m%d"

        try:
            result = datetime.datetime.now().strftime(str_format)
        except Exception:
            raise DateTimeFormatInvalid()

        return result

    @staticmethod
    def datetime_to_str(ori_time, str_format=None):
        str_format = str_format if str_format else "%Y-%m-%d %H:%M:%S"
        return ori_time.strftime(str_format)

    @staticmethod
    def datetime_set_tz(ori_time, tz=None):
        result = None
        tz = tz if tz else "Etc/GMT"
        tzinfo = pytz.timezone(tz)

        if ori_time:
            result = ori_time.replace(tzinfo=tzinfo)
        return result
