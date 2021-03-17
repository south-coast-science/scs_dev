#!/usr/bin/env python3

"""
Created on 14 Jan 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

from scs_core.csv.csv_logger_conf import CSVLoggerConf

from scs_core.data.datetime import LocalizedDatetime

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

start_iso = '2020-01-20T09:50:00Z'
topic_subject = 'climate'
rec_field = 'rec'

start = LocalizedDatetime.construct_from_iso8601(start_iso)
start_datetime = start.datetime

print("start_datetime: %s" % start_datetime)
print("-")

conf = CSVLoggerConf.load(Host)
print(conf)

log = conf.csv_log(topic_subject, timeline_start=start_datetime)
print(log)
