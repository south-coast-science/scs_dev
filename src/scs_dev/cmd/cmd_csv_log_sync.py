"""
Created on 16 Jan 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_core.data.datetime import LocalizedDatetime


# --------------------------------------------------------------------------------------------------------------------

class CmdCSVLogSync(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog { -s START | -f } [-n] [-a] [-v] TOPIC",
                                              version="%prog 1.0")

        # manual data specification...
        self.__parser.add_option("--start", "-s", type="string", nargs=1, action="store", dest="start",
                                 help="ISO 8601 datetime start")

        # server data specification...
        self.__parser.add_option("--fill", "-f", action="store_true", dest="fill",
                                 help="find logged documents more recent than server latest")

        # output...
        self.__parser.add_option("--nullify", "-n", action="store_true", dest="nullify", default=False,
                                 help="convert empty strings to nulls")

        self.__parser.add_option("--absolute", "-a", action="store_true", dest="absolute", default=False,
                                 help="absolute topic path (default is find from AWS project)")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()



    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.topic is None:
            return False

        if bool(self.start) == bool(self.fill):
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def start(self):
        return None if self.__opts.start is None else LocalizedDatetime.construct_from_iso8601(self.__opts.start)


    @property
    def fill(self):
        return self.__opts.fill


    @property
    def nullify(self):
        return self.__opts.nullify


    @property
    def absolute(self):
        return self.__opts.absolute


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def topic(self):
        return self.__args[0] if len(self.__args) > 0 else None


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdCSVLogSync:{start:%s, fill:%s, nullify:%s, absolute:%s, verbose:%s, topic:%s}" % \
               (self.start, self.fill, self.nullify, self.absolute, self.verbose, self.topic)
