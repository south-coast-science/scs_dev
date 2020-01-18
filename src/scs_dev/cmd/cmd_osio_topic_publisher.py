"""
Created on 19 Nov 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

https://opensensorsio.helpscoutdocs.com/article/84-overriding-timestamp-information-in-message-payload
"""

import optparse

from scs_core.osio.config.project import Project


# --------------------------------------------------------------------------------------------------------------------

class CmdOSIOTopicPublisher(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog { -t TOPIC_PATH | -c { C | G | P | S | X } } "
                                                    "[-q PRIORITY] [-o] [-v]", version="%prog 1.0")

        # compulsory...
        self.__parser.add_option("--topic", "-t", type="string", nargs=1, action="store", dest="topic",
                                 help="topic path")

        self.__parser.add_option("--channel", "-c", type="string", nargs=1, action="store", dest="channel",
                                 help="publication channel")

        # optional...
        self.__parser.add_option("--queue-priority", "-q", type="int", nargs=1, action="store", dest="priority",
                                 default=1, help="queue priority (default 1)")

        self.__parser.add_option("--override", "-o", action="store_true", dest="override", default=False,
                                 help="override OSIO reception datetime")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

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
    def priority(self):
        return self.__opts.priority


    @property
    def override(self):
        return self.__opts.override


    @property
    def verbose(self):
        return self.__opts.verbose


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdOSIOTopicPublisher:{topic:%s, channel:%s, priority:%s, override:%s, verbose:%s}" % \
                    (self.topic, self.channel, self.priority, self.override, self.verbose)
