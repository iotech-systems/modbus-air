#!/usr/bin/env python3

from system import hc12ops
from system.processStarter import processStarter


CONF_XML = "conf.xml"
START_LIST = ["channelProcess.channelProcess"]


def main():
   starter: processStarter = processStarter()
   starter.load_xml(CONF_XML)
   starter.start(START_LIST)


# -- entry point --
if __name__ == "__main__":
   main()
