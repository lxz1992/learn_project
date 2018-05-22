import logging

from cr_review_sys.models import MdMccMnc
from my_to_do.util import Singleton


class CountryCodeService(object, metaclass=Singleton):
    def __init__(self):
        '''
        constructor
        '''
        self.logger = logging.getLogger('aplogger')

    def get_code_by_country(self, code):

        queryset = MdMccMnc.objects.filter(country_code=code).values_list(
            'country', flat=True).distinct()

        country = list(queryset)[0]
        return country
