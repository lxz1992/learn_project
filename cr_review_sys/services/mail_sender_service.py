'''
@author: mtk10809
'''
from email.header import Header
from email.mime.text import MIMEText
from email.utils import COMMASPACE
import logging
import smtplib
import socket

from django.conf import settings

from cr_review_sys.const import Const
from my_to_do.util import Singleton


class MailSenderService(object, metaclass=Singleton):
    def __init__(self):
        self.logger = logging.getLogger("aplogger")
        self.smtp_obj = self.login_smtp()
        self.sender = "Claire.Hsieh@mediatek.com"

    def login_smtp(self):
        smtp_obj = smtplib.SMTP(settings.SMTP_SERVER)
#         smtp_obj.starttls()
#         # need to apply an account for mytodo cr review system
#         # NT account, ex. mtk10809
#         # password
#         smtp_obj.login('mtk10809', 'clairepwd1')
        return smtp_obj

    def logout_smtp(self):
        self.smtp_obj.quit()

    def send_mail(self, to_list, cc_list, subject, mail_msg):
        message = MIMEText(mail_msg, 'html', Const.UTF8)
        message['From'] = Header(Const.MAIL_FROM, Const.UTF8)
        message['To'] = Header(COMMASPACE.join(to_list))
        message['CC'] = Header(COMMASPACE.join(cc_list))
        message['Subject'] = Header(subject, Const.UTF8)
        receiver_list = to_list + cc_list

        try:
            self.smtp_obj.sendmail(self.sender, receiver_list, message.as_string())
        except socket.timeout:
            # smtp session expired, re-login
            self.login_smtp()
            self.smtp_obj.sendmail(self.sender, receiver_list, message.as_string())
        except smtplib.SMTPException as e:
            self.logger.exception("smtplib exception: %s", e)
        except Exception as e:
            self.logger.exception("send mail exception: %s", e)
