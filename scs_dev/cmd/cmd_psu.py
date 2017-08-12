"""
Created on 10 Aug 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdPSU(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-p] [-v] [CMD [PARAM]]", version="%prog 1.0")

        # optional...
        self.__parser.add_option("--prompt", "-p", action="store_true", dest="prompt", default=False,
                                 help="display prompt on stderr (if no CMD)")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def has_psu_command(self):
        return bool(self.psu_command)


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def psu_command(self):
        return ' '.join(self.__args) if len(self.__args) > 0 else None


    @property
    def prompt(self):
        return self.__opts.prompt


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def args(self):
        return self.__args


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "CmdPSU:{prompt:%s, verbose:%s, args:%s}" % \
                    (self.prompt, self.verbose, self.args)
