#!/bin/bash

set -e
export TERM=xterm-color

# =========================================================================
# This script will find all the changed python files and run
# 1. flake8
# 3. pylint
# for each of the changed file and provide the relevant output
# =========================================================================

TOXINIDIR=$1
CHECKTYPE=$2
POSTARGS=$3
PYLINTRCFILE=${TOXINIDIR}/pylintrc
FLAKERC=${TOXINIDIR}/flake8rc

# Find all the changed python files that needs to be checked / linted for
# ====================================================================
# If dev is passed as {postargs} then it is indicative that the
# check will be performed in a local dev environment
# Else it is indicative of a pipeline for container build process
# ====================================================================

if [[ "${POSTARGS}" = "dev" ]]; then
    CHANGEDFILES=($(git status -s | grep -v 'D' | egrep '\.py' | awk -F ' ' '{print $2}' || true))
    LENGTHARR=${#CHANGEDFILES[@]}
else
    CHANGEDFILES=($(git diff-tree --no-commit-id --name-only --diff-filter AM -r HEAD | egrep '\.py' || true))
    LENGTHARR=${#CHANGEDFILES[@]}
fi


for ((i=0;i<$LENGTHARR; i++));do
    echo "$(tput setaf 4)============================================================$(tput setaf 9)"
    echo "$(tput setaf 5) Performing check on ${CHANGEDFILES[i]}$(tput setaf 9)"
    echo "$(tput setaf 4)============================================================$(tput setaf 9)"
    echo ${CHANGEDFILES[i]}
    if [[ "${CHECKTYPE}" = "flake" ]]; then
        flake8 --config=$FLAKERC ${CHANGEDFILES[i]}
    elif [[ "${CHECKTYPE}" = "pylint" ]]; then
        pylint -rn --rcfile=$PYLINTRCFILE ${CHANGEDFILES[i]}
    fi
done

