#!/bin/bash

set -e

# setup
conda env update --name=grabseqs-test --file environment.yml -q
source activate grabseqs-test
python setup.py install

export PATH=${PATH}:${HOME}/miniconda3/bin
source activate grabseqs-test

# basic tests
grabseqs -v
grabseqs -h

# repo grabseqs tests
TMPLOC=/tmp

while getopts "d:" opt; do
  case $opt in
    d)
      TMPLOC=`readlink -f $OPTARG`
      ;;
    \?)
      echo "Unknown option - '$OPTARG'"
      exit 1
      ;;
  esac
done

TMPDIR=$TMPLOC/grabseqs_unittest
mkdir -p $TMPDIR

# SRA
## test sample listing, metadata download
if [ `grabseqs sra -m -l -o $TMPDIR/test_metadata/ SRP057027 | wc -l` -ne 369 ]; then
    exit 1
fi
echo ":D SRA sample listing test passed"

## test metadata download
if [ `cat $TMPDIR/test_metadata/SRP057027.tsv | wc -l` -ne 371 ] ; then
    exit 1
fi
echo ":D SRA metadata test passed"

## download a tiny sample
grabseqs sra -t 2 -o $TMPDIR/test_tiny_sra ERR2279063
ls $TMPDIR/test_tiny_sra/ERR2279063.fastq.gz > /dev/null
echo ":D SRA unpaired sample download test passed"

# MG-RAST
## test sample listing
if [ `grabseqs mgrast -l mgp8384 | wc -l` -ne 12 ]; then
    exit 1
fi
echo ":D MG-RAST sample listing test passed"

## download a tiny sample
grabseqs mgrast -o $TMPDIR/test_tiny_mg mgm4793571.3
ls $TMPDIR/test_tiny_mg/mgm4793571.3.fastq.gz > /dev/null
echo ":D MG-RAST unpaired sample download test passed"

# test conda install
conda install -c louiejtaylor -qy grabseqs 
echo ":D  conda install test passed"

# cleanup
rm -r $TMPDIR
