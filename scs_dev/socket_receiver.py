#!/usr/bin/env python3

"""
Created on 18 Aug 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./socket_receiver.py -v
"""

import socket
import sys
import time

from scs_core.data.json import JSONify
from scs_core.sys.exception_report import ExceptionReport

from scs_dev.cmd.cmd_socket_receiver import CmdSocketReceiver


# TODO: re-write as ProcessComms implementation

# --------------------------------------------------------------------------------------------------------------------

class SocketReceiver(object):
    """
    classdocs
    """

    __BUFFER_SIZE =     1024        # bytes
    __BACKLOG =         5

    __ACK =             "ACK"


    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, port, verbose=False):
        """
        Constructor
        """
        # fields...
        self.__port = port
        self.__verbose = verbose

        # socket...
        self.__address = ('', port)        # a receiving socket should not be given an IP address!

        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.bind(self.__address)
        self.__socket.listen(SocketReceiver.__BACKLOG)

        self._conn = None


    # ----------------------------------------------------------------------------------------------------------------

    def accept(self):
        self._conn, self.__address = self.__socket.accept()


    def messages(self):
        while True:
            message = self.__receive()

            if len(message) == 0:
                break

            yield message


    def ack(self):
        self._conn.send(str(SocketReceiver.__ACK).encode())


    def close(self):
        try:
            self.ack()
        except RuntimeError:
            pass

        time.sleep(0.1)     # allows the client to close first?

        try:
            self._conn.close()

            if self.__verbose:
                print("SocketReceiver: connection closed.")
        except RuntimeError:
            pass

        self.__socket.close()

        if self.__verbose:
            print("SocketReceiver: socket closed.")


    # ----------------------------------------------------------------------------------------------------------------

    def __receive(self):
        received = self._conn.recv(SocketReceiver.__BUFFER_SIZE).decode()

        return received.strip()


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def address(self):
        return self.__address


    @property
    def verbose(self):
        return self.__verbose


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "SocketReceiver:{address:%s, verbose:%s}" % (str(self.address), self.verbose)


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSocketReceiver()

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    receiver = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        receiver = SocketReceiver(cmd.port, cmd.verbose)

        if cmd.verbose:
            print(receiver, file=sys.stderr)
            sys.stderr.flush()

        # ------------------------------------------------------------------------------------------------------------
        # run...

        receiver.accept()

        for datum in receiver.messages():
            print(datum)
            sys.stdout.flush()

            receiver.ack()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("socket_receiver: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)


    # ----------------------------------------------------------------------------------------------------------------
    # close...

    finally:
        try:
            if receiver is not None:
                receiver.close()
        except:
            raise
