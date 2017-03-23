"""
Created on 2 Aug 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdCSVWriter(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [FILENAME] [-a] [-e] [-v]", version="%prog 1.0")

        # optional...
        self.__parser.add_option("--append", "-a", action="store_true", dest="append", default=False,
                                 help="if FILENAME is given and the file exists, append rows")

        self.__parser.add_option("--echo", "-e", action="store_true", dest="echo", default=False,
                                 help="echo stdin to stdout")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def filename(self):
        return self.__args[0] if len(self.__args) > 0 else None


    @property
    def append(self):
        return self.__opts.append


    @property
    def echo(self):
        return self.__opts.echo


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def args(self):
        return self.__args


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "CmdCSVWriter:{filename:%s, echo:%s, append:%s, verbose:%s, args:%s}" % \
                    (self.filename, self.append, self.echo, self.verbose, self.args)
