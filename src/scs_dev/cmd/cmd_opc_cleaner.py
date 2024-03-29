"""
Created on 3 May 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_dev import version


# --------------------------------------------------------------------------------------------------------------------

class CmdOPCCleaner(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-n NAME] [-p] [-v]", version=version())

        # identity...
        self.__parser.add_option("--name", "-n", type="string", action="store", dest="name",
                                 help="the name of the OPC configuration")

        # mode...
        self.__parser.add_option("--power", "-p", action="store_true", dest="power", default=False,
                                 help="force OPC power on and off")

        # output...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def name(self):
        return self.__opts.name


    @property
    def power(self):
        return self.__opts.power


    @property
    def verbose(self):
        return self.__opts.verbose


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "CmdOPCCleaner:{name:%s, power:%s, verbose:%s}" % (self.name, self.power, self.verbose)
