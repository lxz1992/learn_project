from django.test import TestCase

from md_analysis.const import MdMeta
from md_analysis.services.cr_analysis_by_hwprj_service import CrAnalysisByHwPrjService


class CrAnalysisByHwPrjServiceTest(TestCase):
    def setUp(self):
        self.cr_ana_by_hwprj = CrAnalysisByHwPrjService()

    def test_check_md_dept_or_not(self):
        test_result = self.cr_ana_by_hwprj.check_md_dept_or_not("wcs_sd_a_b")
        self.assertEqual(test_result, True)

        test_result = self.cr_ana_by_hwprj.check_md_dept_or_not("wcs_sd")
        self.assertEqual(test_result, True)

        test_result = self.cr_ana_by_hwprj.check_md_dept_or_not("a_wcs_sdc")
        self.assertEqual(test_result, True)

        test_result = self.cr_ana_by_hwprj.check_md_dept_or_not("mfi_wsp_se7_de7")
        self.assertEqual(test_result, True)
