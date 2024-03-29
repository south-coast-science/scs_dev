"""
Created on 16 Apr 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_dev import version


# --------------------------------------------------------------------------------------------------------------------

class CmdCSVLogger(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-a] [-e] [-v] TOPIC", version=version())

        # mode...
        self.__parser.add_option("--absolute", "-a", action="store_true", dest="absolute", default=False,
                                 help="absolute topic path (default is find from AWS project)")

        # output...
        self.__parser.add_option("--echo", "-e", action="store_true", dest="echo", default=False,
                                 help="echo stdin to stdout (mediated by storage and byline)")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if len(self.__args) < 1:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def absolute(self):
        return self.__opts.absolute


    @property
    def echo(self):
        return self.__opts.echo


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def topic(self):
        return self.__args[0] if len(self.__args) > 0 else None


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdCSVLogger:{absolute:%s, echo:%s, verbose:%s, topic_subject:%s}" % \
               (self.absolute, self.echo, self.verbose, self.topic)
