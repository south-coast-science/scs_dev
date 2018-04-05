#!/usr/bin/env python3

"""
Created on 26 Sep 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The dfe_product_id utility is used to read the vendor, product ID and product UUID fields from the EEPROM on the
South Coast Science digital front-end (DFE) board.

DFE boards conform to Raspberry Pi HAT and BeagleBone Cape standards, as appropriate, and have differing fields, as
required by the respective standards.

Note: the utility is not currently functional on BeagleBone systems.

SYNOPSIS
dfe_product_id.py

EXAMPLES
./dfe_product_id.py

DOCUMENT EXAMPLE
{"vendor": null, "product": null, "product_id": null, "product_ver": null, "uuid": null}

SEE ALSO
scs_mfr/eeprom_read
scs_mfr/eeprom_write
"""

from scs_core.data.json import JSONify

from scs_dfe.board.dfe_product_id import DFEProductID


# TODO: implement DFEProductID for BeagleBone

# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # resources...

    product_id = DFEProductID()


    # ----------------------------------------------------------------------------------------------------------------
    # run...

    jstr = JSONify.dumps(product_id)
    print(jstr)
