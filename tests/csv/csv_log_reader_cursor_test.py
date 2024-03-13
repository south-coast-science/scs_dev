#!/usr/bin/env python3

"""
Created on 14 Jan 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

from scs_core.aws.manager.byline.byline_finder import BylineFinder

from scs_core.aws.security.cognito_device import CognitoDeviceCredentials
from scs_core.aws.security.cognito_login_manager import CognitoLoginManager

from scs_core.csv.csv_log_reader import CSVLogReader, CSVLogQueueBuilder
from scs_core.csv.csv_logger_conf import CSVLoggerConf

from scs_core.data.datetime import LocalizedDatetime

from scs_core.sys.logging import Logging
from scs_core.sys.system_id import SystemID

from scs_host.sys.host import Host


# ------------------------------------------------------------------------------------------------------------
# logging...

Logging.config('csv_log_reader_cursor_test', verbose=True)
logger = Logging.getLogger()

# ------------------------------------------------------------------------------------------------------------
# authentication...

credentials = CognitoDeviceCredentials.load_credentials_for_device(Host)

gatekeeper = CognitoLoginManager()

# --------------------------------------------------------------------------------------------------------------------

start_iso = '2020-01-20T09:50:00Z'
topic_name = 'climate'
topic_path = 'south-coast-science-dev/development/loc/1/climate'
rec_field = 'rec'

start = LocalizedDatetime.construct_from_iso8601(start_iso)
start_datetime = start.datetime

logger.info("start_datetime: %s" % start_datetime)
logger.info("-")

conf = CSVLoggerConf.load(Host)
logger.info(conf)

system_id = SystemID.load(Host)
logger.info(system_id)

finder = BylineFinder()
logger.info(finder)

queue_builder = CSVLogQueueBuilder(conf, credentials, system_id.message_tag(), topic_name, topic_path)
print(queue_builder)
logger.info("-")


reader = CSVLogReader(queue_builder)
print(reader)
logger.info("-")

reader.start()

try:
    reader.join()
except KeyboardInterrupt:
    pass
