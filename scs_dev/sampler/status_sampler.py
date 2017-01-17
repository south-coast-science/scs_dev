"""
Created on 20 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

from scs_core.data.localized_datetime import LocalizedDatetime
from scs_core.location.gpgga import GPGGA
from scs_core.location.gps_location import GPSLocation
from scs_core.sample.status_datum import StatusDatum
from scs_core.sync.sampler import Sampler
from scs_core.sys.system_temp import SystemTemp

from scs_dfe.board.mcp9808 import MCP9808
from scs_dfe.gps.pam7q import PAM7Q

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

class StatusSampler(Sampler):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, interval, sample_count=0):
        """
        Constructor
        """
        Sampler.__init__(self, interval, sample_count)

        self.__board = MCP9808(True)
        self.__gps = PAM7Q()


    # ----------------------------------------------------------------------------------------------------------------

    def reset(self):
        pass


    def sample(self):
        recorded = LocalizedDatetime.now()

        # location...
        try:
            self.__gps.open()
            gga = self.__gps.report(GPGGA)
            location = GPSLocation.construct(gga)
        except RuntimeError:
            location = None

        finally:
            self.__gps.close()

        # temperature...
        board_sample = self.__board.sample()
        mcu_sample = Host.mcu_temp()

        temperature = SystemTemp.construct(board_sample, mcu_sample)

        # exception...
        exception = None    # TODO: handle exception sending

        return StatusDatum(recorded, location, temperature, exception)


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "StatusSampler:{board:%s, timer:%s, sample_count:%d}" % \
                    (self.__board, self.timer, self.sample_count)
