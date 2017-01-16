#!/usr/bin/env python3

'''
Created on 5 Aug 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
'''

import os
import threading
import time


# --------------------------------------------------------------------------------------------------------------------
# run...

while True:
    print("pid:%d" % os.getpid())
    print("thread:%d" % threading.current_thread().ident)
    time.sleep(2)
