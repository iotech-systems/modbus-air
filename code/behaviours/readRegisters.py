
import time
import typing as t, serial
from radiolib.radioMsg import *
from system.genDo import genDo
import xml.etree.ElementTree as et
from system.consts import *
from system.uartRecieve import uartReceive
from system.uartSendReceive import uartSendReceive, uartStatus
from radiolib.reportBuffer import reportBuffer
from radiolib.radioUtils import radioUtils
from omms.memblock_reader import memblock_reader


class readResults(object):

   def __init__(self, picobugID: int, modbusID: str):
      self.picobugID = picobugID
      self.modbusID = modbusID
      self.ack_ok = True
      self.rsp_code: int = 0
      self.rsp_barr: bytearray = None

   def __repr__(self):
      return f"\nackOK: {self.ack_ok}\npicobugID: {self.picobugID}"\
         f"\nmodbusNodeID: {self.modbusID}\nrsp_code: {self.rsp_code}"\
         f"\nnodeoutput: {self.nodeoutput}"

   @property
   def nodeoutput(self) -> bytearray:
      barr = self.rsp_barr[16:-1]
      if not radioMsg.test_vts(barr):
         raise ValueError("BadOrNoVTs")
      # --
      barr_no_vts = barr[1:-1]
      return barr_no_vts


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

   def run(self, **kwargs):
      print("\n\treadRegisters\n")
      picos: t.List[et.Element] = self.xmlconf.findall(xpaths.PICOBUGS_PICOBUG)
      # -- for each pico in air channel --
      for pico in picos:
         rset = self.__qry_picobug__(pico)
         self.__process_results__(pico, rset)
      # -- end for each pico --

   def __qry_picobug__(self, pico: et.Element) -> t.List[readResults]:
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
      return accu_bag

   def __read_each_modbus_node__(self, pico_airid, mb_node: et.Element) -> readResults:
      read_from = 0x00
      msgid: int = msgIDGen.get_id()
      adr: int = int(mb_node.attrib["address"])
      node_adr = radioUtils.modbus_node_to_atid(adr)
      rs: readResults = readResults(pico_airid, node_adr)
      rnrs: bytearray = radioMsg.new_msg(pico_airid, read_from, msgid
         , msgTypes.READ_NODE_REGS, bytearray(node_adr.encode()))
      # -- will catch ack first --
      first_ack_secs = 2
      print(f"\t\t-> qry: @{pico_airid} + {node_adr}")
      sndRecv: uartSendReceive = uartSendReceive(self.uart, rnrs, first_ack_secs)
      sndRecv.do(with_snd=True)
      # -- wait for ack from picobug --
      sndRecv.await_ack()
      # -- this buff should ba ack msg --
      if not radioMsg.is_good_ack(pico_airid, msgid, sndRecv.response_buffer):
         print("BAD_ACK")
         rs.ack_ok = False
         return rs
      # -- good ack --
      print(f"GOOD_ACK: {pico_airid}/{msgid}")
      ur: uartReceive = uartReceive(uart=self.uart, ttl=2)
      ur.do()
      while ur.status not in (uartStatus.TIMEOUT, uartStatus.DONE):
         time.sleep(0.01)
      rs.rsp_barr = ur.read_buff
      print(f"RSP: {rs.rsp_barr}")
      return rs

   def __process_results__(self, pico: et.Element, rset: t.List[readResults]):
      print(f"\n\t[ process_results ~ count: {len(rset)} ]\n")
      for item in rset:
         self.__per_result__(pico, item)

   def __per_result__(self, pico: et.Element, rs: readResults):
      rp: reportBuffer = reportBuffer()
      rp.parse_bytes(rs.nodeoutput)
      print(f"\t[ {rp.modbus_node_atid} ]")
      if rp.error_code == 0:
         mb: memblock_reader = memblock_reader(pico, self.xmlconf, rp)
         mb.parse_read_results()
         mb.load_node_regs_file()
         mb.process_reads_buffer()
         # mb.print_registers()
         mb.report()
      else:
         print(f"\terr: {rp.error_code} -- errmsg: {rp.error_msg}")
