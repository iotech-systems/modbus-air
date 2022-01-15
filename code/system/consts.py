
from typing import Callable


class uartStatus(object):

   READY = 0
   SENDING = 2
   WAITING = 4
   DONE = 8
   AWAIT_ACK = 16
   GOT_ACK = 32
   AWAIT_RSP = 64
   GOT_RSP = 128
   TIMEOUT = 256
   READING = 512

