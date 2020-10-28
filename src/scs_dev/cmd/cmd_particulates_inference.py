"""
Created on 22 Sep 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdParticulatesInference(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog -p PARTICULATES_PATH -c CLIMATE_PATH [-u UDS] [-v]",
                                              version="%prog 1.0")

        # compulsory...
        self.__parser.add_option("--particulates", "-p", type="string", nargs=1, action="store", dest="particulates",
                                 help="path to particulates node")

        self.__parser.add_option("--climate", "-c", type="string", nargs=1, action="store", dest="climate",
                                 help="path to climate node")

        # optional...
        self.__parser.add_option("--uds", "-u", type="string", nargs=1, action="store", dest="uds",
                                 help="UDS for inference server (default is ~/SCS/pipes/lambda-model-pmx-s1.uds)")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.__opts.particulates is None or self.__opts.climate is None:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def particulates(self):
        return self.__opts.particulates


    @property
    def climate(self):
        return self.__opts.climate


    @property
    def uds(self):
        return self.__opts.uds


    @property
    def verbose(self):
        return self.__opts.verbose


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdParticulatesInference:{particulates:%s, climate:%s, uds:%s, verbose:%s}" % \
                    (self.particulates, self.climate, self.uds, self.verbose)
