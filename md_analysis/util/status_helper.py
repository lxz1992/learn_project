import datetime

from md_analysis.const import MdPrjStatus
from my_to_do.util.date_helper import DateHelper


class StatusHelper(object):

    @staticmethod
    def get_prj_status(year, week):
        '''
        Get prj status for MD OP/FTA project
        Input year/week(last 2 digits)
        Return ongoing/incoming/now
        '''
        if not (year and week):
            return None

        check_year = int(year)
        check_week = int(week)
        (now_year, now_week) = DateHelper.calculate_mtk_week(
            datetime.datetime.now())

        if check_year > now_year:

            tmp_week = 53 - now_week
            total_week = tmp_week + check_week

            if total_week < 5:
                return MdPrjStatus.INCOMING
            else:
                return None  # over 4 weeks

        else:
            if check_year == now_year:
                if check_week > now_week:
                    interval = check_week - now_week
                    if interval > 4:
                        return None  # over 4 weeks
                    else:
                        return MdPrjStatus.INCOMING
                else:
                    if check_week == now_week:
                        return MdPrjStatus.NEW
                    else:
                        return MdPrjStatus.ONGOING
            else:
                return MdPrjStatus.ONGOING
