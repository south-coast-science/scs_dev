"""
Created on 25 Apr 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdNode(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog PATH [-i] [-v]", version="%prog 1.0")

        # optional...
        self.__parser.add_option("--ignore", "-i", action="store_true", dest="ignore", default=False,
                                 help="ignore data where node is missing")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.path is None:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def path(self):
        return self.__args[0] if len(self.__args) > 0 else None


    @property
    def ignore(self):
        return self.__opts.ignore


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
        return "CmdNode:{ignore:%s, verbose:%s, args:%s}" %  (self.ignore, self.verbose, self.args)
