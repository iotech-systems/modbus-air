
from smtplib import SMTP


SMTP_SERVER = ""
SMTP_PORT = ""
SMTP_USER = ""
SMTP_PWD = ""
EMAIL_TO = "omms@iotech.systems"
EMAIL_FR = "noreply@omms.iotech.systems"


class sysutils(object):

   @staticmethod
   def send_email(title, msg):
      print(f"send_email: {msg}")