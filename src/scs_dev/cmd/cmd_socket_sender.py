"""
Created on 13 Jul 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdSocketSender(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog HOSTNAME [-p PORT] [-e] [-v]", version="%prog 1.0")

        # optional
        self.__parser.add_option("--port", "-p", type="int", nargs=1, action="store", default=2000, dest="port",
                                 help="socket port [default 2000]")

        self.__parser.add_option("--echo", "-e", action="store_true", dest="echo", default=False,
                                 help="echo stdin to stdout")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.hostname is None:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def hostname(self):
        return self.__args[0] if len(self.__args) > 0 else None


    @property
    def port(self):
        return self.__opts.port


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
        return "CmdSocketSender:{hostname:%s, port:%d, echo:%s, verbose:%s, args:%s}" % \
                    (self.hostname, self.port, self.echo, self.verbose, self.args)
