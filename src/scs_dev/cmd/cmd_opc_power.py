"""
Created on 17 May 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdOPCPower(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-f FILE] { 1 | 0 } [-v]", version="%prog 1.0")

        # optional...
        self.__parser.add_option("--file", "-f", type="string", nargs=1, action="store", dest="file",
                                 help="override default conf file location")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.power is None:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def power(self):
        if len(self.__args) > 0:
            try:
                return bool(int(self.__args[0]))
            except RuntimeError:
                return None

        return None


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def file(self):
        return self.__opts.file


    @property
    def verbose(self):
        return self.__opts.verbose


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdOPCPower:{file:%s, power:%d, verbose:%s}" % (self.file, self.power, self.verbose)
