#!/usr/bin/env bash

GIT_PATH=~/SCS/scs_core/
echo ${GIT_PATH}
git -C ${GIT_PATH} pull
echo '-'

GIT_PATH=~/SCS/scs_dev/
echo ${GIT_PATH}
git -C ${GIT_PATH} pull
echo '-'

GIT_PATH=~/SCS/scs_dfe_eng/         # replace with the appropriate board package, as necessary
echo ${GIT_PATH}
git -C ${GIT_PATH} pull
echo '-'

GIT_PATH=~/SCS/scs_host_rpi/        # replace with the appropriate host package, as necessary
echo ${GIT_PATH}
git -C ${GIT_PATH} pull
echo '-'

GIT_PATH=~/SCS/scs_mfr/
echo ${GIT_PATH}
git -C ${GIT_PATH} pull
echo '-'

#GIT_PATH=~/SCS/scs_ndir/           # uncomment if the NDIR package is installed
#echo ${GIT_PATH}
#git -C ${GIT_PATH} pull
#echo '-'

