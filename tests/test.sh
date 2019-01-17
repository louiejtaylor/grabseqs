#!/bin/bash

# setup
set -e
export PATH=${PATH}:${HOME}/miniconda3/bin

# set up temp locations
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
fs=`ls $TMPDIR | wc -l`

if [ $fs -ne 0 ] ; then
    echo "Directory $TMPDIR not empty. Clean it or specify a testing location with -d [loc]"
    exit 1
fi

GREEN="\x1B[32m"
RESET="\x1B[0m"
PASS="${GREEN}\u2714${RESET}"

# environment and package install
conda env update --name=grabseqs-unittest --file environment.yml -q > /dev/null
source activate grabseqs-unittest
python setup.py install

# basic tests
grabseqs -v
grabseqs -h

# SRA
## test sample listing, metadata download
if [ `grabseqs sra -m -l -o $TMPDIR/test_metadata/ SRP057027 | wc -l` -ne 369 ]; then
    exit 1
fi
echo -e "$PASS SRA sample listing test passed"

## test metadata download
if [ `cat $TMPDIR/test_metadata/SRP057027.tsv | wc -l` -ne 371 ] ; then
    exit 1
fi
echo -e "$PASS SRA metadata test passed"

## unpaired fasterq-dump
grabseqs sra -t 2 -o $TMPDIR/test_tiny_sra ERR2279063
ls $TMPDIR/test_tiny_sra/ERR2279063.fastq.gz > /dev/null
echo -e "$PASS SRA unpaired sample download test passed"

## paired fasterq-dump
grabseqs sra -t 2 -o $TMPDIR/test_tiny_sra_paired SRR1913936
ls $TMPDIR/test_tiny_sra_paired/SRR1913936_1.fastq.gz > /dev/null
ls $TMPDIR/test_tiny_sra_paired/SRR1913936_2.fastq.gz > /dev/null
echo -e "$PASS SRA paired sample download test passed"

## unpaired fastq-dump
grabseqs sra -t 2 -o $TMPDIR/test_fastqdump_sra --use_fastq_dump ERR2279063
ls $TMPDIR/test_fastqdump_sra/ERR2279063.fastq.gz > /dev/null
echo -e "$PASS SRA unpaired sample download using fastq-dump test passed"

## paired fasterq-dump
grabseqs sra -t 2 -o $TMPDIR/test_fastqdump_sra_paired --use_fastq_dump SRR1913936
ls $TMPDIR/test_fastqdump_sra_paired/SRR1913936_1.fastq.gz > /dev/null
ls $TMPDIR/test_fastqdump_sra_paired/SRR1913936_2.fastq.gz > /dev/null
echo -e "$PASS SRA paired sample download using fastq-dump test passed"

## test no clobber
t=`grabseqs sra -t 2 -o $TMPDIR/test_fastqdump_sra ERR2279063`
if [[ $t != *"Pass -f to force download"* ]] ; then
    exit 1
fi
echo -e "$PASS SRA no-clobber passed"

# MG-RAST
## test sample listing
if [ `grabseqs mgrast -l mgp8384 | wc -l` -ne 12 ]; then
    exit 1
fi
echo -e "$PASS MG-RAST sample listing test passed"

## download a tiny sample
grabseqs mgrast -o $TMPDIR/test_tiny_mg mgm4793571.3
ls $TMPDIR/test_tiny_mg/mgm4793571.3.fastq.gz > /dev/null
echo -e "$PASS MG-RAST unpaired sample download test passed"

# test conda install
conda install -c louiejtaylor -qy grabseqs 
echo -e "$PASS conda install test passed"

# cleanup
rm -r $TMPDIR
source deactivate
conda env remove -n grabseqs-unittest -qy > /dev/null

echo -e "$PASS all tests passed!"
