
import struct


class register(object):

   def __init__(self, buff: str):
      self.buff = buff
      arr = buff.split(":")
      self.adr: str = arr[0]
      self.size = int(arr[1], 10)
      self.ntype = arr[2]
      self.dcpnt: int = int(arr[3])
      self.label = arr[4]
      self.reading: bytearray = bytearray()
      self.flt_val: float = None
      self.int_val: int = None

   def __repr__(self):
      return f"adr: {self.adr}; sz: {self.size}; tp: {self.ntype};" \
         f" dcpnt: {self.dcpnt}; lbl: {self.label}; int: {self.int_val};" \
         f" flt: {self.flt_val}"

   def set_reading(self, barr: bytearray):
      self.reading.extend(barr)
      if self.ntype == "flt":
         self.flt_val = struct.unpack(">f", self.reading)
      elif self.ntype == "int":
         self.int_val = struct.unpack(">I", self.reading)
      else:
         pass
