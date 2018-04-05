#!/usr/bin/env python3

"""
Created on 11 Apr 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The node utility is used to extract a node from within a JSON document. Data is presented as a sequence of documents on
stdin, and the extracted node is passed to stdout. The extracted node may be a leaf node or an internal node. If no
node path is specified, the whole input document is passed to stdout.

The node utility may be set to either ignore documents that do not contain the specified node, or to terminate if the
node is not present.

SYNOPSIS
node.py [-i] [-v] [PATH]

EXAMPLES
./gases_sampler.py -i10 | ./node.py val.CO
"""

import sys

from scs_core.data.json import JSONify
from scs_core.data.path_dict import PathDict

from scs_dev.cmd.cmd_node import CmdNode


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdNode()

    if cmd.verbose:
        print(cmd, file=sys.stderr)
        sys.stderr.flush()


    try:
        # ------------------------------------------------------------------------------------------------------------
        # run...

        for line in sys.stdin:
            datum = PathDict.construct_from_jstr(line)

            if cmd.ignore and not datum.has_path(cmd.path):
                continue

            node = datum.node(cmd.path)

            print(JSONify.dumps(node))
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("node: KeyboardInterrupt", file=sys.stderr)
