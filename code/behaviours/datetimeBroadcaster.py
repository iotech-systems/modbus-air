import time
import typing as t, serial
from radiolib.radioMsg import *
from system.genDo import genDo
import xml.etree.ElementTree as et
from system.consts import *
from system.uartSendReceive import uartSendReceive
from system.sysutils import sysutils


class datetimeBroadcaster(genDo):

   PING_TTL_SECS = 2
   PING_TRIES = 3

   def __init__(self, **kwargs):
      super().__init__()
      if "uart" not in kwargs:
         raise ValueError("MissingUART")
      self.uart: serial.Serial = kwargs["uart"]
      if "xmlconf" not in kwargs:
         raise ValueError("MissingXMLCONF")
      self.xmlconf: et.Element = kwargs["xmlconf"]

   def run(self, **kwargs):
      xpath = "picobugs/picobug"
      picos: t.List[et.Element] = self.xmlconf.findall(xpath)
      # -- for each pico --
      for pico in picos:
         for i in range(0, datetimeBroadcaster.PING_TRIES):
            if self.__ping_pico__(pico):
               break
            else:
               if i == (datetimeBroadcaster.PING_TRIES - 1):
                  airid = pico.attrib["airid"]
                  msg = f"unable to ping picobug: {airid}; tries: {i}"
                  sysutils.send_email(msg)
      # -- end for each pico --

   def __ping_pico__(self, pico: et.Element):
      tmp = pico.attrib["airid"]
      pico_airid = int(tmp, 16) if tmp.startswith("0x") else int(tmp)
      ping: bytearray = radioMsg.ping_msg(pico_airid, 0x00)
      sendReceive: uartSendReceive = uartSendReceive(self.uart, ping
         , datetimeBroadcaster.PING_TTL_SECS)
      sendReceive.do()
      while sendReceive.doing == Doing.WAITING:
         time.sleep(datetimeBroadcaster.PING_TTL_SECS / 10)
         print("sr is doing...")
      if sendReceive.doing == Doing.DONE and sendReceive.no_response:
         print("no response...")
      else:
         print(sendReceive.response_buffer)
      print("xxxxx")
