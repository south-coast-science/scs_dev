# scs_dev
High-level scripts and command-line applications for South Coast Science data producers.

_Contains command line utilities and library classes._


**Required libraries:** 

* Third party: AWSIoTPythonSDK, paho-mqtt, pyserial
* SCS root:  scs_core
* SCS host:  scs_host_bbe, scs_host_bbe_southern or scs_host_rpi
* SCS dfe:   scs_dfe_eng
* SCS NDIR:  scs_ndir_alphasense
* SCS PSU:   scs_psu


**Branches:**

The stable branch of this repository is master. For deployment purposes, use:

    git clone --branch=master https://github.com/south-coast-science/scs_dev.git


**Example PYTHONPATH:**

Raspberry Pi, in /home/pi/.bashrc:

    export PYTHONPATH=~/SCS/scs_analysis/src:~/SCS/scs_dev/src:~/SCS/scs_osio/src:~/SCS/scs_mfr/src:~/SCS/scs_dfe_eng/src:~/SCS/scs_ndir/src:~/SCS/scs_host_rpi/src:~/SCS/scs_core/src:$PYTHONPATH


BeagleBone, in /root/.bashrc:

    export PYTHONPATH=/home/debian/SCS/scs_dev/src:/home/debian/SCS/scs_osio/src:/home/debian/SCS/scs_mfr/src:/home/debian/SCS/scs_psu/src:/home/debian/SCS/scs_comms_ge910/src:/home/debian/SCS/scs_dfe_eng/src:/home/debian/SCS/scs_ndir/src:/home/debian/SCS/scs_host_bbe/src:/home/debian/SCS/scs_core/src:$PYTHONPATH


BeagleBone, in /home/debian/.bashrc:

    export PYTHONPATH=~/SCS/scs_dev/src:~/SCS/scs_osio/src:~/SCS/scs_mfr/src:~/SCS/scs_psu/src:~/SCS/scs_comms_ge910/src:~/SCS/scs_dfe_eng/src:~debian/SCS/scs_ndir/src:~/SCS/scs_host_bbe/src:~/SCS/scs_core/src:$PYTHONPATH
