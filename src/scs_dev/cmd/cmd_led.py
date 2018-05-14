"""
Created on 20 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_dfe.display.led import LED


# --------------------------------------------------------------------------------------------------------------------

class CmdLED(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog { -s { R | A | G | 0 } | "
                                                    "-f { R | A | G | 0 } { R | A | G | 0 } } [-u UDS] [-v]",
                                              version="%prog 1.0")

        # compulsory...
        self.__parser.add_option("--solid", "-s", type="string", nargs=1, action="store", dest="solid",
                                 help="continuous colour")

        self.__parser.add_option("--flash", "-f", type="string", nargs=2, action="store", dest="flash",
                                 help="flashing colours")

        # optional...
        self.__parser.add_option("--uds", "-u", type="string", nargs=1, action="store", dest="uds",
                                 help="send to Unix domain socket instead of stdout")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if bool(self.solid) == bool(self.flash):
            return False

        if self.solid is not None:
            return LED.is_valid_colour(self.solid)

        if self.flash is not None:
            return LED.is_valid_colour(self.flash[0]) and LED.is_valid_colour(self.flash[1])

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def solid(self):
        return self.__opts.solid


    @property
    def flash(self):
        return self.__opts.flash


    @property
    def uds(self):
        return self.__opts.uds


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
        return "CmdLED:{solid:%s, flash:%s, uds:%s, verbose:%s, args:%s}" % \
               (self.solid, self.flash, self.uds, self.verbose, self.args)
