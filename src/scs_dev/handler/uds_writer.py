"""
Created on 13 Jul 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

https://unix.stackexchange.com/questions/139490/continuous-reading-from-named-pipe-cat-or-tail-f
"""

from scs_host.comms.domain_socket import DomainSocket


# --------------------------------------------------------------------------------------------------------------------

class UDSWriter(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, uds_name):
        """
        Constructor
        """
        self.__uds = DomainSocket(uds_name) if uds_name else None


    # ----------------------------------------------------------------------------------------------------------------

    def connect(self):
        if self.__uds:
            self.__uds.connect(False)


    def close(self):
        if self.__uds:
            self.__uds.close()


    def write(self, message):
        if self.__uds:
            self.__uds.write(message, False)

        else:
            print(message)


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "UDSWriter:{uds:%s}" % self.__uds
