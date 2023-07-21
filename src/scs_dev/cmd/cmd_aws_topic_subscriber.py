"""
Created on 19 Nov 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_core.aws.config.project import Project
from scs_dev import version


# --------------------------------------------------------------------------------------------------------------------

class CmdAWSTopicSubscriber(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog { -t TOPIC_PATH | -c { C | G | P | S | X } } [-s UDS_SUB] "
                                                    "[-v]", version=version())

        # compulsory...
        self.__parser.add_option("--topic", "-t", type="string", action="store", dest="topic",
                                 help="topic path")

        self.__parser.add_option("--channel", "-c", type="string", action="store", dest="channel",
                                 help="publication channel")

        # optional...
        self.__parser.add_option("--sub", "-s", type="string", action="store", dest="uds_sub",
                                 help="read subscriptions from UDS instead of stdin")

        # output...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        # build...
        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if bool(self.topic) == bool(self.channel):
            return False

        if self.channel and not Project.is_valid_channel(self.channel):
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def topic(self):
        return self.__opts.topic


    @property
    def channel(self):
        return self.__opts.channel


    @property
    def uds_sub(self):
        return self.__opts.uds_sub


    @property
    def verbose(self):
        return self.__opts.verbose


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdAWSTopicSubscriber:{topic:%s, channel:%s, uds_sub:%s, verbose:%s}" % \
               (self.topic, self.channel, self.uds_sub, self.verbose)
