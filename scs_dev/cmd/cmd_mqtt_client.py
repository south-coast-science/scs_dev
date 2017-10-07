"""
Created on 23 Mar 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdMQTTClient(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-p UDS_PUB] "
                                                    "[-s] { -c { C | G | P | S | X } (UDS_SUB_1) | "
                                                    "[SUB_TOPIC_1 (UDS_SUB_1) .. SUB_TOPIC_N (UDS_SUB_N)] }"
                                                    "[-e] [-v]", version="%prog 1.0")

        # optional...
        self.__parser.add_option("--pub-addr", "-p", type="string", nargs=1, action="store", dest="uds_pub_addr",
                                 help="read publications from UDS instead of stdin")

        self.__parser.add_option("--sub", "-s", action="store_true", dest="uds_sub",
                                 help="write subscriptions to UDS instead of stdout")

        self.__parser.add_option("--channel", "-c", type="string", nargs=1, action="store", dest="channel",
                                 help="subscribe to channel")

        self.__parser.add_option("--echo", "-e", action="store_true", dest="echo", default=False,
                                 help="echo input to stdout (if writing subscriptions to DomainSocket)")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.echo and not self.__opts.uds_sub:
            return False

        if self.channel is None:
            if self.__opts.uds_sub and len(self.__args) % 2 != 0:
                return False

        else:
            if self.__opts.uds_sub and len(self.__args) != 1:
                return False

            if not self.__opts.uds_sub and len(self.__args) != 0:
                return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def subscriptions(self):
        subscriptions = []

        if self.__opts.uds_sub:
            for i in range(0, len(self.__args), 2):
                subscriptions.append(Subscription(self.__args[i], self.__args[i + 1]))
        else:
            for i in range(len(self.__args)):
                subscriptions.append(Subscription(self.__args[i]))

        return subscriptions


    @property
    def channel(self):
        return self.__opts.channel


    @property
    def channel_uds(self):
        if self.channel is None or not self.__opts.uds_sub:
            return None

        return self.__args[0]


    @property
    def uds_pub_addr(self):
        return self.__opts.uds_pub_addr


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
        subscriptions = '[' + ', '.join(str(subscription) for subscription in self.subscriptions) + ']'

        return "CmdMQTTClient:{subscriptions:%s, channel:%s, uds_pub_addr:%s, echo:%s, verbose:%s, args:%s}" % \
               (subscriptions, self.channel, self.uds_pub_addr, self.echo, self.verbose, self.args)


# --------------------------------------------------------------------------------------------------------------------

class Subscription(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, topic, address=None):
        """
        Constructor
        """
        self.__topic = topic            # string        topic path
        self.__address = address        # string        DomainSocket address


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def topic(self):
        return self.__topic


    @property
    def address(self):
        return self.__address


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "Subscription:{topic:%s, address:%s}" % (self.topic, self.address)
