"""
Created on 13 Jul 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_dev import version


# --------------------------------------------------------------------------------------------------------------------

class CmdPSUMonitor(object):
    """unix command line handler"""

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [{ -c | -i INTERVAL } [-x] [-o]] [-v]", version=version())

        # mode...
        self.__parser.add_option("--config-interval", "-c", action="store_true", dest="config_interval", default=False,
                                 help="use PSU configuration interval specification")

        self.__parser.add_option("--interval", "-i", type="float", action="store", dest="interval",
                                 default=None, help="sampling interval in seconds")

        # optional...
        self.__parser.add_option("--ignore-standby", "-x", action="store_true", dest="ignore_standby", default=False,
                                 help="ignore PSU standby status")

        # output...
        self.__parser.add_option("--no-output", "-o", action="store_true", dest="no_output", default=False,
                                 help="suppress reporting on stdout")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.config_interval and self.__opts.interval is not None:
            return False

        if self.single_shot_mode() and (self.ignore_standby or self.__opts.no_output):
            return False

        return True


    def single_shot_mode(self):
        return not self.config_interval and self.__opts.interval is None


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def config_interval(self):
        return self.__opts.config_interval


    @property
    def interval(self):
        return 0 if self.__opts.interval is None else self.__opts.interval


    @property
    def ignore_standby(self):
        return self.__opts.ignore_standby


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
        return "CmdPSUMonitor:{config_interval:%s, interval:%s, ignore_standby:%s, no_output:%s, " \
               "verbose:%s}" % \
                    (self.config_interval, self.__opts.interval, self.ignore_standby, self.__opts.no_output,
                     self.verbose)
