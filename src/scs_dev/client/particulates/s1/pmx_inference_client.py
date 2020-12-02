"""
Created on 2 Dec 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

example request:
{"particulates":
    {"tag": "scs-be2-3", "src": "N3", "rec": "2020-08-16T07:52:24Z",
    "val": {"per": 4.9, "pm1": 17.8, "pm2p5": 19.4, "pm10": 19.5,
    "bin": [703, 32, 3, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    "mtf1": 79, "mtf3": 80, "mtf5": 0, "mtf7": 0, "sfr": 0.52,
    "sht": {"hmd": 45.8, "tmp": 30.1}},
    "exg": {"ISLin/N3/vPLHR": {"pm1": 41.0, "pm2p5": 21.0, "pm10": 15.3}}},
"climate":
    {"hmd": 60.5, "tmp": 25.9}}
"""

import json
import logging
import sys

from scs_core.comms.uds_client import UDSClient

from scs_core.data.json import JSONify

from scs_core.model.particulates.s1.pmx_request import PMxRequest


# --------------------------------------------------------------------------------------------------------------------

class PMxInferenceClient(object):
    """
    classdocs
    """

    @classmethod
    def construct(cls, inference_uds_path):
        # logger...
        logger = logging.getLogger(__name__)
        logging.basicConfig(stream=sys.stderr, level=logging.INFO)

        # UDS...
        uds_client = UDSClient(inference_uds_path, logger)

        return cls(uds_client)


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, uds_client):
        """
        Constructor
        """
        self.__uds_client = uds_client                      # UDSClient


    # ----------------------------------------------------------------------------------------------------------------

    def connect(self):
        self.__uds_client.connect()


    def disconnect(self):
        self.__uds_client.disconnect()


    def infer(self, opc_sample, ext_sht_sample):
        pmx_request = PMxRequest(opc_sample, ext_sht_sample)
        self.__uds_client.request(JSONify.dumps(pmx_request.as_json()))
        response = self.__uds_client.wait_for_response()

        return json.loads(response)


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "PMxInferenceClient(s1):{uds_client:%s}" %  self.__uds_client
