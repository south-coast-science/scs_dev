"""
Created on 2 Aug 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdCSVWriter(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [{ -a | -x }] [-e] [-v] [FILENAME]", version="%prog 1.0")

        # optional...
        self.__parser.add_option("--append", "-a", action="store_true", dest="append", default=False,
                                 help="append rows to existing file")

        self.__parser.add_option("--exclude-header", "-x", action="store_true", dest="exclude_header", default=False,
                                 help="do not write the header row to stdout")

        self.__parser.add_option("--echo", "-e", action="store_true", dest="echo", default=False,
                                 help="echo stdin to stdout")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.append and self.exclude_header:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def append(self):
        return self.__opts.append


    @property
    def exclude_header(self):
        return self.__opts.exclude_header


    @property
    def echo(self):
        return self.__opts.echo


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def filename(self):
        return self.__args[0] if len(self.__args) > 0 else None


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdCSVWriter:{append:%s, exclude_header:%s, echo:%s, verbose:%s, filename:%s}" % \
                    (self.append, self.exclude_header, self.echo, self.verbose, self.filename)
