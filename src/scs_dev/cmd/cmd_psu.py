"""
Created on 10 Aug 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_dev import version


# --------------------------------------------------------------------------------------------------------------------

class CmdPSU(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog { -i | CMD [PARAM] } [-v]", version=version())

        # mode...
        self.__parser.add_option("--interactive", "-i", action="store_true", dest="interactive", default=False,
                                 help="interactive mode")

        # output...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if bool(self.interactive) == bool(self.psu_command):
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    def has_psu_command(self):
        return bool(self.psu_command)


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def psu_command(self):
        return ' '.join(self.__args) if len(self.__args) > 0 else None


    @property
    def interactive(self):
        return self.__opts.interactive


    @property
    def verbose(self):
        return self.__opts.verbose


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdPSU:{interactive:%s, psu_command:%s, verbose:%s}" % \
            (self.interactive, self.psu_command, self.verbose)
