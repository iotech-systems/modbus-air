
import xml.etree.ElementTree as et
from radiolib.reportBuffer import reportBuffer


class memblock_reader(object):

   def __init__(self, xmlconf: et.Element, rp: reportBuffer):
      self.xmlconf = xmlconf
      self.rptbuff = rp
      print(f"rptbuff: {self.rptbuff}")

   def load_from(self):
      print(self.xmlconf.text)
      print(self.rptbuff)
