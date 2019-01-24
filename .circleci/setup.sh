#!/bin/bash

set -e

# setup miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p

# CircleCI fix weird error
sudo apt-get install libxtst6 libxi6 libgconf-2-4 libnss3 libasound2

export PATH=${PATH}:${HOME}/miniconda3/bin

