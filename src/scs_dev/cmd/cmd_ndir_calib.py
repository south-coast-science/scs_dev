"""
Created on 17 Feb 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdNDIRCalib(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [{ -d | -s PATH VALUE | -r }] [-v]", version="%prog 1.0")

        # optional...
        self.__parser.add_option("--default", "-d", action="store_true", dest="default",
                                 help="load the default settings")

        self.__parser.add_option("--set", "-s", type="string", nargs=2, action="store", dest="set",
                                 help="set the named field to VALUE")

        self.__parser.add_option("--restart", "-r", action="store_true", dest="restart",
                                 help="restart sampling with updated values")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        param_count = 0

        if self.default is not None:
            param_count += 1

        if self.__opts.set is not None:
            param_count += 1

        if self.restart is not None:
            param_count += 1

        if param_count > 1:
            return False

        return True


    def set(self):
        return self.__opts.set is not None


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def default(self):
        return self.__opts.default


    @property
    def path(self):
        if self.set():
            return self.__opts.set[0]

        return None


    @property
    def value(self):
        if self.set():
            return self.__opts.set[1]

        return None


    @property
    def restart(self):
        return self.__opts.restart


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
        return "CmdNDIRCalib:{default:%s, set:%s, restart:%s, verbose:%s, args:%s}" % \
               (self.default, self.__opts.set, self.restart, self.verbose, self.args)
