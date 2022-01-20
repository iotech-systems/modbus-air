import datetime
import time, setproctitle
import xml.etree.ElementTree as et
from system.genProcess import genProcess
from behaviours.datetimeBroadcaster import datetimeBroadcaster
from behaviours.pingPong import pingPong
from behaviours.readRegisters import readRegisters


class channelProcess(genProcess):

   def __init__(self, xml: et.Element):
      super().__init__(xml)
      self.xml: et.Element = xml
      self.__try_create_uart__()

   def run(self) -> None:
      procname = self.xml.attrib["procname"]
      setproctitle.setproctitle(procname)
      runfreq = self.xml.attrib["runfreq"].upper()
      delay_secs = self.__get_delay__(runfreq)
      # -- run --
      while True:
         try:
            self.__main__()
            now = datetime.datetime.now()
            nxt = now + datetime.timedelta(seconds=delay_secs)
            print(f"\n\t[ nxt run @: {nxt} ]")
            time.sleep(delay_secs)
            print(f"\t[ running: {datetime.datetime.now()} ]")
         except Exception as e:
            print(e)

   def __main__(self) -> int:
      print("\n\n\t[ channelProcess ]\n")
      behaviours = self.xml.findall("behaviour/do")
      print(f"[behaviour/do] count: {len(behaviours)}")
      for doxml in behaviours:
         self.__do__(doxml)
      return 0

   def __do__(self, xml: et.Element):
      try:
         action = xml.attrib["action"]
         idx = xml.attrib["index"]
         print(f"\n[ behaviour: idx: {idx}; act: {action}; ]\n")
         # -- do --
         if action == "BROADCAST_DATETIME":
            dtb = datetimeBroadcaster(uart=self.uart, xmlconf=self.xml)
            dtb.run()
         elif action == "SLEEP":
            self.__sleep__(xml)
         elif action == "PING_PONG":
            pp: pingPong = pingPong(uart=self.uart, xmlconf=self.xml)
            pp.run()
         elif action == "READ_REGISTERS":
            rr: readRegisters = readRegisters(uart=self.uart, xmlconf=self.xml)
            rr.run()
         else:
            pass
      except Exception as e:
         print(f"e: {e}")
