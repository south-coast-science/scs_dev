"""
Created on 13 Jul 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

https://unix.stackexchange.com/questions/139490/continuous-reading-from-named-pipe-cat-or-tail-f
"""

import sys

from scs_host.comms.domain_socket import DomainSocket


# --------------------------------------------------------------------------------------------------------------------

class UDSWriter(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, address):
        """
        Constructor
        """
        self.__uds = DomainSocket(address) if address else None


    # ----------------------------------------------------------------------------------------------------------------

    def connect(self):
        if self.__uds:
            self.__uds.connect()


    def close(self):
        if self.__uds:
            self.__uds.close()


    def write(self, message, wait_for_availability=False):
        if self.__uds:
            self.__uds.write(message, wait_for_availability)

        else:
            print(message)
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "UDSWriter:{uds:%s}" % self.__uds
