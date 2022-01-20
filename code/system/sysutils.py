
from smtplib import SMTP
from radiolib.asciitable import asciitable


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

   @staticmethod
   def get_reading(sloc: int, barr: bytearray) -> [None, (int, bytearray)]:
      for idx in range(sloc, len(barr)):
         if barr[idx] == asciitable.RS:
            return idx, barr[sloc:idx]
      # -- not found --
      return None
