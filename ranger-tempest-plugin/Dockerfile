FROM ubuntu:16.04

ENV DEBIAN_FRONTEND noninteractive
ENV container docker
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

RUN apt -qq update && \
apt -y install git \
netcat \
netbase \
openssh-server \
python-minimal \
python-setuptools \
python-pip \
python-dev \
python-dateutil \
ca-certificates \
openstack-pkg-tools \
apache2 \
libmysqlclient-dev \
gcc \
g++ \
libffi-dev \
libssl-dev --no-install-recommends \
&& apt-get clean \
&& rm -rf \
     /var/lib/apt/lists/* \
     /tmp/* \
     /var/tmp/* \
     /usr/share/man \
     /usr/share/doc \
     /usr/share/doc-base
RUN pip install -U setuptools --user
RUN pip install wheel --user
RUN pip install --upgrade six
# RUN pip install virtualenv


##########################################################################
### aic-orm-tempest-plugin  setup
##########################################################################
WORKDIR /
# COPY  ranger-tempest-plugin/. ranger-tempest-plugin/
COPY . ranger-tempest-plugin/

WORKDIR /ranger-tempest-plugin/
RUN python setup.py develop

##########################################################################
### END OF ranger-tempest-plugin setup 
##########################################################################

##########################################################################
### openstack tempest setup steps
##########################################################################
##
### reset workdir to root before executing tempest steps
WORKDIR /
##
### git clone tempest
RUN git clone https://git.openstack.org/openstack/tempest

### change requirements params - customized for ranger tempest
RUN sed -i 's/paramiko>=.*/paramiko<2.1.3,>=2.0/g' \
    /tempest/requirements.txt
# if os-testr exists, replace os-testr line else insert after PrettyTable line
RUN grep -q 'os-testr.*' /tempest/requirements.txt \
    && sed -i 's/os-testr.*/os-testr==0.8.0/' /tempest/requirements.txt \
    || sed -i '/PrettyTable.*/a os-testr==0.8.0' /tempest/requirements.txt

### now run 'pip install -r requirements'
RUN pip install -r /tempest/requirements.txt
RUN pip install -r /tempest/test-requirements.txt

### create required tempest directories - and remove .stestr folder
RUN mkdir -p /tempest/logs \
    && mkdir -p /tempest/tempest_lock \
    && mkdir -p /tempest/images \
    && mkdir -p /var/log/tempest \
    && rm -rf /tempest/.stestr

# copy tempest test setup files
COPY tempest_setup/.testr.conf  /tempest/
COPY tempest_setup/create_tenant.sh  /tempest/
COPY tempest_setup/accounts.yaml  /tempest/etc
COPY tempest_setup/tempest.conf  /tempest/etc

##########################################################################
### END OF  openstack tempest setup steps
##########################################################################

##########################################################################
### RUN tempest tests on test_regions  
##########################################################################
### create egg-info for tempest
WORKDIR /tempest/
RUN python /tempest/setup.py develop
#ENTRYPOINT ostestr run ranger_tempest_plugin.tests.api.test_regions \
#   && /bin/bash
#ENTRYPOINT ostestr run ranger_tempest_plugin.tests.api.test_flavors/ \
#   && /bin/bash
#ENTRYPOINT ostestr run ranger_tempest_plugin.tests.api.test_customers/ \
#   && /bin/bash
#ENTRYPOINT ostestr run ranger_tempest_plugin.tests.api.test_images/ \
#   && /bin/bash

