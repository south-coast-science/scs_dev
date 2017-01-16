'''
Created on 20 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
'''

import time

from scs_dfe.particulate.opc_n2 import OPCN2
from scs_core.common.localized_datetime import LocalizedDatetime
from scs_core.sample.particulates_datum import ParticulatesDatum
from scs_core.sync.sampler import Sampler


# --------------------------------------------------------------------------------------------------------------------

class ParticulatesSampler(Sampler):
    '''
    classdocs
    '''

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, interval, sample_count = 0):
        '''
        Constructor
        '''
        Sampler.__init__(self, interval, sample_count)

        self.__opc = OPCN2()


    # ----------------------------------------------------------------------------------------------------------------

    def on(self):
        self.__opc.on()
        time.sleep(5)


    def off(self):
        self.__opc.off()


    def reset(self):
        self.__opc.sample()


    def sample(self):
        recorded = LocalizedDatetime.now()

        opc_sample = self.__opc.sample()

        return ParticulatesDatum(recorded, opc_sample)


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "ParticulatesSampler:{opc:%s, timer:%s, sample_count:%d}" % \
                    (self.__opc, self.timer, self.sample_count)
