"""
Created on 19 Nov 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdTopicPublisher(object):
    """unix command line handler"""

    def __init__(self):
        """stuff"""
        self.__parser = optparse.OptionParser(usage="%prog TOPIC [-e] [-v]", version="%prog 1.0")

        # optional...
        self.__parser.add_option("--echo", "-e", action="store_true", dest="echo", default=False, help="report samples to stdout")
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False, help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.topic is None:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def topic(self):
        return self.__args[0] if len(self.__args) > 0 else None


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
        return "CmdTopicPublisher:{topic:%s, echo:%s, verbose:%s, args:%s}" % \
                    (self.topic, self.echo, self.verbose, self.args)
