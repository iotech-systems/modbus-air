
import time
import typing as t, serial
from radiolib.radioMsg import *
from system.genDo import genDo
import xml.etree.ElementTree as et
from system.consts import *
from system.uartSendReceive import uartSendReceive
from system.sysutils import sysutils


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
      print("datetimeBroadcaster run")
      msgid = msgIDGen.get_id()
      dts = bytearray("20220122T092244".encode())
      barr: bytearray = radioMsg.new_msg(0xff, 0x00, msgid, msgTypes.SET_DATETIME, dts)
      cnt = self.uart.write(barr)
      print(f"\n\tbytes sent: {cnt}")
