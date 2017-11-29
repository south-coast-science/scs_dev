#!/usr/bin/env python3

"""
Created on 4 Aug 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The csv_reader utility is used to convert data from comma-separated value (CSV) format to JSON format.

The names of columns given in the header row indicate paths into the JSON document, with nodes separated by a period
('.') character. The period character cannot be used within the name of a node.

The first row of the CSV file (or stdin input) is assumed to be a header row. If there are more columns in the body of
the CSV than in the header, excess values are ignored.

EXAMPLES
./csv_reader.py temp.csv

SEE ALSO
scs_dev/csv_writer
"""

import sys

from scs_core.csv.csv_reader import CSVReader
from scs_core.data.json import JSONify
from scs_core.sys.exception_report import ExceptionReport
from scs_dev.cmd.cmd_csv_reader import CmdCSVReader


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    cmd = None
    csv = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdCSVReader()

        if cmd.verbose:
            print(cmd, file=sys.stderr)

        # ------------------------------------------------------------------------------------------------------------
        # resources...

        csv = CSVReader(cmd.filename)

        if cmd.verbose:
            print(csv, file=sys.stderr)
            sys.stderr.flush()

        # ------------------------------------------------------------------------------------------------------------
        # run...

        for datum in csv.rows:
            print(datum)
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("csv_reader: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)


    # ----------------------------------------------------------------------------------------------------------------
    # close...

    finally:
        if csv is not None:
            csv.close()
