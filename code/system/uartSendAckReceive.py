
import time
import threading, serial
from system.consts import *
from system.uartRecieve import uartReceive, uartReceiveStatus
from radiolib.radioMsg import msgTypes


class uartSendAckReceive(object):

   def __init__(self, uart: serial.Serial, barr: bytearray
      , ttl: int = 0, ack_ttl: int = 1):
      # -- fields --
      self.uart = uart
      self.barr = barr
      self.ttl = ttl
      self.ack_ttl = ack_ttl
      self.do_thread: threading.Thread = None
      self.ttl_timer: threading.Timer
      self.ttl_flag = False
      self.__status = uartStatus.WAITING
      self.__no_resp = False
      self.__buff_out: bytearray = bytearray()
      self.__chr_dly_secs = round(((1 / (self.uart.baudrate / 11)) + 0.001), 4)

   def do(self):
      self.do_thread = threading.Thread(target=self.__do_thread__)
      self.do_thread.start()

   @property
   def status(self) -> uartStatus:
      return self.__status

   @property
   def no_response(self) -> bool:
      return self.__no_resp

   @property
   def response_buffer(self) -> bytearray:
      return self.__buff_out

   def __do_thread__(self):
      self.__status = uartStatus.AWAIT_ACK
      self.__rec_msg__(mtype=msgTypes.MSG_ACK)
      self.__status = (uartStatus.GOT_ACK | uartStatus.AWAIT_RSP)
      self.__rec_msg__(mtype=msgTypes.READ_NODE_REGS)
      self.__status = uartStatus.GOT_RSP

   def __rec_msg__(self, mtype: bytearray):
      ur: uartReceive = uartReceive(self.uart, 1)
      ur.do()
      while ur.status != uartReceiveStatus.DONE:
         print(ur.status)
         time.sleep(0.02)
      if ur.status == uartReceiveStatus.TIMEOUT:
         pass
      if ur.status == uartReceiveStatus.DONE:
         print(f"__rec_msg__: {ur.buff_out}")
      # -- check msg type --
