"""
Created on 2 Aug 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdCSVReader(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-a] [-v] [FILENAME]", version="%prog 1.0")

        # optional...
        self.__parser.add_option("--array", "-a", action="store_true", dest="array", default=False,
                                 help="output JSON documents as array instead of a sequence")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def array(self):
        return self.__opts.array


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def filename(self):
        return self.__args[0] if len(self.__args) > 0 else None


    @property
    def args(self):
        return self.__args


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdCSVReader:{array:%s, verbose:%s, filename:%s, args:%s}" % \
               (self.array, self.verbose, self.filename, self.args)
