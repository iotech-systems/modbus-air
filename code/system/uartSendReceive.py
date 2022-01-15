
import time
import threading, serial
from system.consts import *


class uartSendReceive(object):

   def __init__(self, uart: serial.Serial, barr: bytearray, ttl=0):
      self.uart = uart
      self.barr = barr
      self.ttl = ttl
      self.do_thread: threading.Thread = None
      self.ttl_timer: threading.Timer
      self.ttl_flag = False
      self.__doing = Doing.WAITING
      self.__no_resp = False
      self.__buff_out: bytearray = bytearray()

   def do(self):
      self.do_thread = threading.Thread(target=self.__do_thread__)
      self.do_thread.start()

   @property
   def doing(self) -> Doing:
      return self.__doing

   @property
   def no_response(self) -> bool:
      return self.__no_resp

   @property
   def response_buffer(self) -> bytearray:
      return self.__buff_out

   def __do_thread__(self):
      # -- callback --
      ontimer_flag = False
      def ontimer():
         print("-- ontimer --")
         nonlocal ontimer_flag
         ontimer_flag = True
      # -- end callback --
      self.uart.reset_output_buffer()
      self.uart.reset_input_buffer()
      print(f"sending: {self.barr}")
      self.uart.write(self.barr)
      self.ttl_timer = threading.Timer(interval=self.ttl, function=ontimer, args=())
      self.ttl_timer.start()
      # -- wait on feedback --
      while self.uart.in_waiting == 0:
         if ontimer_flag:
            break
         time.sleep(0.02)
      # -- run --
      if self.uart.in_waiting == 0 and ontimer_flag:
         self.__doing = Doing.DONE
         self.__no_resp = True
      else:
         # -- got response in ttl --
         self.ttl_timer.cancel()
         while self.uart.in_waiting > 0:
            self.__buff_out.extend(self.uart.read(1))
         self.__doing = Doing.DONE
