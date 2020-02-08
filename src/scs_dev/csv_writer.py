#!/usr/bin/env python3

"""
Created on 19 Aug 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The csv_writer utility is used to convert from JSON format to comma-separated value (CSV) format.

The path into the JSON document is used to name the column in the header row: dictionary fields are separated
from their container by a period ('.') character, and array members are separated by a colon (':') character.

All the leaf nodes of the first JSON document are included in the CSV. If subsequent JSON documents in the input stream
contain fields that were not in this first document, these extra fields are ignored. If subsequent JSON documents
do not contain a field in the header, then this field is given the null value.

SYNOPSIS
csv_writer.py [-c] [-a] [-e] [-v] [FILENAME]

EXAMPLES
./socket_receiver.py | ./csv_writer.py temp.csv -e

DOCUMENT EXAMPLE - INPUT
{"tag": "scs-ap1-6", "rec": "2018-04-04T14:50:27.641+00:00", "val": {"hmd": 59.6, "tmp": 23.8}}

DOCUMENT EXAMPLE - OUTPUT
tag,rec,val.hmd,val.tmp
scs-ap1-6,2018-04-04T14:50:38.394+00:00,59.7,23.8

SEE ALSO
scs_dev/csv_logger
scs_dev/csv_reader
"""

import sys

from scs_core.csv.csv_writer import CSVWriter

from scs_core.sys.signalled_exit import SignalledExit

from scs_dev.cmd.cmd_csv_writer import CmdCSVWriter


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    writer = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdCSVWriter()

    if cmd.verbose:
        print("csv_writer: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        writer = CSVWriter(cmd.filename, cmd.append)

        if cmd.verbose:
            print("csv_writer: %s" % writer, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # signal handler...
        SignalledExit.construct("csv_writer", cmd.verbose)

        for line in sys.stdin:
            jstr = line.strip()

            if jstr is None:
                break

            writer.write(jstr)

            # echo...
            if cmd.echo:
                print(jstr)
                sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except ConnectionError as ex:
        print("csv_writer: %s" % ex, file=sys.stderr)

    except (KeyboardInterrupt, SystemExit):
        pass

    finally:
        if cmd and cmd.verbose:
            print("csv_writer: finishing", file=sys.stderr)

        if writer:
            writer.close()
