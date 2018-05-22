from django.test import TestCase

from cr_review_sys.models import OpGroup, CrmHwProject
from md_analysis.const import Ces
from md_analysis.services.cr_list_service import CrListService


class CrListServiceTest(TestCase):
    def setUp(self):
        self.cr_list_service = CrListService()

    def test_get_country_list_by_group(self):
        group_list = ["Orange Group", "Vodafone Group"]

        OpGroup.objects.create(id="Operator_Orange",
                               type=Ces.GROUP, value="Orange", group_name="Orange Group")
        OpGroup.objects.create(id="Operator_Vodafone",
                               type=Ces.GROUP, value="Vodafone", group_name="Vodafone Group")

        expected_result = ["Orange", "Vodafone"]
        test_result = self.cr_list_service.get_country_list_by_group(
            group_list)
        self.assertEqual(expected_result, test_result)

    def test_get_all_country_list_by_group(self):
        OpGroup.objects.create(id="Operator_Orange",
                               type=Ces.GROUP, value="Orange", group_name="Orange Group")
        OpGroup.objects.create(id="Operator_Vodafone",
                               type=Ces.GROUP, value="Vodafone", group_name="Vodafone Group")
        OpGroup.objects.create(id="Operator_VodafoneB",
                               type=Ces.GROUP, value="VodafoneB", group_name="Vodafone Group")

        expected_result = ["Orange", "Vodafone", "VodafoneB"]
        test_result = self.cr_list_service.get_all_country_list_by_group()
        self.assertEqual(expected_result, test_result)

    def test_get_hw_prj_id_list_by_operator(self):
        operator = "CMCC"
        CrmHwProject.objects.create(id="00001_opertor", hw_project_id="00001", operator=operator)
        CrmHwProject.objects.create(id="00002_opertor", hw_project_id="00002", operator=operator)

        expected_result = ["00001", "00002"]
        test_result = self.cr_list_service.get_hw_prj_id_list_by_operator(
            operator)
        self.assertEqual(expected_result, test_result)
