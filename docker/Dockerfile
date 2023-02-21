FROM ubuntu:latest

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update

RUN apt-get install -y curl  git ffmpeg net-tools\
      python3.10 python3-distutils python3.8-dev 

RUN apt-get clean

# WE ARE NOT GOING TO USE THE UBUNTU SYSTEM PACKAGE MANAGER FOR PYTHON PACKAGES.  SO WE WILL USE PIP.

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py

RUN python3 get-pip.py

COPY requirements.txt .

RUN pip3 install -r requirements.txt