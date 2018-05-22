from django.test import TestCase

from cr_review_sys.models import OpGroup
from md_analysis.const import MdMeta
from md_analysis.services.ces_specific_service import CesSpecificService


class CesSpecificTest(TestCase):
    def setUp(self):
        self.ces = CesSpecificService()

    def all_upper(self, input_list):
        return [s.upper() for s in input_list]

    def test_get_mea_top10(self):
        op_type = "MEA top 10"
        country_list = ["Kenya", "Morocco", "Nigeria", "Oman Sultanate of",
                        "Saudi Arabia", "South Africa", "Tunisia", "Turkey", "UAE"]

        for eachcountry in country_list:
            OpGroup.objects.create(id="{}_{}".format(
                op_type, eachcountry), group_name=MdMeta.MEATop10, type=MdMeta.OpCountryType, value=eachcountry)
        expected_result = self.all_upper(country_list)
        test_result = self.ces.get_mea_top10()
        self.assertEqual(expected_result, test_result)
