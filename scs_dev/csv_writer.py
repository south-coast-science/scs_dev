#!/usr/bin/env python3

"""
Created on 19 Aug 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./temp_sampler.py | ./csv_writer.py temp.csv -e
"""

import sys

from scs_core.csv.csv_writer import CSVWriter
from scs_core.data.json import JSONify
from scs_core.sys.exception_report import ExceptionReport

from scs_dev.cmd.cmd_csv_writer import CmdCSVWriter


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    cmd = None
    csv = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdCSVWriter()

        if cmd.verbose:
            print(cmd, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # resource...

        csv = CSVWriter(cmd.filename)

        if cmd.verbose:
            print(csv, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            datum = line.strip()

            if datum is None:
                break

            csv.write(datum)

            # echo...
            if cmd.echo:
                print(datum)
                sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt as ex:
        if cmd.verbose:
            print("csv_writer: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)


    # ----------------------------------------------------------------------------------------------------------------
    # close...

    finally:
        if csv is not None:
            csv.close()
