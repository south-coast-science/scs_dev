"""
Created on 25 Jan 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import sys

from scs_core.csv.csv_log_reader import CSVLogReporter


# --------------------------------------------------------------------------------------------------------------------

class CSVLoggerReporter(CSVLogReporter):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, script_name, topic_subject, verbose):
        """
        Constructor
        """
        self.__script_name = script_name                    # string
        self.__topic_subject = topic_subject                # string
        self.__verbose = bool(verbose)                      # bool


    # ----------------------------------------------------------------------------------------------------------------

    def timeline_start(self, timeline_start):
        if self.__verbose:
            print("%s (%s): timeline_start: %s" % (self.__script_name, self.__topic_subject, timeline_start),
                  file=sys.stderr)
            sys.stderr.flush()


    def opening(self, cursor):
        if self.__verbose:
            print("%s (%s): reading: %s" % (self.__script_name, self.__topic_subject, cursor),
                  file=sys.stderr)
            sys.stderr.flush()


    def closing(self, cursor, read_count):
        if self.__verbose:
            print("%s (%s): closing: %s: read: %s" % (self.__script_name, self.__topic_subject, cursor, read_count),
                  file=sys.stderr)
            sys.stderr.flush()


    def timeout(self, cursor, read_count):
        if self.__verbose:
            print("%s (%s): TimeoutError: %s: read: %s" %
                  (self.__script_name, self.__topic_subject, cursor, read_count),
                  file=sys.stderr)
            sys.stderr.flush()


    def exception(self, ex):
        if self.__verbose:
            print("%s (%s): %s" % (self.__script_name, self.__topic_subject, ex),
                  file=sys.stderr)
            sys.stderr.flush()


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "CSVLoggerReporter:{script_name:%s, topic_subject:%s, verbose:%s}" % \
               (self.__script_name, self.__topic_subject, self.__verbose)
