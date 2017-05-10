"""
Created on 23 Mar 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_core.osio.config.project import Project


# --------------------------------------------------------------------------------------------------------------------

class CmdOSIOMQTTClient(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [TOPIC_1 .. TOPIC_N] [-c { C | G | P | S | X }] [-p [-e]] "
                                                    "[-v]", version="%prog 1.0")

        # optional...
        self.__parser.add_option("--channel", "-c", type="string", nargs=1, action="store", dest="channel",
                                 help="subscribe to channel")

        self.__parser.add_option("--pub", "-p", action="store_true", dest="publish", default=False,
                                 help="publish publication documents from stdin")

        self.__parser.add_option("--echo", "-e", action="store_true", dest="echo", default=False,
                                 help="echo stdin to stdout (if publishing)")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.echo and not self.publish:
            return False

        if self.channel and not Project.is_valid_channel(self.channel):
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def topics(self):
        return self.__args


    @property
    def channel(self):
        return self.__opts.channel


    @property
    def publish(self):
        return self.__opts.publish


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
        return "CmdOSIOMQTTClient:{topics:%s, channel:%s, publish:%s, echo:%s, verbose:%s, args:%s}" % \
               (self.topics, self.channel, self.publish, self.echo, self.verbose, self.args)
