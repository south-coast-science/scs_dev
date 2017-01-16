#!/usr/bin/env python3

'''
Created on 17 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
'''

import os
import sys

from scs_core.data.json import JSONify

# --------------------------------------------------------------------------------------------------------------------

path = os.environ['PYTHONPATH']
print("PYTHONPATH: %s" % path)
print("-")

syspath = sys.path
print("syspath: %s" % syspath)
print("-")

jstr = JSONify.dumps(syspath)
print("jstr: %s" % jstr)
print("-")


