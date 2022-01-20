
import xml.etree.ElementTree as et
from radiolib.reportBuffer import reportBuffer
from radiolib.asciitable import asciitable
from system.sysutils import sysutils


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
      print(f"init: {self.rptbuff.node_data}")
      rval = (0, -1, None)
      while rval is not None:
         # --- return sloc, idx, barr[sloc:idx] ---
         idx = rval[1]
         rval = sysutils.get_next((idx+1), self.rptbuff.node_data)
         if rval is None:
            rval = sysutils.get_last((idx+1), self.rptbuff.node_data)
            print(rval)
            exit(0)
         # -- print --
         print(rval)
