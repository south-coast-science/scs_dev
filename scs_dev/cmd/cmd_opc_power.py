"""
Created on 21 Jan 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdOPCPower(object):
    """unix command line handler"""

    def __init__(self):
        """stuff"""
        self.__parser = optparse.OptionParser(usage="%prog 1 | 0 [-v]", version="%prog 1.0")

        # optional...
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
        try:
            return bool(int(self.__args[0]))
        except RuntimeError:
            return None


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def args(self):
        return self.__args


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdOPCPower:{power:%d, verbose:%s, args:%s}" % \
                    (self.power, self.verbose, self.args)
