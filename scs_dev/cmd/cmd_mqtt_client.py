"""
Created on 23 Mar 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# TODO: remove --pub flag

# --------------------------------------------------------------------------------------------------------------------

class CmdMQTTClient(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog { -p [-e] | -s TOPIC } [-v]", version="%prog 1.0")

        # optional...
        self.__parser.add_option("--pub", "-p", action="store_true", dest="publish", default=False,
                                 help="publish documents from stdin")

        self.__parser.add_option("--echo", "-e", action="store_true", dest="echo", default=False,
                                 help="echo stdin to stdout")

        self.__parser.add_option("--sub", "-s", type="string", nargs=1, dest="topic", default=False,
                                 help="subscribe to TOPIC")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if not self.publish and not self.subscribe():
            return False

        if self.echo and not self.publish:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    def subscribe(self):
        return self.topic is not None


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def publish(self):
        return self.__opts.publish


    @property
    def topic(self):
        return self.__opts.topic


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
        return "CmdMQTTClient:{publish:%s, topic:%s, echo:%s, verbose:%s, args:%s}" % \
                    (self.publish, self.topic, self.echo, self.verbose, self.args)
