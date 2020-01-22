"""
Created on 16 Jan 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse

from scs_core.data.localized_datetime import LocalizedDatetime


# --------------------------------------------------------------------------------------------------------------------

class CmdCSVLogSync(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog { -t TOPIC_NAME -s START | -f } [-n]] "
                                                    "[-p UDS_PUB] [-v]", version="%prog 1.0")

        # manual data specification...
        self.__parser.add_option("--topic", "-t", type="string", nargs=1, action="store", dest="topic_name",
                                 help="topic name")

        self.__parser.add_option("--start", "-s", type="string", nargs=1, action="store", dest="start",
                                 help="ISO 8601 datetime start")

        # server data specification...
        self.__parser.add_option("--fill", "-f", action="store_true", dest="fill",
                                 help="find logged documents more recent than server latest")

        # output...
        self.__parser.add_option("--nullify", "-n", action="store_true", dest="nullify", default=False,
                                 help="convert empty strings to nulls")

        self.__parser.add_option("--wrapper", "-w", action="store_true", dest="wrapper", default=False,
                                 help="use topic wrapper")

        self.__parser.add_option("--pub", "-p", type="string", nargs=1, action="store", dest="uds_pub",
                                 default=None, help="write documents to UDS instead of stdout")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()



    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if bool(self.topic_name) == bool(self.fill):
            return False

        if self.topic_name is not None and self.start is None:
            return False

        return True


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def topic_name(self):
        return self.__opts.topic_name


    @property
    def start(self):
        return None if self.__opts.start is None else LocalizedDatetime.construct_from_iso8601(self.__opts.start)


    @property
    def fill(self):
        return self.__opts.fill


    @property
    def nullify(self):
        return self.__opts.nullify


    @property
    def wrapper(self):
        return self.__opts.wrapper


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
        return "CmdCSVLogSync:{topic_name:%s, start:%s, fill:%s, nullify:%s, wrapper:%s, uds_pub:%s, verbose:%s}" % \
               (self.topic_name, self.start, self.fill, self.nullify, self.wrapper, self.uds_pub, self.verbose)