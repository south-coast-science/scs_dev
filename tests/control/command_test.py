#!/usr/bin/env python3

"""
Created on 20 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import json

from collections import OrderedDict

from scs_core.control.command import Command
from scs_core.data.json import JSONify

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

tokens = ['test']


# --------------------------------------------------------------------------------------------------------------------

command = Command.construct_from_tokens(tokens)
print("command: %s" % command)
print("is_valid: %s" % command.is_valid(Host))
print("-")

success = command.execute(Host)
print("success: %s" % success)

print("stdout: %s" % command.stdout)
print("stderr: %s" % command.stderr)
print("return_code: %s" % command.return_code)
print("-")

jstr = JSONify.dumps(command)

print(jstr)
print("-")

jdict = json.loads(jstr, object_pairs_hook=OrderedDict)

command = Command.construct_from_jdict(jdict)
print("command: %s" % command)
print("-")

command = Command.construct_from_tokens(['test', '|'])
print("command: %s" % command)
print("is_valid: %s" % command.is_valid(Host))
print("-")

