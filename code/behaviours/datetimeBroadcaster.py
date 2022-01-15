
import time, serial, datetime
from radiolib.radioMsg import *
from system.genDo import genDo
import xml.etree.ElementTree as et


class datetimeBroadcaster(genDo):

   def __init__(self, **kwargs):
      super().__init__()
      if "uart" not in kwargs:
         raise ValueError("MissingUART")
      self.uart: serial.Serial = kwargs["uart"]
      if "xmlconf" not in kwargs:
         raise ValueError("MissingXMLCONF")
      self.xmlconf: et.Element = kwargs["xmlconf"]

   def run(self, **kwargs):
      msgid = msgIDGen.get_id()
      dts = self.__dts__()
      barr: bytearray = radioMsg.new_msg(0xff, 0x00, msgid, msgTypes.SET_DATETIME, dts)
      cnt = self.uart.write(barr)
      print(f"\n\tbytes sent: {cnt}\n\tSTDT: {barr}")

   def __dts__(self) -> bytearray:
      t = datetime.datetime.today()
      dts = "%04d%02d%02dT%02d%02d%02d" \
            % (t.year, t.month, t.day, t.hour, t.minute, t.second)
      return bytearray(dts.encode())
