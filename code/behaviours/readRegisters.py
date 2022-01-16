
import time
import typing as t, serial
from radiolib.radioMsg import *
from system.genDo import genDo
import xml.etree.ElementTree as et
from system.consts import *
from system.uartSendReceive import uartSendReceive, uartStatus
from system.sysutils import sysutils


class readResults(object):

   def __init__(self, picobugID: int, modbusID: str):
      self.picobug_id = picobugID
      self.modbus_node_id = modbusID
      self.ack_ok = True
      self.rsp_code: int = 0
      self.rsp_barr: bytearray = None


class readRegisters(genDo):

   MAX_DO_TRIES = 3
   DO_TTL_SECS = 1

   def __init__(self, **kwargs):
      super().__init__()
      if "uart" not in kwargs:
         raise ValueError("MissingUART")
      self.uart: serial.Serial = kwargs["uart"]
      if "xmlconf" not in kwargs:
         raise ValueError("MissingXMLCONF")
      self.xmlconf: et.Element = kwargs["xmlconf"]

   """
      needs to be redone ... do it as:
         create a list of all pics + nodes on it ... as simple list then
         run over the list in a single for loop ....
   """
   def run(self, **kwargs):
      print("\n\treadRegisters\n")
      picos: t.List[et.Element] = self.xmlconf.findall(xpaths.PICOBUGS_PICOBUG)
      # -- for each pico in air channel --
      for pico in picos:
         self.__qry_picobug__(pico)
      # -- end for each pico --

   def __qry_picobug__(self, pico: et.Element):
      tmp = pico.attrib["airid"]
      pico_airid = int(tmp, 16) if tmp.startswith("0x") else int(tmp)
      pico_modbus_nodes = pico.findall(xpaths.MODBUS_NODE)
      accu_bag: t.List[readResults] = []
      # -- qry each node on the picobug --
      print(f"\n\t[qry picobug: {pico_airid}]\n")
      for mb_node in pico_modbus_nodes:
         rs: readResults = self.__read_each_modbus_node__(pico_airid, mb_node)
         accu_bag.append(rs)
         time.sleep(1)
      # -- post picobug scan --
      print(accu_bag)

   def __read_each_modbus_node__(self, pico_airid, mb_node: et.Element) -> readResults:
      read_from = 0x00
      msgid: int = msgIDGen.get_id()
      adr = mb_node.attrib["address"]
      node_adr = f"@{adr}"
      rs: readResults = readResults(pico_airid, node_adr)
      rnrs: bytearray = radioMsg.new_msg(pico_airid, read_from, msgid
         , msgTypes.READ_NODE_REGS, bytearray(node_adr.encode()))
      # -- will catch ack first --
      first_ack_secs = 2
      print(f"\t\t-> qry: @{pico_airid} + {node_adr}")
      sndRecv: uartSendReceive = uartSendReceive(self.uart, rnrs, first_ack_secs)
      sndRecv.do(with_snd=False)
      # -- wait for ack from picobug --
      sndRecv.await_ack()
      rs.rsp_barr = sndRecv.response_buffer
      return rs

   def __await_ack__(self, sndRecv: uartSendReceive):
      while sndRecv.status not in (uartStatus.TIMEOUT, uartStatus.DONE):
         time.sleep(readRegisters.DO_TTL_SECS / 8)
         print(f"*{sndRecv.status};", end="")
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

