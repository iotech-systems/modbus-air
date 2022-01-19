
import xml.etree.ElementTree as et
from radiolib.reportBuffer import reportBuffer


class memblock_reader(object):

   def __init__(self, pico: et.Element, xmlconf: et.Element, rp: reportBuffer):
      self.pico: et.Element = pico
      self.xmlconf = xmlconf
      self.rptbuff = rp
      self.picoid = self.pico.attrib["airid"]

   def __repr__(self):
      return f"picoid: {self.picoid}; nodeid: {self.rptbuff.modbus_node_atid};"\
         f" node_dts: {self.rptbuff.node_dts}; node_data: {self.rptbuff.node_data}"

   def init(self):
      pass
