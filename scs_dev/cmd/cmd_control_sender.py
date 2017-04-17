"""
Created on 17 Apr 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdControlSender(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog TAG SERIAL_NUMBER CMD [PARAMS] [-v]",
                                              version="%prog 1.0")

        # optional...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        return len(self.__args) > 2


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def tag(self):
        return self.__args[0] if len(self.__args) > 0 else None


    @property
    def serial_number(self):
        return self.__args[1] if len(self.__args) > 1 else None


    @property
    def command(self):
        return self.__args[2] if len(self.__args) > 2 else None


    @property
    def params(self):
        return self.__args[3:] if len(self.__args) > 3 else []


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
        return "CmdControlSender:{tag:%s, serial_number:%s, command:%s, params:%s, verbose:%s, args:%s}" % \
                    (self.tag, self.serial_number, self.command, self.params, self.verbose, self.args)
