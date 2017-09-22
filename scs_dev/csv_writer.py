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


# TODO: catch / trace the following error:


# {"cls": "NameError", "args": ["name 'calib' is not defined"], "trace": [
# {"loc": "File \"./gases_sampler.py\", line 98, in <module>", "stat": "for sample in sampler.samples():"},
# {"loc": "File \"/home/pi/SCS/scs_core/scs_core/sampler/sampler.py\", line 35, in samples", "stat": "for sample in self.__runner.samples(self):"},
# {"loc": "File \"/home/pi/SCS/scs_core/scs_core/sync/timed_runner.py\", line 37, in samples", "stat": "yield sampler.sample()"},
# {"loc": "File \"/home/pi/SCS/scs_dev/scs_dev/sampler/gases_sampler.py\", line 57, in sample", "stat": "afe_datum = self.__afe.sample(sht_datum)"},
# {"loc": "File \"/home/pi/SCS/scs_dfe_eng/scs_dfe/gas/afe.py\", line 79, in sample", "stat": "sample = sensor.sample(self, temp, sensor_index, no2_sample)"},
# {"loc": "File \"/home/pi/SCS/scs_core/scs_core/gas/pid.py\", line 50, in sample", "stat": "return PIDDatum.construct(calib, self.baseline, self.__tc, temp, we_v)

# {"cls": "ValueError", "args": ["Expecting value: line 1 column 1 (char 0)"], "trace": [
# {"loc": "File \"./csv_writer.py\", line 55, in <module>", "stat": "csv.write(datum)"},
# {"loc": "File \"/home/pi/SCS/scs_core/scs_core/csv/csv_writer.py\", line 56, in write", "stat": "jdict = json.loads(jstr, object_pairs_hook=OrderedDict)"},
# {"loc": "File \"/usr/lib/python3.4/json/__init__.py\", line 331, in loads", "stat": "return cls(**kw).decode(s)"},
# {"loc": "File \"/usr/lib/python3.4/json/decoder.py\", line 343, in decode", "stat": "obj, end = self.raw_decode(s, idx=_w(s, 0).end())"},
# {"loc": "File \"/usr/lib/python3.4/json/decoder.py\", line 361, in raw_decode", "stat": "raise ValueError(errmsg(\"Expecting value\", s, err.value)) from None"}],
# "sum": "ValueError: Expecting value: line 1 column 1 (char 0)"}


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
        # resources...

        csv = CSVWriter(cmd.filename, cmd.cache, cmd.append)

        if cmd.verbose:
            print(csv, file=sys.stderr)
            sys.stderr.flush()

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

    except KeyboardInterrupt:
        if cmd.verbose:
            print("csv_writer: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)


    # ----------------------------------------------------------------------------------------------------------------
    # close...

    finally:
        if csv is not None:
            csv.close()
