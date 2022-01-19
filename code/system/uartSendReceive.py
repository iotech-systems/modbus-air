
import time
import threading, serial
from system.consts import *


class uartSendReceive(object):

   def __init__(self, uart: serial.Serial, barr: bytearray, timeout_secs=1):
      self.uart = uart
      self.barr_out = barr
      self.with_send = True
      self.timeout_secs = timeout_secs
      self.do_thread: threading.Thread = None
      self.__status = uartStatus.READY
      self.__rsp_buffer: bytearray = bytearray()
      self.__chr_dly_secs = self.__char_delay__()
      self.on_response = None
      self.on_timeout = None
      self.__clr_uart__()

   def do(self, with_snd: bool = True):
      self.with_send = with_snd
      self.do_thread = threading.Thread(target=self.__do_thread__)
      self.do_thread.start()

   @property
   def status(self) -> uartStatus:
      return self.__status

   @property
   def response_buffer(self) -> bytearray:
      return self.__rsp_buffer

   def await_ack(self):
      """
         this will simply check if the 1st msg coming from picobug is MACK
         :return:
      """
      while self.status not in (uartStatus.TIMEOUT, uartStatus.DONE):
         time.sleep(0.01)
      if self.status == uartStatus.TIMEOUT:
         print("\tACK_TIMEOUT_REACHED")
      if self.status == uartStatus.DONE:
         print(f"\t[ uartStatus.DONE ]")

   def send(self):
      print(f"sending: {self.barr_out}")
      self.uart.write(self.barr_out)

   def __do_thread__(self):
      # -- with send --
      if self.with_send:
         self.send()
      # -- callback --
      ontimer_flag = False
      def on_ttl_timeout():
         print("\n\t-- on_ttl_timeout --\n")
         nonlocal ontimer_flag
         ontimer_flag = True
      # -- end callback --
      self.ttl_timer = threading.Timer(interval=self.timeout_secs, function=on_ttl_timeout)
      self.ttl_timer.start()
      # -- wait on response --
      while self.uart.in_waiting == 0:
         if ontimer_flag:
            break
         time.sleep(self.timeout_secs/8)
      # -- run --
      if ontimer_flag:
         self.__status = uartStatus.TIMEOUT
         if self.on_timeout is not None:
            self.on_timeout()
      else:
         self.ttl_timer.cancel()
         while self.uart.in_waiting > 0:
            self.__rsp_buffer.extend(self.uart.read(1))
            time.sleep(self.__chr_dly_secs)
         self.__status = uartStatus.DONE
         print(f"__rsp_buffer: {self.__rsp_buffer}")
         if self.on_response is not None:
            self.on_response(self.__rsp_buffer)

   def __char_delay__(self):
      BYTEBITS = 11
      OFFSET = 0.001
      return round(((1 / (self.uart.baudrate / BYTEBITS)) + OFFSET), 4)

   def __clr_uart__(self):
      if self.uart is not None:
         self.uart.reset_output_buffer()
         self.uart.reset_input_buffer()
