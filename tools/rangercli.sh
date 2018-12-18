#!/bin/bash
# Copyright 2018 AT&T Intellectual Property.  All other rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -e

# rangercli require  /${HOME}/openrc environment file that contains all the
# required env variables to run the ranger CLI commands.
envfile="${HOME}/openrc"

if [ ! -f $envfile ]
then
    echo "Environment file $envfile not found."
    exit 1
fi

# source the environment file if exists
. ${HOME}/openrc

# User can run the script as they would execute the ranger CLI.
# For instance, to run the './orm cms create_customer' command, user can execute
# the following command after setting up the required environment variables:
#
# $ ./rangercli.sh ./orm cms create_customer /target/cms/create_basic_cms.json
#

# NOTE: If user is executing the script from outside the cluster, e.g. from
# a remote jump server, then he/she will need to ensure that the DNS server
# is able to resolve the FQDN of the Ranger and Keystone public URL (both
# will be pointing to the IP of the Ingress Controller). If the DNS resolution
# is not available, the user will need to ensure that the /etc/hosts file is
# properly updated before running the script.


### Additional variables required to run ranger cli commands:
# RANGERCLI_HOSTPATH: we'll always use '/target' as defined below
RANGERCLI_HOSTPATH=${RANGERCLI_HOSTPATH:-"/target"}
# RANGERCLI_JSONPATH = provide full path of your ranger CLiJSON files
RANGERCLI_JSONPATH=${RANGERCLI_JSONPATH}
# RANGERCLI_IMAGE = provide rangercli docker image name to use
RANGERCLI_IMAGE=${RANGERCLI_IMAGE}

# Define Base Docker Command
base_docker_command=$(cat << EndOfCommand
sudo docker run -t --rm --net=host
-e http_proxy=${HTTP_PROXY}
-e https_proxy=${HTTPS_PROXY}
-e no_proxy=${NO_PROXY:-127.0.0.1,localhost,.svc.cluster.local}
-e RANGER_USERNAME=${RANGER_USERNAME:-ranger-admin}
-e RANGER_TENANT_NAME=${RANGER_TENANT_NAME:-service}
-e RANGER_PASSWORD=${RANGER_PASSWORD:-xxxxxxxx}
-e RANGER_AUTH_REGION=${RANGER_AUTH_REGION}
-e RANGER_CMS_BASE_URL=${RANGER_CMS_BASE_URL}
-e RANGER_FMS_BASE_URL=${RANGER_FMS_BASE_URL}
-e RANGER_IMS_BASE_URL=${RANGER_IMS_BASE_URL}
-e RANGER_RMS_BASE_URL=${RANGER_RMS_BASE_URL}
-e verify=False
-it 
EndOfCommand
)

# Execute Ranger CLI
${base_docker_command} -v "${RANGERCLI_JSONPATH}":"${RANGERCLI_HOSTPATH}" "${RANGERCLI_IMAGE}" $@
