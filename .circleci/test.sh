#!/bin/bash

set -e

# setup
export PATH=${PATH}:${HOME}/miniconda3/bin
source activate grabseqs-test

# basic tests
python bin/grabseqs -v
python bin/grabseqs -h

# repo grabseqs tests
mkdir -p $HOME/tmp_test

# SRA
## test sample listing, metadata download
if [ `python bin/grabseqs sra -m -l -o $HOME/tmp_test/test_metadata/ SRP057027 | wc -l` -ne 369 ]; then
    exit 1
fi
echo ":D SRA sample listing test passed"
## test metadata download
if [ `cat $HOME/tmp_test/test_metadata/SRP057027.tsv | wc -l` -ne 371 ] ; then
    exit 1
fi
echo ":D SRA metadata test passed"
## download a tiny sample
python bin/grabseqs sra -t 2 -o $HOME/tmp_test/test_tiny_sra ERR2279063
ls $HOME/tmp_test/test_tiny_sra/ERR2279063.fastq.gz > /dev/null
echo ":D SRA unpaired sample download test passed"

# MG-RAST
## test sample listing
if [ `python bin/grabseqs mgrast -l mgp8384 | wc -l` -ne 12 ]; then
    exit 1
fi
echo ":D MG-RAST sample listing test passed"
## download a tiny sample
python bin/grabseqs mgrast -o $HOME/tmp_test/test_tiny_mg mgm4793571.3
ls $HOME/tmp_test/test_tiny_mg/mgm4793571.3.fastq.gz > /dev/null
echo ":D MG-RAST unpaired sample download test passed"

# test conda install
conda install -c louiejtaylor --quiet grabseqs 
echo ":D  conda install test passed"

# cleanup
rm -r $HOME/tmp_test
