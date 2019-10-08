"""
Created on 13 Jul 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

https://unix.stackexchange.com/questions/139490/continuous-reading-from-named-pipe-cat-or-tail-f
"""

import os
import sys

from scs_host.comms.domain_socket import DomainSocket


# --------------------------------------------------------------------------------------------------------------------
# input reader...

class UDSReader(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, uds_name):
        """
        Constructor
        """
        if uds_name is None:
            self.__uds = None
            return

        try:
            os.remove(uds_name)             # override any previous use of the UDS
        except OSError:
            pass

        self.__uds = DomainSocket(uds_name)


    # ----------------------------------------------------------------------------------------------------------------

    def connect(self):
        if self.__uds:
            self.__uds.connect()


    def close(self):
        if self.__uds:
            self.__uds.close()


    def messages(self):
        if self.__uds:
            for message in self.__uds.read():
                yield message.strip()

        else:
            for message in sys.stdin:
                yield message.strip()


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "UDSReader:{uds:%s}" % self.__uds
