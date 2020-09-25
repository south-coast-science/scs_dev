#!/usr/bin/env python3

"""
Created on 22 Sep 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The particulates_inference utility is used to perform data interpretation on reported OPC samples. Typically, a CSV
file is rendered as a stream of JSON documents and piped to stdin. The particulates_inference appends the
interpretation on each document and presents it to stdout.

An AWS greengrass inference server must be running in order that the utility can operate. The inference server is
accessed via a Unix domain socket. The default socket path is SCS/pipes/lambda-model-pmx-s1.uds

SYNOPSIS
particulates_inference.py -p PARTICULATES_PATH -c CLIMATE_PATH [-l LABEL_PATH] [-u UDS] [-v]

EXAMPLES
./csv_reader.py -v pm2p5-h1-validation.csv | ./particulates_inference.py -v -p praxis.pmx -c praxis.meteo -l label

FILES
 ~/SCS/pipes/lambda-model-pmx-s1.uds

DOCUMENT EXAMPLE - INPUT
{"label": 30.2926,
"praxis": {"meteo": {"val": {"hmd": 79.9, "tmp": 5.4}},
"pmx": {"val": {"per": 4.9,
"bin": [4089.0, 1736.0, 528.0, 120.0, 93.0, 26.0, 10.0, 2.0, 2.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
0.0, 0.0, 0.0, 0.0, 0.0], "mtf1": 32.0, "mtf3": 36.0, "mtf5": 42.0, "mtf7": 43.0,
"sfr": 3.0, "sht": {"hmd": 49.8, "tmp": 12.1}}}}}

DOCUMENT EXAMPLE - OUTPUT
{"src": "N3", "rec": null, "val": {"per": 4.9,
"bin": [4089.0, 1736.0, 528.0, 120.0, 93.0, 26.0, 10.0, 2.0, 2.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
0.0, 0.0, 0.0, 0.0, 0.0], "mtf1": 32.0, "mtf3": 36.0, "mtf5": 42.0, "mtf7": 43.0,
"sfr": 3.0, "sht": {"hmd": 49.8, "tmp": 12.1}},
"exg": {"s1/2020h1": {"pm1": 30.2, "pm2p5": 30.3, "pm10": 36.1}},
"label": 30.3}

SEE ALSO
scs_dev/particulates_sampler.py
"""

import json
import logging
import os
import sys

from collections import OrderedDict

from scs_core.comms.uds_client import UDSClient

from scs_core.data.datum import Datum
from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict

from scs_core.sample.sample import Sample

from scs_dev.cmd.cmd_particulates_inference import CmdParticulatesInference

from scs_host.sys.host import Host


# TODO: move to scs_analysis

# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    default_uds_path = os.path.join(Host.home_dir(), 'SCS/pipes/lambda-model-pmx-s1.uds')

    label = None
    client = None
    document_count = 0
    processed_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdParticulatesInference()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("particulates_inference: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        src_path = cmd.particulates + '.src'

        # logger...
        logger = logging.getLogger(__name__)
        logging.basicConfig(stream=sys.stderr, level=logging.INFO)

        # inference client...
        uds_path = default_uds_path if cmd.uds is None else cmd.uds

        client = UDSClient(uds_path, logger)
        print("pmx_inference_test: %s" % client, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        client.connect()

        for line in sys.stdin:
            jstr = line.strip()
            datum = PathDict.construct_from_jstr(jstr)

            document_count += 1

            if datum is None:
                break

            if not datum.has_sub_path(cmd.particulates):
                print("particulates_inference: path %s not in: %s" % (cmd.particulates, jstr), file=sys.stderr)
                exit(1)

            if not datum.has_sub_path(cmd.climate):
                print("particulates_inference: path %s not in: %s" % (cmd.climate, jstr), file=sys.stderr)
                exit(1)

            if cmd.label and not datum.has_path(cmd.label):
                print("particulates_inference: path %s not in: %s" % (cmd.label, jstr), file=sys.stderr)
                exit(1)

            if not datum.has_path(src_path):
                datum.append(src_path, 'N3')

            if cmd.label:
                label = Datum.float(datum.node(cmd.label), 1)

            particulates = Sample.construct_from_jdict(datum.node(cmd.particulates))
            climate = Sample.construct_from_jdict(datum.node(cmd.climate))

            combined = {"particulates": particulates.as_json(), "climate": climate.as_json()}

            # inference...
            client.request(JSONify.dumps(combined))
            response = client.wait_for_response()

            jdict = json.loads(response, object_hook=OrderedDict)

            # response...
            if jdict is None:
                print("particulates_inference: inference rejected: %s" % JSONify.dumps(combined), file=sys.stderr)
                sys.stderr.flush()
                break

            opc_sample = Sample.construct_from_jdict(jdict)

            jdict = opc_sample.as_json()

            if cmd.label:
                jdict[cmd.label] = label

            print(JSONify.dumps(jdict))
            sys.stdout.flush()

            processed_count += 1


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except ConnectionError as ex:
        print("particulates_inference: ConnectionError: %s" % ex, file=sys.stderr)

    except (KeyboardInterrupt, SystemExit):
        print()

    finally:
        if client:
            client.disconnect()

        print("particulates_inference: documents: %d processed: %d" % (document_count, processed_count),
              file=sys.stderr)
