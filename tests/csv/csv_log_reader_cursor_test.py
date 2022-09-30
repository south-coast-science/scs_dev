#!/usr/bin/env python3

"""
Created on 14 Jan 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import requests

from scs_core.aws.manager.byline_manager import BylineManager

from scs_core.csv.csv_log_reader import CSVLogReader, CSVLogQueueBuilder
from scs_core.csv.csv_logger_conf import CSVLoggerConf

from scs_core.data.datetime import LocalizedDatetime

from scs_host.sys.host import Host
from scs_core.sys.system_id import SystemID


# --------------------------------------------------------------------------------------------------------------------

start_iso = '2020-01-20T09:50:00Z'
topic_name = 'climate'
topic_path = 'south-coast-science-dev/development/loc/1/climate'
rec_field = 'rec'

start = LocalizedDatetime.construct_from_iso8601(start_iso)
start_datetime = start.datetime

print("start_datetime: %s" % start_datetime)
print("-")

conf = CSVLoggerConf.load(Host)
print(conf)

system_id = SystemID.load(Host)
print(system_id)

manager = BylineManager(requests)
print(manager)

queue_builder = CSVLogQueueBuilder(topic_name, topic_path, manager, system_id, conf)
print(queue_builder)
print("-")


reader = CSVLogReader(queue_builder)
print(reader)
print("-")

reader.start()

try:
    reader.join()
except KeyboardInterrupt:
    pass
