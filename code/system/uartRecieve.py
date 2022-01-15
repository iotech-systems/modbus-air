
import time
import serial
import threading
from system.consts import uartStatus


class uartReceive(object):

   OFFSET = 0.001
   BYTE_BITS = 11

   def __init__(self, uart: serial.Serial, ttl: int = 1):
      self.uart = uart
      self.ttl = ttl
      self.timeout_flag = False
      self.buff_out: bytearray = bytearray()
      self.status = uartStatus.READY
      self.__chr_dly_secs = \
         round(((1 / (self.uart.baudrate / uartReceive.BYTE_BITS)) + uartReceive.OFFSET), 4)

   def do(self):
      self.uart.reset_input_buffer()
      self.uart.reset_output_buffer()
      thread = threading.Thread(target=self.__do_thread__, args=())
      thread.start()

   def __do_thread__(self):
      # -- callback --
      timeout_flag = False
      def __on_timeout__():
         nonlocal timeout_flag
         timeout_flag = True
      # -- end callback --
      timer = threading.Timer(interval=self.ttl, function=__on_timeout__)
      timer.start()
      while self.uart.in_waiting == 0:
         if timeout_flag:
            break
         time.sleep(self.ttl / 16)
      # -- got chars or timeout
      if timeout_flag:
         self.status = uartStatus.TIMEOUT
      else:
         # -- read incoming ---
         self.status = uartStatus.READING
         while self.uart.in_waiting > 0:
            self.buff_out.extend(self.uart.read(1))
            time.sleep(self.__chr_dly_secs)
         # -- done reading ---
         self.status = uartStatus.DONE
