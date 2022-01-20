import os.path
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
      self.reads_buffer = []
      self.registers = []

   def __repr__(self):
      return f"picoid: {self.picoid}; nodeid: {self.rptbuff.modbus_node_atid};"\
         f" node_dts: {self.rptbuff.node_dts}; node_data: {self.rptbuff.node_data}"

   def process_read_results(self):
      print(f"process_read_results: {self.rptbuff.node_data}")
      rval = (0, -1, None)
      # -- start while --
      while rval is not None:
         # -- return sloc, idx, barr[sloc:idx] --
         idx = rval[1]
         rval = sysutils.get_next((idx+1), self.rptbuff.node_data)
         if rval is not None:
            self.reads_buffer.append(rval)
         else:
            rval = sysutils.get_last((idx+1), self.rptbuff.node_data)
            self.reads_buffer.append(rval)
            rval = None
      # -- end while --

   def load_node_regs_file(self):
      nid = self.rptbuff.modbus_node_id
      xpath = f"modbus/node[@address=\"{nid}\"]"
      elmt = self.pico.find(xpath)
      if elmt is None:
         print(f"NodeNotFound: {nid}")
         return
      # -- -- -- --
      model = elmt.attrib["model"]
      model_file = f"meters/{model}.regs"
      if not os.path.exists(model_file):
         print(f"FileNotFound: {model_file}")
         return
      # -- -- -- --
      with open(model_file, "r") as f:
         lns = f.readlines()
      self.registers = [ln for ln in lns if ln.startswith("0x")]
      print(self.registers)
