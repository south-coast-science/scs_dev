#!/usr/bin/env python3

'''
Created on 2 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./bluetooth_monitor.py > /dev/null &
'''

import sys

from scs_core.data.json import JSONify
from scs_core.monitor.monitor_error import MonitorError
from scs_core.monitor.monitor_response import MonitorResponse
from scs_core.sys.exception_report import ExceptionReport

from scs_dfe.network.bluetooth_connection import BluetoothConnection
from scs_dfe.network.bluetooth_serial import BluetoothSerial
from scs_dfe.network.interface import Interface
from scs_dfe.network.wifi_station import WiFiStation
from scs_dfe.network.wpa_supplicant_file import WPASupplicantFile

from scs_host.sys.hostname import Hostname


# --------------------------------------------------------------------------------------------------------------------

class BluetoothHandler(object):
    '''
    classdocs
    '''

    # ----------------------------------------------------------------------------------------------------------------

    def respond(self, request):
        message = None
        error = None

        # TODO: handle (password-protected) session

        try:
            if request == "":
                return None

            elif request == "wifi-hostname":
                message = Hostname.find()

            elif request == "wifi-ifconfig":
                message = Interface.find(Interface.WIFI)

            elif request == "wifi-stations":
                message = WiFiStation.find_all()

            elif request == "wifi-supplicants":
                message = WPASupplicantFile.read().supplicants

            else:
                error = MonitorError(MonitorError.CODE_UNKNOWN_CMD, request)

        except Exception as ex:
            error = type(ex).__name__ + ":" + str(ex)

        response = MonitorResponse(message, error)
        jstr = JSONify.dumps(response)

        print('\r\n' + jstr, end='')

        return jstr


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resource...

        handler = BluetoothHandler()

        BluetoothConnection.enable()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for state in BluetoothConnection.monitor():
            print("state:[%s]" % state, end='\r\n')

            if state == BluetoothConnection.FAILED:
                raise RuntimeError("bluetooth_monitor: connection failed")

            if state == BluetoothConnection.STOPPED:
                break

            if state == BluetoothConnection.CONNECTED:
                BluetoothSerial.monitor(handler)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt as ex:
        print("bluetooth_monitor: " + type(ex).__name__, file=sys.stderr)
        # TODO: BluetoothSerial.stop()
        pass

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)
        # TODO: reboot system!

    finally:
        # BluetoothSerial.stop()          # !?
        print("exiting", end='\r\n')
