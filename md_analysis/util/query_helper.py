'''
@author: MTK10809
'''
from cr_review_sys.models import ActivityCr
from md_analysis.const import MdMeta
from my_to_do.util import Singleton


class QueryHelper(object, metaclass=Singleton):
    def check_cr_in_activity(self, cr_id, activity_id=MdMeta.ActivityId):
        queryset = ActivityCr.objects.filter(cr_id=cr_id, active=1)
        return any(x for x in queryset)
