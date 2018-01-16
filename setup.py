from setuptools import setup, find_packages


with open('requirements.txt') as req_txt:
    required = [line for line in req_txt.read().splitlines() if line]

setup(
    name='scs_dev',
    version='0.1.2',
    description='High-level scripts and command-line applications for South Coast Science data producers.',
    author='South Coast Science',
    author_email='contact@southcoastscience.com',
    url='https://github.com/south-coast-science/scs_dev',
    package_dir={'':'src'},
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
    install_requires=required,
    platforms=['any'],
    python_requires=">=3.3",
    scripts = [
        'src/scs_dev/aws_api_auth.py',
        'src/scs_dev/aws_mqtt_client.py',
        'src/scs_dev/aws_topic_publisher.py',
        'src/scs_dev/aws_topic_subscriber.py',
        'src/scs_dev/climate_sampler.py',
        'src/scs_dev/control_receiver.py',
        'src/scs_dev/csv_reader.py',
        'src/scs_dev/csv_writer.py',
        'src/scs_dev/dfe_power.py',
        'src/scs_dev/dfe_product_id.py',
        'src/scs_dev/gases_sampler.py',
        'src/scs_dev/led.py',
        'src/scs_dev/modem_power.py',
        'src/scs_dev/ndir_sampler.py',
        'src/scs_dev/node.py',
        'src/scs_dev/opc_power.py',
        'src/scs_dev/osio_mqtt_client.py',
        'src/scs_dev/osio_topic_publisher.py',
        'src/scs_dev/osio_topic_subscriber.py',
        'src/scs_dev/particulates_sampler.py',
        'src/scs_dev/ps.py',
        'src/scs_dev/psu.py',
        'src/scs_dev/scheduler.py',
        'src/scs_dev/socket_receiver.py',
        'src/scs_dev/socket_sender.py',
        'src/scs_dev/status_sampler.py',
        'src/scs_dev/uptime.py',
    ]
)