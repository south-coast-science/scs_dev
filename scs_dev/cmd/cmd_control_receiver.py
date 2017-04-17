"""
Created on 17 Apr 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdControlReceiver(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [TAG SERIAL_NUMBER] [-r] [-e] [-v]", version="%prog 1.0")

        # optional...
        self.__parser.add_option("--receipt", "-r", action="store_true", dest="receipt", default=False,
                                 help="print receipt to stdout")

        self.__parser.add_option("--echo", "-e", action="store_true", dest="echo", default=False,
                                 help="echo data to stdout")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        return len(self.__args) == 0 or len(self.__args) == 2


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def tag(self):
        return self.__args[0] if len(self.__args) > 0 else None


    @property
    def serial_number(self):
        return self.__args[1] if len(self.__args) > 1 else None


    @property
    def receipt(self):
        return self.__opts.receipt


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

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdControlReceiver:{tag:%s, serial_number:%s, receipt:%s, verbose:%s, args:%s}" % \
                    (self.tag, self.serial_number, self.receipt, self.verbose, self.args)
