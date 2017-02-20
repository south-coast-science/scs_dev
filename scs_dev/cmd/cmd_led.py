"""
Created on 20 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_dfe.climate.led import LED

# --------------------------------------------------------------------------------------------------------------------

class CmdLED(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-s { R | G | O | 0 }] [-v]", version="%prog 1.0")

        # optional...
        self.__parser.add_option("--set", "-s", type="string", nargs=1, action="store", dest="colour",
                                 help="colour")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.colour is not None:
            return self.colour in LED.STATES

        return True


    # ----------------------------------------------------------------------------------------------------------------

    def set(self):
        return self.colour is not None


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def colour(self):
        return self.__opts.colour


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
        return "CmdLED:{colour:%s, verbose:%s, args:%s}" % \
                    (self.colour, self.verbose, self.args)
