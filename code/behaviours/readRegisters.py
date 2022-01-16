
import time
import typing as t, serial
from radiolib.radioMsg import *
from system.genDo import genDo
import xml.etree.ElementTree as et
from system.consts import *
from system.uartSendReceive import uartSendReceive, uartStatus
from system.sysutils import sysutils


class readRegisters(genDo):

   DO_TRIES = 3
   DO_TTL_SECS = 1

   def __init__(self, **kwargs):
      super().__init__()
      if "uart" not in kwargs:
         raise ValueError("MissingUART")
      self.uart: serial.Serial = kwargs["uart"]
      if "xmlconf" not in kwargs:
         raise ValueError("MissingXMLCONF")
      self.xmlconf: et.Element = kwargs["xmlconf"]

   def run(self, **kwargs):
      print("\n\treadRegisters\n")
      picos: t.List[et.Element] = self.xmlconf.findall(xpaths.PICOBUGS_PICOBUG)
      # -- for each pico --
      for pico in picos:
         for i in range(0, readRegisters.DO_TRIES):
            if self.__read_each_pico__(pico):
               break
            else:
               if i == (readRegisters.DO_TRIES - 1):
                  airid = pico.attrib["airid"]
                  msg = f"unable to ping picobug: {airid}; tries: {i}"
                  sysutils.send_email("OpenMMS Warning", msg)
      # -- end for each pico --

   def __read_each_pico__(self, pico: et.Element):
      ping_from: int = 0x00
      tmp = pico.attrib["airid"]
      pico_airid = int(tmp, 16) if tmp.startswith("0x") else int(tmp)
      pico_modbus_nodes = pico.findall(xpaths.MODBUS_NODE)
      for mb_node in pico_modbus_nodes:
         self.__read_each_pico_node__(pico_airid, mb_node)

   def __read_each_pico_node__(self, pico_airid, mb_node: et.Element):
      read_from = 0x00
      msgid: int = msgIDGen.get_id()
      adr = mb_node.attrib["address"]
      barr = f"@{adr}".encode()
      rnrs: bytearray = radioMsg.new_msg(pico_airid, read_from, msgid
         , msgTypes.READ_NODE_REGS, bytearray(barr))
      # -- will catch ack first --
      sndRecv: uartSendReceive = uartSendReceive(self.uart, rnrs, 1)
      sndRecv.do()
      self.__await_ack__(sndRecv)
      time.sleep_ms(20)
      self.__await_rsp__(sndRecv)

   def __await_ack__(self, sndRecv: uartSendReceive):
      while sndRecv.status not in (uartStatus.TIMEOUT, uartStatus.DONE):
         time.sleep(readRegisters.DO_TTL_SECS / 8)
         print("*", end="")
      if sndRecv.status == uartStatus.TIMEOUT:
         pass
      if sndRecv.status == uartStatus.DONE:
         ack: bytearray = sndRecv.response_buffer
         print(f"ACK: {ack}")

   def __await_rsp__(self, sndRecv: uartSendReceive):
      while sndRecv.status not in (uartStatus.TIMEOUT, uartStatus.DONE):
         time.sleep(readRegisters.DO_TTL_SECS / 8)
         print("*", end="")
      if sndRecv.status == uartStatus.TIMEOUT:
         pass
      if sndRecv.status == uartStatus.DONE:
         rsp: bytearray = sndRecv.response_buffer
         print(f"RSP: {rsp}")
