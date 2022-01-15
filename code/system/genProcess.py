
import serial
import multiprocessing, time
import xml.etree.ElementTree as et


class genProcess(multiprocessing.Process):

   def __init__(self, xml: et.Element):
      super().__init__()
      self.xml = xml
      self.uart: et.Element = None
      self.__try_create_uart__()

   def __main__(self):
      pass

   def __do__(self, xml: et.Element):
      pass

   def __sleep__(self, xml: et.Element):
      xpath = "args/arg[@name=\"delay\"]"
      arg = xml.find(xpath)
      val = arg.attrib["value"]
      delay = self.__get_delay__(val)
      print(f"__sleep__: {delay}")
      time.sleep(delay)

   def __get_delay__(self, arg) -> int:
      arg = arg.upper()
      if "M" in arg:
         delay = int(arg.replace("M", "")) * 60
      else:
         delay = int(arg.replace("S", ""))
      return delay

   def __try_create_uart__(self):
      uxml: et.Element = self.xml.find("uart")
      if uxml is not None:
         dev = uxml.attrib["dev"]
         baud = uxml.attrib["baud"]
         self.uart = serial.Serial(port=dev, baudrate=baud)
      else:
         pass
