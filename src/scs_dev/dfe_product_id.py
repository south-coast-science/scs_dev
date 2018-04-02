#!/usr/bin/env python3

"""
Created on 26 Sep 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The XX utility is used to .

EXAMPLES
xx

FILES
~/SCS/aws/

DOCUMENT EXAMPLE
xx

SEE ALSO
scs_dev/


command line example:
./dfe_product_id.py
"""

from scs_core.data.json import JSONify

from scs_dfe.board.dfe_product_id import DFEProductID


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # resources...

    product_id = DFEProductID()


    # ----------------------------------------------------------------------------------------------------------------
    # run...

    jstr = JSONify.dumps(product_id)
    print(jstr)
