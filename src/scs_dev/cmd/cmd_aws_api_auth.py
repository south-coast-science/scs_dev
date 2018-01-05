"""
Created on 18 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

example document:
{"org-id": "south-coast-science-test-user", "api-key": "9fdfb841-3433-45b8-b223-3f5a283ceb8e"}
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdAWSAPIAuth(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-s API_KEY] [-v]", version="%prog 1.0")

        # optional...
        self.__parser.add_option("--set", "-s", type="string", nargs=1, action="store", dest="api_key",
                                 help="set API key")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def set(self):
        return self.__opts.api_key is not None


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def api_key(self):
        return self.__opts.api_key


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def args(self):
        return self.__args


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "CmdAWSAPIAuth:{api_key:%s, verbose:%s, args:%s}" % (self.api_key, self.verbose, self.args)
