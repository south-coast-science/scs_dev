"""
Created on 13 Jul 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import logging
import optparse

from scs_dev import version


# --------------------------------------------------------------------------------------------------------------------

class CmdSampler(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-n NAME] [{ -s SEMAPHORE | -i INTERVAL [-c SAMPLES] }] "
                                                    "[{ -v | -d }]", version=version())

        # identity...
        self.__parser.add_option("--name", "-n", type="string", action="store", dest="name",
                                 help="the name of the sampler configuration")

        # mode...
        self.__parser.add_option("--semaphore", "-s", type="string", action="store", dest="semaphore",
                                 help="sampling controlled by SEMAPHORE")

        self.__parser.add_option("--interval", "-i", type="float", action="store", dest="interval",
                                 help="sampling interval in seconds")

        self.__parser.add_option("--samples", "-c", type="int", action="store", dest="samples",
                                 help="sample count (1 if interval not specified)")

        # output...
        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__parser.add_option("--debug", "-d", action="store_true", dest="debug", default=False,
                                 help="report detailed narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.__opts.semaphore is not None and (self.__opts.interval is not None or self.__opts.samples is not None):
            return False

        if self.__opts.interval is None and self.__opts.samples is not None:
            return False

        if self.verbose and self.debug:
            return False

        return True


    def log_level(self):
        if self.debug:
            return logging.DEBUG

        if self.verbose:
            return logging.INFO

        return logging.ERROR


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def name(self):
        return self.__opts.name


    @property
    def semaphore(self):
        return self.__opts.semaphore


    @property
    def interval(self):
        return 0 if self.__opts.interval is None else self.__opts.interval


    @property
    def samples(self):
        return 1 if self.__opts.interval is None else self.__opts.samples


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def debug(self):
        return self.__opts.debug


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdSampler:{name:%s, semaphore:%s, interval:%s, samples:%s, verbose:%s, debug:%s}" % \
                    (self.name, self.semaphore, self.interval, self.samples, self.verbose, self.debug)
