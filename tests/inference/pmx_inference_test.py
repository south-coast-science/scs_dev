#!/usr/bin/env python3

"""
Created on 12 Sep 2020

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
import time

from collections import OrderedDict

from scs_core.comms.uds_client import UDSClient

from scs_core.data.datum import Datum
from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict

from scs_core.particulate.opc_datum import OPCDatum

from scs_core.sample.sample import Sample

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------
# references...

uds_path = 'SCS/pipes/lambda-model-pmx-s1.uds'

document_count = 0
processed_count = 0
start_time = None


# --------------------------------------------------------------------------------------------------------------------
# resources...

# logger...
logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

# inference client...
client = UDSClient(os.path.join(Host.home_dir(), uds_path), logger)
print("pmx_inference_test: %s" % client, file=sys.stderr)


# --------------------------------------------------------------------------------------------------------------------
# run...

try:
    client.connect()

    start_time = time.time()

    for line in sys.stdin:
        # request...
        datum = PathDict.construct_from_jstr(line)

        document_count += 1

        if datum is None:
            break

        datum.append('praxis.pmx.src', 'N3')

        particulates = Sample.construct_from_jdict(datum.node('praxis.pmx'))
        climate = Sample.construct_from_jdict(datum.node('praxis.meteo'))
        label = Datum.float(datum.node('label'), 1)

        combined = {"particulates": particulates.as_json(), "climate": climate.as_json()}

        # inference...
        client.request(JSONify.dumps(combined))
        response = client.wait_for_response()

        jdict = json.loads(response, object_hook=OrderedDict)

        # response...
        if jdict is None:
            print("pmx_inference_test: inference rejected: %s" % JSONify.dumps(combined), file=sys.stderr)
            sys.stdout.flush()
            break

        opc_sample = Sample.construct_from_jdict(jdict)

        jdict = opc_sample.as_json()
        jdict['label'] = label

        print(JSONify.dumps(jdict))
        sys.stdout.flush()

        processed_count += 1


# ---------------------------------------------------------------------------------------------------------------------
# end...

except KeyboardInterrupt:
    print()

finally:
    client.disconnect()

    print("pmx_inference_test: documents: %d processed: %d" % (document_count, processed_count),
          file=sys.stderr)

    if start_time and processed_count > 0:
        elapsed_time = round(time.time() - start_time, 1)
        avg_per_inference = round(elapsed_time / processed_count, 3)

        print("pmx_inference_test: elapsed time: %s avg_per_inference: %s" % (elapsed_time, avg_per_inference),
              file=sys.stderr)
