#!/usr/bin/env python3

"""
Created on 28 Sep 2023

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

from scs_core.aws.config.project import Project

from scs_core.aws.manager.byline.byline_finder import DeviceBylineFinder

from scs_core.aws.security.cognito_device import CognitoDeviceCredentials
from scs_core.aws.security.cognito_login_manager import CognitoLoginManager

from scs_core.sys.system_id import SystemID

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

system_id = SystemID.load(Host)
print(system_id)

project = Project.load(Host)
print(project)

topic_path = project.subject_path('status', system_id)
print(topic_path)

print("-")

gatekeeper = CognitoLoginManager()
print(gatekeeper)

finder = DeviceBylineFinder()
print(finder)

credentials = CognitoDeviceCredentials.load_credentials_for_device(Host)
print(credentials)

auth = gatekeeper.device_login(credentials)
print(auth)

print("-")

byline = finder.find_byline_for_topic(auth.id_token, topic_path)
print(byline)
