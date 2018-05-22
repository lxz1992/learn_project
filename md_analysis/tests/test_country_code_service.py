from django.test import TestCase

from cr_review_sys.models import MdMccMnc
from md_analysis.services.country_code_service import CountryCodeService


class CountryCodeTest(TestCase):
    def setUp(self):
        self.country_code_service = CountryCodeService()

    def test_get_code_by_country(self):
        MdMccMnc.objects.create(id="714_01", mcc="714", mcn="01",
                                country="Panama", country_code="PA")
        MdMccMnc.objects.create(id="714_02", mcc="714", mcn="02",
                                country="Panama", country_code="PA")
        expected_result = "Panama"
        test_result = self.country_code_service.get_code_by_country("PA")
        self.assertEqual(expected_result, test_result)
