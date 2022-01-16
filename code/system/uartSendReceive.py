
import time
import threading, serial
from system.consts import *


class uartSendReceive(object):

   def __init__(self, uart: serial.Serial, barr: bytearray, timeout_secs=1):
      self.uart = uart
      self.barr = barr
      self.timeout_secs = timeout_secs
      self.do_thread: threading.Thread = None
      self.__status = uartStatus.READY
      self.__rsp_buffer: bytearray = bytearray()
      self.__chr_dly_secs = self.__char_delay__()
      self.on_response = None
      self.on_timeout = None

   def do(self):
      self.uart.reset_output_buffer()
      self.uart.reset_input_buffer()
      self.do_thread = threading.Thread(target=self.__do_thread__)
      self.do_thread.start()

   @property
   def status(self) -> uartStatus:
      return self.__status

   @property
   def response_buffer(self) -> bytearray:
      return self.__rsp_buffer

   def await_ack(self, ack_timeout_secs: int = 1):
      while self.status not in (uartStatus.TIMEOUT, uartStatus.DONE):
         time.sleep(ack_timeout_secs/8)
         print(f"*{self.status};", end="")
      if self.status == uartStatus.TIMEOUT:
         print("ACK_TIMEOUT_REACHED")
      if self.status == uartStatus.DONE:
         print(f"ACK: {self.response_buffer}")

   def __do_thread__(self):
      # -- send --
      print(f"sending: {self.barr}")
      self.uart.write(self.barr)
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
         time.sleep(self.timeout_secs / 16)
      # -- run --
      if ontimer_flag:
         self.__status = uartStatus.TIMEOUT
         if self.on_timeout is not None:
            self.on_timeout()
      else:
         # -- got rsp b4 ttl out --
         self.ttl_timer.cancel()
         while self.uart.in_waiting > 0:
            self.__rsp_buffer.extend(self.uart.read(1))
            time.sleep(self.__chr_dly_secs)
         self.__status = uartStatus.DONE
         if self.on_response is not None:
            self.on_response(self.__rsp_buffer)

   def __char_delay__(self):
      BYTEBITS = 11
      OFFSET = 0.001
      return round(((1 / (self.uart.baudrate / BYTEBITS)) + OFFSET), 4)
