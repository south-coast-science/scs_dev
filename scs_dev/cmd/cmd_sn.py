"""
Created on 13 Jul 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdSN(object):
    """unix command line handler"""

    def __init__(self):
        """stuff"""
        self.__parser = optparse.OptionParser(usage="%prog -s SENSOR [-i INTERVAL] [-n SAMPLES] [-v]", version="%prog 1.0")

        # compulsory...
        self.__parser.add_option("--sn", "-s", type="int", nargs=1, action="store", dest="sn",
                                 help="sensor number (1 to 4)")

        # optional...
        self.__parser.add_option("--interval", "-i", type="float", nargs=1, action="store", dest="interval", default=1.0,
                                 help="sampling interval in seconds (default 1.0)")

        self.__parser.add_option("--samples", "-n", type="int", nargs=1, action="store", default=0, dest="samples",
                                 help="number of samples (default for-ever = 0)")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.sn is None:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def sn(self):
        return self.__opts.sn


    @property
    def interval(self):
        return self.__opts.interval


    @property
    def samples(self):
        return self.__opts.samples


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
        return "CmdSN:{sn:%s, interval:%0.1f, samples:%d, verbose:%s, args:%s}" % \
                    (self.sn, self.interval, self.samples, self.verbose, self.args)
