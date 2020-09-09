#!/usr/bin/env python3

"""
Created on 11 Apr 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The node utility is used to extract a node or nodes from within a JSON document. Data is presented as a sequence of
documents on stdin, and the extracted node(s) are passed to stdout. The extracted node may be a leaf node or an internal
node.

By default, only the specified nodes are passed to the output. In the --exclude mode, all nodes are passed to stdout,
with the exception of the specified nodes. In the default mode, if no node path is specified, the whole input document
is passed to stdout. In the --exclude mode, if no node path is specified, then nothing is output.

By default, output is in the form of a sequence of JSON documents, separated by newlines. If the array (-a) option is
selected, output is in the form of a JSON array - the output opens with a '[' character, documents are separated by
the ',' character, and the output is terminated by a ']' character.

Alternatively, if the node is an array or other iterable type, then it may be output as a sequence (a list of items
separated by newline characters) according to the -s flag.

SYNOPSIS
node.py { [-x] [-a] | -s } [-v] [SUB_PATH_1 ... SUB_PATH_N]

EXAMPLES
csv_reader.py climate.csv | node.py -x val.bar

DOCUMENT EXAMPLE - INPUT
{"val": {"hmd": 73.5, "tmp": 10.8, "bar": ""}, "rec": "2019-02-17T08:56:53Z"}
{"val": {"hmd": 73.6, "tmp": 10.8, "bar": ""}, "rec": "2019-02-17T08:57:53Z"}

DOCUMENT EXAMPLE - OUTPUT
default mode:
{"val": {"hmd": 73.5, "tmp": 10.8}, "rec": "2019-02-17T08:56:53Z"}
{"val": {"hmd": 73.6, "tmp": 10.8}, "rec": "2019-02-17T08:57:53Z"}

array mode:
[{"val": {"hmd": 73.5, "tmp": 10.8}, "rec": "2019-02-17T08:56:53Z"},
{"val": {"hmd": 73.6, "tmp": 10.8}, "rec": "2019-02-17T08:57:53Z"}]
"""

import sys

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict

from scs_dev.cmd.cmd_node import CmdNode


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    document_count = 0
    output_count = 0

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdNode()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("node: %s" % cmd, file=sys.stderr)
        sys.stderr.flush()

    try:
        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.array:
            print('[', end='')

        node = None
        first = True

        for line in sys.stdin:
            jstr = line.strip()
            datum = PathDict.construct_from_jstr(jstr)

            if datum is None:
                continue

            document_count += 1

            if cmd.exclude and not cmd.sub_paths:
                continue                                # everything is excluded

            # build...
            if not cmd.sub_paths:
                target = datum                          # everything is included

            else:
                target = PathDict()

                if cmd.exclude:
                    # use datum field ordering...
                    for path in datum.paths():
                        if cmd.includes(path):
                            target.append(path, datum.node(path))

                else:
                    # use cmd.sub_paths field ordering...
                    for sub_path in cmd.sub_paths:
                        if datum.has_sub_path(sub_path):
                            target.append(sub_path, datum.node(sub_path))

            # report...
            if not target:
                continue                                # skip empty outputs

            if cmd.sequence:
                for path in cmd.sub_paths:
                    node = target.node(path)

                    try:
                        for item in node:
                            print(JSONify.dumps(item))
                    except TypeError as ex:
                        print(ex)
                        print(JSONify.dumps(node))

            else:
                if cmd.array:
                    if first:
                        print(JSONify.dumps(target), end='')
                        first = False

                    else:
                        print(", %s" % JSONify.dumps(target), end='')

                else:
                    print(JSONify.dumps(target))

            sys.stdout.flush()

            output_count += 1


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyError as ex:
        print("node: KeyError: %s" % ex, file=sys.stderr)

    except KeyboardInterrupt:
        if cmd.verbose:
            print("node: KeyboardInterrupt", file=sys.stderr)

    finally:
        if cmd.array:
            print(']')

        if cmd.verbose:
            print("node: documents: %d output: %d" % (document_count, output_count), file=sys.stderr)
