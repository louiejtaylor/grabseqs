#!/bin/bash

# re-set-up
export PATH=${PATH}:${HOME}/miniconda3/bin
source activate grabseqs-test

python bin/grabseqs -v
python bin/grabseqs -h
