#!/bin/bash

set -e

pwd

# setup miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p

export PATH=${PATH}:${HOME}/miniconda3/bin

# install requirements
conda env update --name=grabseqs-test --file environment.yml -q
