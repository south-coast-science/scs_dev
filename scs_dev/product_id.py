#!/usr/bin/env python3

"""
Created on 26 Sep 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./product_id.py
"""

import sys

from scs_core.data.json import JSONify
from scs_core.sys.exception_report import ExceptionReport

from scs_dfe.board.dfe_product_id import DFEProductID


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    try:

        # ------------------------------------------------------------------------------------------------------------
        # resources...

        product_id = DFEProductID()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        jstr = JSONify.dumps(product_id)
        print(jstr)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)
