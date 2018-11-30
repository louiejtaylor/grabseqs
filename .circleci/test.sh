#!/bin/bash

set -e

# setup
export PATH=${PATH}:${HOME}/miniconda3/bin
source activate grabseqs-test

# basic tests
python bin/grabseqs -v
python bin/grabseqs -h

# more thorough tests
mkdir -p $HOME/tmp_test
if [ `python bin/grabseqs sra -l SRP057027 | wc -l` -ne 369 ] ; then
    exit 1
fi
