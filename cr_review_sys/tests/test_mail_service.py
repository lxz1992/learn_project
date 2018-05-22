import logging

from django.test import TestCase

from cr_review_sys.const import MailInfo, Const
from cr_review_sys.models import Cr, ActivityCr
from cr_review_sys.services.mail_sender_service import MailSenderService
from cr_review_sys.services.cr_notify_mail_service import CrNotifyMailService


class MailServiceTest(TestCase):

    def setUp(self):
        self.logger = logging.getLogger('aplogger')
        self.mail_service = MailSenderService()
        self.cr_notify_service = CrNotifyMailService()

        Cr.objects.create(cr_id="tstdb03618301",
                          state=MailInfo.State.Submitted.value, title="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        ActivityCr.objects.create(
            id="1_tstdb03618301", activity_id="1", cr_id="tstdb03618301", active=Const.IS_ACTIVE)

        Cr.objects.create(cr_id="tstdb03618302",
                          state=MailInfo.State.Submitted.value)
        ActivityCr.objects.create(
            id="1_tstdb03618302", activity_id="1", cr_id="tstdb03618302", active=Const.IS_ACTIVE)

        Cr.objects.create(cr_id="tstdb03618303",
                          state=MailInfo.State.Assigned.value)
        ActivityCr.objects.create(
            id="1_tstdb03618303", activity_id="1", cr_id="tstdb03618303", active=Const.IS_ACTIVE)

        Cr.objects.create(cr_id="ALPS03758724",
                          state=MailInfo.State.Assigned.value)
        ActivityCr.objects.create(
            id="1_ALPS03758724", activity_id="1", cr_id="ALPS03758724", active=Const.IS_ACTIVE)

    def test_send_mail_entry(self):
        to_list = ["claire.hsieh@mediatek.com"]
        cc_list = ["cash.chang@mediatek.com"]
        subject = "CR Review System郵件測試 - test_send_mail_entry"
        mail_msg = "CR Review System郵件測試"

        try:
            self.mail_service.send_mail(to_list, cc_list, subject, mail_msg)
            assert True
        except Exception:
            assert False
