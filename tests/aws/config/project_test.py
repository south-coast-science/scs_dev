#!/usr/bin/env python3

"""
Created on 9 Nov 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

from scs_core.aws.config.project import Project
from scs_core.sys.system_id import SystemID

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

system_id = SystemID.load(Host)
print(system_id)

project = Project.load(Host)
print(project)
print("-")

print(Project.CHANNELS)
print("-")

paths = project.environment_paths(system_id)

for path in paths:
    print(path)

