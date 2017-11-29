"""
Created on 13 Jul 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdSocketReceiver(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-p PORT] [-v]", version="%prog 1.0")

        # optional...
        self.__parser.add_option("--port", "-p", type="int", nargs=1, action="store", default=2000, dest="port",
                                 help="socket port (default 2000)")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def port(self):
        return self.__opts.port


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def args(self):
        return self.__args


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "CmdSocketReceiver:{port:%d, verbose:%s, args:%s}" % \
                    (self.port, self.verbose, self.args)
