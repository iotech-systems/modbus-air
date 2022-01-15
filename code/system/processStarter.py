import multiprocessing
import os.path, typing
import xml.etree.ElementTree as et
from pydoc import locate


class processStarter(object):

   def __init__(self):
      self.xmldoc: et.ElementTree = None

   def load_xml(self, file_path):
      if not os.path.exists(file_path):
         raise FileNotFoundError(file_path)
      self.xmldoc: et.ElementTree = et.parse(file_path)

   def start(self, start_list: []):
      lst: typing.List[et.Element] = self.xmldoc.findall("process")
      for elmt in lst:
         self.__start_process_by_cls(elmt, start_list)

   def __start_process_by_cls(self, confxml: et.Element,  start_lst: []):
      # -- get class name --
      clsname = confxml.attrib["class"]
      if clsname not in start_lst:
         return
      # -- create process --
      __class__ = locate(f"system.{clsname}")
      proc: multiprocessing.Process = __class__(confxml)
      proc.run()
