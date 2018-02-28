#!/usr/bin/env bash

# An example git pull script, normally copied to ~/SCS and incorporating all repos

GIT_PATH=~/SCS/scs_dev/
echo ${GIT_PATH}
git -C ${GIT_PATH} pull
echo '-'

GIT_PATH=~/SCS/scs_core/
echo ${GIT_PATH}
git -C ${GIT_PATH} pull
echo '-'

GIT_PATH=~/SCS/scs_dfe_eng/
echo ${GIT_PATH}
git -C ${GIT_PATH} pull
echo '-'

GIT_PATH=~/SCS/scs_host_posix/          # replace with the appropriate host package
echo ${GIT_PATH}
git -C ${GIT_PATH} pull
echo '-'

GIT_PATH=~/SCS/scs_osio/
echo ${GIT_PATH}
git -C ${GIT_PATH} pull
echo '-'
