FROM ubuntu:latest

RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends python3-dev python3-pip python3-setuptools build-essential libsodium-dev libsecp256k1-dev libgmp3-dev npm git curl

COPY Makefile Makefile
COPY package.json package.json
COPY requirements.txt requirements.txt

# Patch smartpy
COPY smartpy-patch smartpy-patch

RUN make
