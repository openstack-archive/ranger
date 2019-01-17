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

ARG user

# Create user for ranger
RUN useradd -u 1000 -ms /bin/false ${user:-ranger}

# Change permissions
RUN  mkdir -p /etc/ranger \
    && mkdir /var/log/ranger \
   && mkdir /home/${user:-ranger}/git_repo \
    && chown -R ${user:-ranger}: /var/log/ranger \
    && mv /tmp/ranger /home/${user:-ranger}/ranger \
    && chown -R ${user:-ranger}: /home/${user:-ranger} \
    && chown -R ${user:-ranger}: /etc/ranger

# Set work directory
USER ${user:-ranger}
WORKDIR /home/${user:-ranger}
