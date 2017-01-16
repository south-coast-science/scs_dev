'''
Created on 20 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
'''

from scs_dfe.gas.afe import AFE

from scs_core.common.localized_datetime import LocalizedDatetime

from scs_core.sample.gases_datum import GasesDatum

from scs_core.sync.sampler import Sampler


# --------------------------------------------------------------------------------------------------------------------

class GasesSampler(Sampler):
    '''
    classdocs
    '''

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, sht, pt1000, sensors, interval, sample_count = 0):
        '''
        Constructor
        '''
        Sampler.__init__(self, interval, sample_count)

        self.__afe = AFE(pt1000, sensors)
        self.__sht = sht


    # ----------------------------------------------------------------------------------------------------------------

    def reset(self):
        self.__sht.reset()


    def sample(self):
        recorded = LocalizedDatetime.now()

        afe_sample = self.__afe.sample()
        sht_sample = self.__sht.sample()

        return GasesDatum(recorded, afe_sample, sht_sample)


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "GasesSampler:{afe:%s, sht:%s, timer:%s, sample_count:%d}" % \
                    (self.__afe, self.__sht, self.timer, self.sample_count)
