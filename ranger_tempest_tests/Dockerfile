FROM ubuntu:14.04

COPY . /tmp/ranger_tempest

WORKDIR /tmp/ranger_tempest

RUN pip install --default-timeout=100 -r requirements.txt

RUN python setup.py install

# Create user ranger
RUN useradd -u 1000 -ms /bin/bash ranger

# Setup Environment by Cloning tempest
RUN git clone https://github.com/openstack/tempest.git

# installing tempest dependencies
RUN pip install -r /tempest/requirements.txt
RUN pip install -r /tempest/test-requirements.txt

# Copy sample configuration
RUN mkdir /etc/tempest
RUN cp tempest/etc/tempest.conf.sample /etc/tempest/tempest.conf
RUN cp tempest/etc/accounts.yaml.sample /etc/tempest/accounts.yaml.sample

# Running tempest setup
RUN cd tempest && python setup.py install
RUN cd tempest && testr init

# Set work directory
USER root
WORKDIR /opt/app/ranger_tempest

ENTRYPOINT tools/start_services.sh \
 && /bin/bash

