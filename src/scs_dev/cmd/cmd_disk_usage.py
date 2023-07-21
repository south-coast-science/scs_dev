"""
Created on 20 May 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_dev import version


# --------------------------------------------------------------------------------------------------------------------

class CmdDiskUsage(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-v] { -c | PATH }", version=version())

        # optional...
        self.__parser.add_option("--csv", "-c", action="store_true", dest="csv", default=False,
                                 help="use PATH specified by csv_logger_conf")

        # output...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        # build...
        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if bool(self.csv) == bool(self.path):
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def csv(self):
        return self.__opts.csv


    @property
    def path(self):
        return self.__args[0] if len(self.__args) > 0 else None


    @property
    def verbose(self):
        return self.__opts.verbose


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdDiskUsage:{csv:%s, path:%s, verbose:%s}" % (self.csv, self.path, self.verbose)
