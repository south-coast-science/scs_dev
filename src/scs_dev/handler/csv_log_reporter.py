"""
Created on 25 Jan 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import sys

from scs_core.csv.csv_log_reader import CSVLogReaderReporter


# --------------------------------------------------------------------------------------------------------------------

class CSVLogReporter(CSVLogReaderReporter):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, script_name, topic_name, verbose):
        """
        Constructor
        """
        self.__script_name = script_name                    # string
        self.__topic_name = topic_name                      # string
        self.__verbose = bool(verbose)                      # bool


    # ----------------------------------------------------------------------------------------------------------------

    def opening(self, cursor):
        if self.__verbose:
            print("%s (%s): reading: %s" % (self.__script_name, self.__topic_name, cursor),
                  file=sys.stderr)
            sys.stderr.flush()


    def closing(self, cursor, read_count):
        if self.__verbose:
            print("%s (%s): closing: %s: read: %s" % (self.__script_name, self.__topic_name, cursor, read_count),
                  file=sys.stderr)
            sys.stderr.flush()


    def timeout(self, cursor, read_count):
        if self.__verbose:
            print("%s (%s): TimeoutError: %s: read: %s" % (self.__script_name, self.__topic_name, cursor, read_count),
                  file=sys.stderr)
            sys.stderr.flush()


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "CSVLogReporter:{script_name:%s, topic_name:%s, verbose:%s}" % \
               (self.__script_name, self.__topic_name, self.__verbose)
