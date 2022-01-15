
import typing as t
import serial, time
import xml.etree.ElementTree as et
from radiolib.radioMsg import radioMsg
from system.genDo import genDo
from system.sysutils import sysutils
from system.consts import *
from system.uartSendReceive import uartSendReceive


class pingPong(genDo):

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
         for i in range(0, pingPong.PING_TRIES):
            if self.__ping_pico__(pico):
               break
            else:
               if i == (pingPong.PING_TRIES - 1):
                  airid = pico.attrib["airid"]
                  msg = f"unable to ping picobug: {airid}; tries: {i}"
                  sysutils.send_email("OpenMMS Warning", msg)
      # -- end for each pico --

   def __ping_pico__(self, pico: et.Element):
      ping_from: int = 0x00
      tmp = pico.attrib["airid"]
      pico_airid = int(tmp, 16) if tmp.startswith("0x") else int(tmp)
      ping: bytearray = radioMsg.ping_msg(pico_airid, ping_from)
      sendReceive: uartSendReceive = uartSendReceive(self.uart, ping
         , pingPong.PING_TTL_SECS)
      sendReceive.do()
      while sendReceive.doing == Doing.WAITING:
         time.sleep(pingPong.PING_TTL_SECS / 10)
         print("*", end="")
      if sendReceive.doing == Doing.DONE and sendReceive.no_response:
         print(f"\n\tNO_RESPONSE_FROM_PICO: {pico_airid}\n")
      else:
         print(f"rsp buff: {sendReceive.response_buffer}")
         if radioMsg.is_pong_good(pico_airid, ping_from, sendReceive.response_buffer):
            print(f"\n\t good ping -> pong: {pico_airid}")
