#!/usr/bin/env python3

"""
Created on 13 Sep 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

example CSV:
label,
praxis.meteo.val.hmd, praxis.meteo.val.tmp, praxis.pmx.val.per, praxis.pmx.val.bin:0, praxis.pmx.val.bin:1,
praxis.pmx.val.bin:2, praxis.pmx.val.bin:3, praxis.pmx.val.bin:4, praxis.pmx.val.bin:5, praxis.pmx.val.bin:6,
praxis.pmx.val.bin:7, praxis.pmx.val.bin:8, praxis.pmx.val.bin:9, praxis.pmx.val.bin:10, praxis.pmx.val.bin:11,
praxis.pmx.val.bin:12, praxis.pmx.val.bin:13, praxis.pmx.val.bin:14, praxis.pmx.val.bin:15, praxis.pmx.val.bin:16,
praxis.pmx.val.bin:17, praxis.pmx.val.bin:18, praxis.pmx.val.bin:19, praxis.pmx.val.bin:20, praxis.pmx.val.bin:21,
praxis.pmx.val.bin:22, praxis.pmx.val.bin:23,
praxis.pmx.val.mtf1, praxis.pmx.val.mtf3, praxis.pmx.val.mtf5, praxis.pmx.val.mtf7,
praxis.pmx.val.sfr, praxis.pmx.val.sht.hmd, praxis.pmx.val.sht.tmp
"""

import json
import logging
import os
import sys

from collections import OrderedDict

from scs_core.comms.uds_client import UDSClient

from scs_core.data.json import JSONify

from scs_core.climate.sht_datum import SHTDatum
from scs_core.model.particulates.s1.pmx_request import PMxRequest
from scs_core.particulate.opc_datum import OPCDatum

from scs_core.sample.sample import Sample
from scs_core.sample.climate_sample import ClimateSample

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------
# references...

int_sht = SHTDatum(25.0, 29.0)
ext_sht = SHTDatum(35.0, 21.0)

opc = OPCDatum('N3', None, 0.0, 0.0, 0.0, 4.9,
               [9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
               0.0, 0.0, 0.0, 0.0, sfr=4.9, sht=int_sht)

uds_path = 'pipes/lambda-model-pmx-s1.uds'

document_count = 0
processed_count = 0
start_time = None


# --------------------------------------------------------------------------------------------------------------------
# resources...

# logger...
logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

# inference client...
client = UDSClient(os.path.join(Host.scs_path(), uds_path), logger)
print("pmx_inference_test: %s" % client, file=sys.stderr)


# --------------------------------------------------------------------------------------------------------------------
# run...

try:
    client.connect()

    sample = opc.as_sample('tag')
    climate = ClimateSample('tag', None, ext_sht, None)
    label = 1.0

    combined = PMxRequest(sample, climate)

    # inference...
    client.request(JSONify.dumps(combined.as_json()))
    response = client.wait_for_response()

    jdict = json.loads(response, object_hook=OrderedDict)

    # response...
    if jdict is None:
        print("pmx_zero_test: inference rejected: %s" % JSONify.dumps(combined), file=sys.stderr)
        sys.stdout.flush()
        exit(1)

    opc_sample = Sample.construct_from_jdict(jdict)

    jdict = opc_sample.as_json()
    jdict['label'] = label

    print(JSONify.dumps(jdict))
    sys.stdout.flush()


# ---------------------------------------------------------------------------------------------------------------------
# end...

except KeyboardInterrupt:
    print()

finally:
    client.disconnect()
