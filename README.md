# scs_dev
High-level scripts and command-line applications for South Coast Science data producer developers.

**Required libraries:** 

* Third party: paho-mqtt, pyserial
* SCS root:  scs_core
* SCS host:  scs_host_bbe or scs_host_rpi
* SCS NDIR:  scs_ndir_alphasense
* SCS dfe:   scs_dfe_eng


**Example PYTHONPATH:**

**Raspberry Pi, in /home/pi/.profile:**

export \\
PYTHONPATH=\~/SCS/scs_analysis:\~/SCS/scs_dev:\~/SCS/scs_osio:\~/SCS/scs_mfr:\~/SCS/scs_dfe_eng:\~/SCS/scs_ndir_alphasense:\~/SCS/scs_host_rpi:\~/SCS/scs_core:$PYTHONPATH


**Beaglebone, in /root/.bashrc:**

export \\
PYTHONPATH=/home/debian/SCS/scs_dev:/home/debian/SCS/scs_osio:/home/debian/SCS/scs_mfr:/home/debian/SCS/scs_psu:/home/debian/SCS/scs_comms_ge910:/home/debian/SCS/scs_dfe_eng:/home/debian/SCS/scs_ndir_alphasense:/home/debian/SCS/scs_host_bbe:/home/debian/SCS/scs_core:$PYTHONPATH


**Beaglebone, in /home/debian/.bashrc:**

export \\
PYTHONPATH=\~/SCS/scs_dev:\~/SCS/scs_osio:\~/SCS/scs_mfr:\~/SCS/scs_psu:\~/SCS/scs_comms_ge910:\~/SCS/scs_dfe_eng:~debian/SCS/scs_ndir_alphasense:\~/SCS/scs_host_bbe:\~/SCS/scs_core:$PYTHONPATH
