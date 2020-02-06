"""
Created on 13 Jul 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdPSUMonitor(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog { -c | -i INTERVAL } [-x] [-o] [-v]", version="%prog 1.0")

        # compulsory...
        self.__parser.add_option("--interval", "-i", type="float", nargs=1, action="store", dest="interval",
                                 help="sampling interval in seconds")

        self.__parser.add_option("--config-interval", "-c", action="store_true", dest="config_interval", default=False,
                                 help="use PSU config interval specification")

        # optional...
        self.__parser.add_option("--no-shutdown", "-x", action="store_true", dest="no_shutdown", default=False,
                                 help="suppress auto-shutdown")

        self.__parser.add_option("--no-output", "-o", action="store_true", dest="no_output", default=False,
                                 help="suppress reporting on stdout")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if bool(self.__opts.config_interval) == bool(self.__opts.interval):
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def config_interval(self):
        return self.__opts.config_interval


    @property
    def interval(self):
        return self.__opts.interval


    @property
    def shutdown(self):
        return not self.__opts.no_shutdown


    @property
    def output(self):
        return not self.__opts.no_output


    @property
    def verbose(self):
        return self.__opts.verbose


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdPSUMonitor:{config_interval:%s, interval:%s, no_shutdown:%s, no_output:%s, verbose:%s}" % \
                    (self.config_interval, self.interval, self.__opts.no_shutdown, self.__opts.no_output, self.verbose)
