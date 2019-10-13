FROM mongo:3.4.23-xenial

RUN set -ex \
 && apt-get update \
 && apt-get install -y python python-pip \
 && pip install migrate-anything \
 && apt-get clean

COPY . /test
