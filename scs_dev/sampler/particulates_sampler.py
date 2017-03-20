"""
Created on 20 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import time

from scs_core.data.localized_datetime import LocalizedDatetime
from scs_core.sample.particulates_datum import ParticulatesDatum
from scs_core.sync.sampler import Sampler

from scs_dfe.particulate.opc_n2 import OPCN2


# --------------------------------------------------------------------------------------------------------------------

class ParticulatesSampler(Sampler):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, device_id, interval, sample_count=0):
        """
        Constructor
        """
        Sampler.__init__(self, interval, sample_count)

        self.__device_id = device_id
        self.__opc = OPCN2()


    # ----------------------------------------------------------------------------------------------------------------

    def on(self):
        self.__opc.power_on()
        self.__opc.operations_on()
        time.sleep(5)


    def off(self):
        self.__opc.operations_off()
        self.__opc.power_off()


    def reset(self):
        self.__opc.sample()


    def sample(self):
        tag = self.__device_id.message_tag()

        opc_sample = self.__opc.sample()

        recorded = LocalizedDatetime.now()      # after sampling, so that we can monitor resource contention

        return ParticulatesDatum(tag, recorded, opc_sample)


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "ParticulatesSampler:{device_id:%s, opc:%s, timer:%s, sample_count:%d}" % \
                    (self.__device_id, self.__opc, self.timer, self.sample_count)
