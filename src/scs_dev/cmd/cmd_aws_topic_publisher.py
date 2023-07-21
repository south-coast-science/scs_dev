"""
Created on 6 Oct 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_core.aws.config.project import Project
from scs_dev import version


# --------------------------------------------------------------------------------------------------------------------

class CmdAWSTopicPublisher(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog { -t TOPIC_PATH | -c { C | G | P | S | X } } "
                                                    "[-p UDS_PUB] [-v]", version=version())

        # compulsory...
        self.__parser.add_option("--topic", "-t", type="string", action="store", dest="topic",
                                 help="topic path")

        self.__parser.add_option("--channel", "-c", type="string", action="store", dest="channel",
                                 help="publication channel")

        # output...
        self.__parser.add_option("--pub", "-p", type="string", action="store", dest="uds_pub",
                                 default=None, help="write publications to UDS instead of stdout")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        # build...
        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if bool(self.topic) == bool(self.channel):
            return False

        if not bool(self.topic) and not bool(self.channel):
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
    def uds_pub(self):
        return self.__opts.uds_pub


    @property
    def verbose(self):
        return self.__opts.verbose


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdAWSTopicPublisher:{topic:%s, channel:%s, verbose:%s}" % (self.topic, self.channel, self.verbose)
