#!/usr/bin/env python3

"""
Created on 4 Aug 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The csv_reader utility is used to convert data from comma-separated value (CSV) format to JSON format.

The names of columns given in the CSV header row indicate paths into the JSON document: dictionary fields are separated
from their container by a period ('.') character, and JSON array members separated from their container by a
colon (':') character.

The first row of the CSV file (or stdin input) is assumed to be a header row. If there are more columns in the body of
the CSV than in the header, excess values are ignored. Header cells may not be empty.

By default, output is in the form of a sequence of JSON documents, separated by newlines. If the array (-a) option is
selected, output is in the form of a JSON array - the output opens with a '[' character, documents are separated by
the ',' character, and the output is terminated by a ']' character.

SYNOPSIS
csv_reader.py [-s] [-n] [-l LIMIT] [-a] [-v] [FILENAME_1 .. FILENAME_N]

EXAMPLES
csv_reader.py -v scs-ph1-10-status-2019-07-*.csv

DOCUMENT EXAMPLE - INPUT
tag,rec,val.hmd,val.tmp
scs-ap1-6,2018-04-04T14:50:38.394+00:00,59.7,23.8
scs-ap1-6,2018-04-04T14:55:38.394+00:00,59.8,23.9

DOCUMENT EXAMPLE - OUTPUT
Sequence mode:
{"tag": "scs-ap1-6", "rec": "2018-04-04T14:50:38.394+00:00", "val": {"hmd": 59.7, "tmp": 23.8}}
{"tag": "scs-ap1-6", "rec": "2018-04-04T14:55:38.394+00:00", "val": {"hmd": 59.8, "tmp": 23.9}}

Array mode:
[{"tag": "scs-ap1-6", "rec": "2018-04-04T14:50:38.394+00:00", "val": {"hmd": 59.7, "tmp": 23.8}},
{"tag": "scs-ap1-6", "rec": "2018-04-04T14:55:38.394+00:00", "val": {"hmd": 59.8, "tmp": 23.9}}]

SEE ALSO
scs_dev/csv_writer
"""

import sys

from scs_core.csv.csv_reader import CSVReader, CSVReaderException
from scs_core.csv.csv_dict import CSVHeaderError

from scs_dev.cmd.cmd_csv_reader import CmdCSVReader


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    file_count = 0
    total_rows = 0

    reader = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdCSVReader()

    if cmd.verbose:
        print("csv_reader: %s" % cmd, file=sys.stderr)

    if cmd.array:
        print('[', end='')

    try:
        for filename in cmd.filenames:

            file_count += 1
            rows = 0

            # --------------------------------------------------------------------------------------------------------
            # resources...

            try:
                reader = CSVReader.construct_for_file(filename, cast=cmd.cast, nullify=cmd.nullify)

            except FileNotFoundError:
                print("csv_reader: file not found: %s" % filename, file=sys.stderr)
                exit(1)

            except KeyError as ex:
                print("csv_reader: empty header cell in: %s." % ex, file=sys.stderr)
                exit(1)

            except ValueError as ex:
                print("csv_reader: duplicate column names in: %s." % ex, file=sys.stderr)
                exit(1)

            if cmd.verbose:
                print("csv_reader: %s" % reader, file=sys.stderr)
                sys.stderr.flush()


            # --------------------------------------------------------------------------------------------------------
            # run...

            try:
                for datum in reader.rows():
                    if cmd.limit is not None and rows >= cmd.limit:
                        break

                    if cmd.array:
                        if rows == 0:
                            print(datum, end='')

                        else:
                            print(", %s" % datum, end='')

                    else:
                        print(datum)

                    sys.stdout.flush()

                    rows += 1

            except CSVHeaderError as ex:
                print("csv_reader: clashing column names: '%s' and '%s'" % (ex.left, ex.right), file=sys.stderr)
                exit(1)

            except CSVReaderException as ex:
                if cmd.verbose:
                    print("csv_reader: ending file on row %d: %s" % (rows, ex), file=sys.stderr)
                    continue

            finally:
                if reader is not None:
                    reader.close()

            if cmd.verbose:
                print("csv_reader: rows: %d" % rows, file=sys.stderr)

            total_rows += rows


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd and cmd.verbose:
            print("csv_reader: KeyboardInterrupt", file=sys.stderr)

    finally:
        if cmd.array:
            print(']')

        if cmd and cmd.verbose and file_count > 1:
            print("csv_reader: files: %d total rows: %d" % (file_count, total_rows), file=sys.stderr)
