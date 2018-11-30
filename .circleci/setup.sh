#!/bin/bash

set -e

pwd

# setup miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p

export $PATH=${PATH}:~/miniconda3/bin

# install requirements
conda create -n grabseqs-test
source activate grabseqs-test
conda install --file requirements.txt


