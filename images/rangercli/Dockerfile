FROM ubuntu:16.04

#ubuntu environment variables
ENV DEBIAN_FRONTEND noninteractive
ENV container docker
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

# define and pass application environment variables
ARG ranger_user
ARG ranger_pass
ARG ranger_tenant
ARG ranger_url
ARG ranger_region

ENV RANGER_USERNAME ${ranger_user:-ranger}
ENV RANGER_PASSWORD ${ranger_pass:-password}
ENV RANGER_TENANT_NAME ${ranger_tenant:-admin}
ENV RANGER_ORM_BASE_URL ${ranger_url:-http://127.0.0.1}
ENV RANGER_AUTH_REGION ${ranger_region:-RegionOne}

# install needed components
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
vim \
curl \
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

WORKDIR /tmp
# Create user
RUN useradd -u 1000 -ms /bin/bash ${RANGER_USERNAME}

# Change permissions
RUN  mv /tmp/ranger/orm/orm_client /home/${RANGER_USERNAME}/ \
    && rm -rf /tmp/* \
    && chown -R ${RANGER_USERNAME}: /home/${RANGER_USERNAME}/orm_client

# Set work directory
USER ${RANGER_USERNAME}
WORKDIR /home/${RANGER_USERNAME}/orm_client/ormcli
