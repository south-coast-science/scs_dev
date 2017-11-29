#!/usr/bin/env python3

"""
Created on 18 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The aws_api_auth utility is used to store or read the API key required by the South Coast Science / AWS historic data
retrieval system.

EXAMPLES
./aws_api_auth.py -v -s de92c5ff-b47a-4cc4-a04c-62d684d74a1f

FILES
~/SCS/aws/aws_api_auth.json

DOCUMENT EXAMPLE
{"api-key": "de92c5ff-b47a-4cc4-a04c-62d684d74a1f"}

SEE ALSO
scs_dev/aws_topic_history
"""

import sys

from scs_core.aws.client.api_auth import APIAuth
from scs_core.data.json import JSONify

from scs_host.sys.host import Host

from scs_analysis.cmd.cmd_aws_api_auth import CmdAWSAPIAuth


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdAWSAPIAuth()

    if cmd.verbose:
        print(cmd, file=sys.stderr)
        sys.stderr.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # run...

    if cmd.set():
        auth = APIAuth(cmd.api_key)

        auth.save(Host)

    else:
        # find self...
        auth = APIAuth.load(Host)

    print(JSONify.dumps(auth))
