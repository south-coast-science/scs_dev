"""
Created on 13 Jul 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdStatusSampler(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [{ -s SEMAPHORE | -i INTERVAL [-n SAMPLES] }] [-x] [-v]",
                                              version="%prog 1.0")

        # optional...
        self.__parser.add_option("--file", "-f", type="string", nargs=1, action="store", dest="file",
                                 help="override default conf file location")

        self.__parser.add_option("--semaphore", "-s", type="string", nargs=1, action="store", dest="semaphore",
                                 help="sampling controlled by SEMAPHORE")

        self.__parser.add_option("--interval", "-i", type="float", nargs=1, action="store", dest="interval",
                                 help="sampling interval in seconds")

        self.__parser.add_option("--samples", "-n", type="int", nargs=1, action="store", dest="samples",
                                 help="number of samples (1 if interval not specified)")

        self.__parser.add_option("--no-shutdown", "-x", action="store_true", dest="no_shutdown", default=False,
                                 help="suppress auto-shutdown")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.__opts.semaphore is not None and self.__opts.interval is not None:
            return False

        if self.__opts.interval is None and self.__opts.samples is not None:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def file(self):
        return self.__opts.file


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
    def no_shutdown(self):
        return self.__opts.no_shutdown


    @property
    def verbose(self):
        return self.__opts.verbose


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdStatusSampler:{file:%s, semaphore:%s, interval:%s, samples:%s, no_shutdown:%s, verbose:%s}" % \
                    (self.file, self.semaphore, self.interval, self.samples, self.no_shutdown, self.verbose)
