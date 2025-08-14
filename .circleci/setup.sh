#!/bin/bash

set -e

# setup miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p ${HOME}

# CircleCI fix weird error
cat .circleci/deplist.txt | xargs sudo apt-get install

export PATH=${PATH}:${HOME}/miniconda3/bin

