

class register(object):

   def __init__(self, buff: str):
      self.buff = buff
      arr = buff.split(":")
      self.adr: str = arr[0]
      self.size = int(arr[1], 10)
      self.ntype = arr[2]
      self.dcpnt: int = int(arr[3])
      self.label = arr[4]

   def __repr__(self):
      return f"adr: {self.adr}; sz: {self.size}; tp: {self.ntype};" \
         f" dcpnt: {self.dcpnt}; lbl: {self.label};"

