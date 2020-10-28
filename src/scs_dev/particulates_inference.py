#!/usr/bin/env python3

"""
Created on 22 Sep 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The particulates_inference utility is used to perform data interpretation on reported OPC samples. Typically, a CSV
file is rendered as a stream of JSON documents and piped to stdin. The particulates_inference appends the
interpretation on the particulates node of each document and presents it to stdout.

An AWS greengrass inference server must be running in order that the utility can operate. The inference server is
accessed via a Unix domain socket. The default socket path is SCS/pipes/lambda-model-pmx-s1.uds

SYNOPSIS
particulates_inference.py -p PARTICULATES_PATH -c CLIMATE_PATH [-u UDS] [-v]

EXAMPLES
csv_reader.py -v -n ~/scs-bgx-508-ref-meteo-particulates-2020-0809-15min.csv | \
particulates_inference.py -v -c praxis.meteo -p praxis.pmx -l ref | \
csv_writer.py -v ~/scs-bgx-508-ref-meteo-particulates-2020-0809-15min-exg.csv

FILES
 ~/SCS/pipes/lambda-model-pmx-s1.uds

DOCUMENT EXAMPLE - INPUT
{"rec": "2020-08-01T00:15:00Z", "ref": {"PM10 Converted Measurement (µg/m³)": 14.13,
"PM25 Converted Measurement (µg/m³)": 7.2142, "PM1 Converted Measurement (µg/m³)": 5.54},
"praxis": {"meteo": {"val": {"hmd": 70.6, "tmp": 22.9, "bar": ""}, "tag": "scs-bgx-508"},
"pmx": {"val": {"mtf1": 28.0, "pm1": 2.4, "mtf5": 36.0, "pm2p5": 7.5,
"bin": [643.0, 48.0, 24.0, 9.0, 12.0, 12.0, 4.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
0.0, 0.0, 0.0, 0.0], "mtf3": 32.0, "pm10": 18.4, "mtf7": 33.0, "per": 4.9, "sfr": 5.35,
"sht": {"hmd": 45.9, "tmp": 30.0}}, "tag": "scs-bgx-508", "src": "N3"}}}

DOCUMENT EXAMPLE - OUTPUT
{"rec": "2020-08-01T00:15:00Z", "ref": {"PM10 Converted Measurement (µg/m³)": 14.13,
"PM25 Converted Measurement (µg/m³)": 7.2142, "PM1 Converted Measurement (µg/m³)": 5.54},
"praxis": {"meteo": {"val": {"hmd": 70.6, "tmp": 22.9, "bar": ""}, "tag": "scs-bgx-508"},
"pmx": {"val": {"mtf1": 28.0, "pm1": 2.4, "mtf5": 36.0, "pm2p5": 7.5,
"bin": [643.0, 48.0, 24.0, 9.0, 12.0, 12.0, 4.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
0.0, 0.0, 0.0, 0.0], "mtf3": 32.0, "pm10": 18.4, "mtf7": 33.0, "per": 4.9, "sfr": 5.35,
"sht": {"hmd": 45.9, "tmp": 30.0}}, "tag": "scs-bgx-508", "src": "N3",
"exg": {"s1/2020h1": {"pm1": 5.4, "pm2p5": 8.0, "pm10": 13.5}}}}}

SEE ALSO
scs_dev/particulates_sampler.py
"""

import json
import logging
import os
import sys

from scs_core.comms.uds_client import UDSClient

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict

from scs_core.sample.sample import Sample

from scs_dev.cmd.cmd_particulates_inference import CmdParticulatesInference

from scs_host.sys.host import Host


# TODO: move to scs_analysis

# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    default_uds_path = os.path.join(Host.scs_path(), 'pipes/lambda-model-pmx-s1.uds')

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

        # paths...
        src_path = cmd.particulates + '.src'
        exg_path = cmd.particulates + '.exg'

        # logger...
        logger = logging.getLogger(__name__)
        logging.basicConfig(stream=sys.stderr, level=logging.INFO)

        # output...
        # inference client...
        uds_path = default_uds_path if cmd.uds is None else cmd.uds

        if not os.path.exists(uds_path):
            print("particulates_inference: WARNING: %s required, but not present" % uds_path, file=sys.stderr)

        client = UDSClient(uds_path, logger)

        if cmd.verbose:
            print("particulates_inference: %s" % client, file=sys.stderr)

        sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        client.connect()

        for line in sys.stdin:
            jstr = line.strip()
            datum = PathDict.construct_from_jstr(jstr)

            document_count += 1

            if datum is None:
                break

            # fields...
            if not datum.has_sub_path(cmd.particulates):
                print("particulates_inference: path %s not in: %s" % (cmd.particulates, jstr), file=sys.stderr)
                exit(1)

            if not datum.has_sub_path(cmd.climate):
                print("particulates_inference: path %s not in: %s" % (cmd.climate, jstr), file=sys.stderr)
                exit(1)

            if not datum.has_path(src_path):
                datum.append(src_path, 'N3')

            particulates = Sample.construct_from_jdict(datum.node(cmd.particulates))
            climate = Sample.construct_from_jdict(datum.node(cmd.climate))

            combined = {"particulates": particulates.as_json(), "climate": climate.as_json()}

            # inference...
            client.request(JSONify.dumps(combined))
            response = client.wait_for_response()

            jdict = json.loads(response)

            # response...
            if jdict is None:
                print("particulates_inference: inference rejected: %s" % jstr, file=sys.stderr)
                sys.stderr.flush()
                break

            datum.append(exg_path, jdict['exg'])

            print(JSONify.dumps(datum))
            sys.stdout.flush()

            processed_count += 1


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except ConnectionError as ex:
        print("particulates_inference: ConnectionError: %s" % ex, file=sys.stderr)

    except (KeyboardInterrupt, SystemExit):
        print(file=sys.stderr)

    finally:
        if client:
            client.disconnect()

        print("particulates_inference: documents: %d processed: %d" % (document_count, processed_count),
              file=sys.stderr)
