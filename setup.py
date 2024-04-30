#!/usr/bin/env python3

"""
Created on 4 Sep 2020
Updated 23 Mar 2021

@author: Jade Page (jade.page@southcoastscience.com)

https://packaging.python.org/tutorials/packaging-projects/
https://packaging.python.org/guides/single-sourcing-package-version/
"""

import codecs
import os

from setuptools import setup, find_packages


# --------------------------------------------------------------------------------------------------------------------

def read(rel_path):
    here = str(os.path.abspath(os.path.dirname(__file__)))
    with codecs.open(os.path.join(here, rel_path)) as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            return line.split("'")[1]
    else:
        raise RuntimeError("Unable to find version string.")


# --------------------------------------------------------------------------------------------------------------------

with open('requirements.txt') as req_txt:
    required = [line for line in req_txt.read().splitlines() if line]


setup(
    name='scs_dev',
    version=get_version("src/scs_dev/__init__.py"),
    description='High-level scripts and command-line applications for South Coast Science data producers.',
    author='South Coast Science',
    author_email='contact@southcoastscience.com',
    url='https://github.com/south-coast-science/scs_dev',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: POSIX',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    scripts=[
        'src/scs_dev/aws_mqtt_client.py',
        'src/scs_dev/aws_topic_publisher.py',
        'src/scs_dev/aws_topic_subscriber.py',
        'src/scs_dev/climate_sampler.py',
        'src/scs_dev/control_receiver.py',
        'src/scs_dev/csv_logger.py',
        'src/scs_dev/csv_reader.py',
        'src/scs_dev/csv_writer.py',
        'src/scs_dev/dfe_product_id.py',
        'src/scs_dev/disk_usage.py',
        'src/scs_dev/disk_volume.py',
        'src/scs_dev/display.py',
        'src/scs_dev/gases_sampler.py',
        'src/scs_dev/interface_power.py',
        'src/scs_dev/led.py',
        'src/scs_dev/led_controller.py',
        'src/scs_dev/modem_power.py',
        'src/scs_dev/node.py',
        'src/scs_dev/opc_cleaner.py',
        'src/scs_dev/particulates_inference.py',
        'src/scs_dev/particulates_sampler.py',
        'src/scs_dev/pressure_sampler.py',
        'src/scs_dev/ps.py',
        'src/scs_dev/psu.py',
        'src/scs_dev/psu_monitor.py',
        'src/scs_dev/scheduler.py',
        'src/scs_dev/socket_sender.py',
        'src/scs_dev/status_sampler.py',
        'src/scs_dev/uds_receiver.py',
        'src/scs_dev/uptime.py'
    ],
    install_requires=required,
    platforms=['any'],
    python_requires=">=3.3"
)
