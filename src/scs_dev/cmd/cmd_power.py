"""
Created on 21 Jan 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_core.led.led import LED
from scs_dev import version


# --------------------------------------------------------------------------------------------------------------------

class CmdPower(object):
    """unix command line handler"""


    @classmethod
    def is_valid_boolean(cls, value):
        if value is None:
            return True

        try:
            boolean = int(value)
            return boolean == 0 or boolean == 1
        except (TypeError, ValueError):
            return False


    @classmethod
    def boolean(cls, value):
        try:
            return bool(int(value))
        except (TypeError, ValueError):
            return None


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog { [-g ENABLE] [-p ENABLE] [-m ENABLE] [-n ENABLE] "
                                                    "[-o ENABLE] [-l { R | A | G | 0 }] | ENABLE_ALL } [-v]",
                                              version=version())

        # optional...
        self.__parser.add_option("--gases", "-g", type="int", action="store", dest="gases",
                                 help="switch gas sensors ON (1) or OFF (0)")

        self.__parser.add_option("--gps", "-p", type="int", action="store", dest="gps",
                                 help="switch GPS receiver ON (1) or OFF (0)")

        self.__parser.add_option("--modem", "-m", type="int", action="store", dest="modem",
                                 help="switch modem ON (1) or OFF (0)")

        self.__parser.add_option("--ndir", "-n", type="int", action="store", dest="ndir",
                                 help="switch NDIR sensor ON (1) or OFF (0)")

        self.__parser.add_option("--opc", "-o", type="int", action="store", dest="opc",
                                 help="switch particulate sensor ON (1) or OFF (0)")

        self.__parser.add_option("--led", "-l", type="string", action="store", dest="led",
                                 help="set the LED to the given colour")

        # output...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if not self.is_valid_boolean(self.__opts.gases) or not self.is_valid_boolean(self.__opts.gps) or \
                not self.is_valid_boolean(self.__opts.modem) or not self.is_valid_boolean(self.__opts.ndir) or \
                not self.is_valid_boolean(self.__opts.opc):
            return False

        if len(self.__args) > 0 and not self.is_valid_boolean(self.__args[0]):
            return False

        if self.all is not None and (self.gases is not None or self.gps is not None or self.modem is not None or
                                     self.ndir is not None or self.opc is not None or self.led is not None):
            return False

        if self.led is not None and not LED.is_valid_colour(self.led):
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def gases(self):
        return self.boolean(self.__opts.gases)


    @property
    def gps(self):
        return self.boolean(self.__opts.gps)


    @property
    def modem(self):
        return self.boolean(self.__opts.modem)


    @property
    def ndir(self):
        return self.boolean(self.__opts.ndir)


    @property
    def opc(self):
        return self.boolean(self.__opts.opc)


    @property
    def led(self):
        return self.__opts.led


    @property
    def all(self):
        return self.boolean(self.__args[0]) if len(self.__args) > 0 else None


    @property
    def verbose(self):
        return self.__opts.verbose


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdPower:{gases:%s, gps:%s, modem:%s, ndir:%s, opc:%s, led:%s, all:%s, verbose:%s}" % \
               (self.gases, self.gps, self.modem, self.ndir, self.opc, self.led, self.all, self.verbose)
