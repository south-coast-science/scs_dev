#!/usr/bin/env python3

"""
Created on 14 Aug 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import os
import time

from scs_core.comms.uds_client import UDSClient
from scs_core.data.datetime import LocalizedDatetime
from scs_core.sys.logging import Logging

from scs_host.comms.domain_socket import DomainSocket


# --------------------------------------------------------------------------------------------------------------------
# resources...

# logging...
logger = Logging.config(__name__, verbose=True)

# client...
location = os.getcwd()
path = os.path.join(location, 'lambda-model.uds')

client = UDSClient(DomainSocket, path)


# --------------------------------------------------------------------------------------------------------------------
# run...

try:
    client.open()
    print(client)

    while True:
        client.request('%s: hello' % LocalizedDatetime.now().as_iso8601())
        print('requested')

        message = client.wait_for_response()
        print(message)

        time.sleep(4)

except KeyboardInterrupt:
    print()

finally:
    client.close()
