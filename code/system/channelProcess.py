
import time, setproctitle
import xml.etree.ElementTree as et
from system.genProcess import genProcess
from behaviours.datetimeBroadcaster import datetimeBroadcaster
from behaviours.pingPong import pingPong


class channelProcess(genProcess):

   def __init__(self, xml: et.Element):
      super().__init__(xml)
      self.xml: et.Element = xml
      self.__try_create_uart__()

   def run(self) -> None:
      procname = self.xml.attrib["procname"]
      setproctitle.setproctitle(procname)
      runfreq = self.xml.attrib["runfreq"].upper()
      delay = self.__get_delay__(runfreq)
      # -- run --
      while True:
         try:
            self.__main__()
            time.sleep(delay)
         except Exception as e:
            print(e)

   def __main__(self) -> int:
      behaviours = self.xml.findall("behaviour/do")
      for doxml in behaviours:
         self.__do__(doxml)

   def __do__(self, xml: et.Element):
      action = xml.attrib["action"]
      if action == "BROADCAST_DATETIME":
         dtb = datetimeBroadcaster(uart=self.uart, xmlconf=self.xml)
         dtb.run()
      elif action == "SLEEP":
         self.__sleep__(xml)
      elif action == "PING_PONG":
         pp: pingPong = pingPong(uart=self.uart, xmlconf=self.xml)
         pp.run()
      else:
         pass
