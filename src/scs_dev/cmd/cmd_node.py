"""
Created on 25 Apr 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdNode(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-i] [{ -a | -s }] [-v] [PATH]", version="%prog 1.0")

        # optional...
        self.__parser.add_option("--ignore", "-i", action="store_true", dest="ignore", default=False,
                                 help="ignore data where node is missing")

        self.__parser.add_option("--array", "-a", action="store_true", dest="array", default=False,
                                 help="output the sequence of input JSON documents as array")

        self.__parser.add_option("--sequence", "-s", action="store_true", dest="sequence", default=False,
                                 help="output the contents of the input array node as a sequence")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.array and self.sequence:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def ignore(self):
        return self.__opts.ignore


    @property
    def array(self):
        return self.__opts.array


    @property
    def sequence(self):
        return self.__opts.sequence


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def path(self):
        return self.__args[0] if len(self.__args) > 0 else None


    @property
    def args(self):
        return self.__args


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdNode:{ignore:%s, array:%s, sequence:%s, verbose:%s, path:%s, args:%s}" %  \
               (self.ignore, self.array, self.sequence, self.verbose, self.path, self.args)
