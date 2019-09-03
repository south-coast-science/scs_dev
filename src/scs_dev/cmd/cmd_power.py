"""
Created on 21 Jan 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
    def power_gases(self, enable):                  # switches digital component only
    def power_gps(self, enable):
    def power_modem(self, enable):
    def power_ndir(self, enable):
    def power_opc(self, enable):
        pass

"""

import optparse


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
                                                    "[-o ENABLE] | ENABLE_ALL } [-v]", version="%prog 1.0")

        # optional...
        self.__parser.add_option("--gases", "-g", type="int", nargs=1, action="store", dest="gases",
                                 help="switch gas sensors ON (1) or OFF (0)")

        self.__parser.add_option("--gps", "-p", type="int", nargs=1, action="store", dest="gps",
                                 help="switch GPS receiver ON (1) or OFF (0)")

        self.__parser.add_option("--modem", "-m", type="int", nargs=1, action="store", dest="modem",
                                 help="switch modem ON (1) or OFF (0)")

        self.__parser.add_option("--ndir", "-n", type="int", nargs=1, action="store", dest="ndir",
                                 help="switch NDIR sensor ON (1) or OFF (0)")

        self.__parser.add_option("--opc", "-o", type="int", nargs=1, action="store", dest="opc",
                                 help="switch particulate sensor ON (1) or OFF (0)")

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
                                     self.ndir is not None or self.opc is not None):
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
    def all(self):
        return self.boolean(self.__args[0]) if len(self.__args) > 0 else None


    @property
    def verbose(self):
        return self.__opts.verbose


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdPower:{gases:%s, gps:%s, modem:%s, ndir:%s, opc:%s, all:%s, verbose:%s}" % \
               (self.gases, self.gps, self.modem, self.ndir, self.opc, self.all, self.verbose)
