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
gcc \
g++ \
libffi-dev \
libssl-dev --no-install-recommends \
libmysqlclient-dev \
&& apt-get clean \
&& rm -rf \
     /var/lib/apt/lists/* \
     /tmp/* \
     /var/tmp/* \
     /usr/share/man \
     /usr/share/doc \
     /usr/share/doc-base

RUN pip install wheel

COPY . /tmp/ranger

WORKDIR /tmp/ranger

RUN pip install --default-timeout=100 -r requirements.txt

RUN python setup.py install

# Create user ranger
RUN useradd -u 1000 -ms /bin/bash ranger

# Change permissions
RUN chown -R ranger: /home/ranger \
    && mkdir -p /etc/ranger \
    && chown -R ranger: /etc/ranger \
    && mkdir /var/log/ranger \
    && mkdir -p /opt/app \
    && mkdir /home/ranger/git_repo \
    && chown -R ranger: /var/log/ranger \
    && mv /tmp/ranger /home/ranger/ranger

# Set work directory
USER ranger
WORKDIR /home/ranger
