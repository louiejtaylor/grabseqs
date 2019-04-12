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
python setup.py install -q

# basic tests
grabseqs -v
grabseqs -h

#####
# SRA
#####

## test sample listing, metadata download
if [ `grabseqs sra -m SRP057027.tsv -l -o $TMPDIR/test_metadata/ SRP057027 | wc -l` -ne 370 ]; then
    exit 1
fi
echo -e "$PASS SRA sample listing test passed"

## test metadata download
if [ `cat $TMPDIR/test_metadata/SRP057027.tsv | wc -l` -ne 370 ] ; then
    exit 1
fi
echo -e "$PASS SRA metadata test passed"

## test behavior with -l and --no_parsing
if [ `grabseqs sra -l --no_parsing SRR1804203 | wc -l` -ne 1 ]; then
    exit 1
fi
echo -e "$PASS SRA sample listing test with SRR parsing disabled passed"

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
echo $t
if [[ $t != *"Pass -f to force download"* ]] ; then
    exit 1
fi
echo -e "$PASS SRA no-clobber test passed"

## test force
tf=`grabseqs sra -t 2 -o $TMPDIR/test_fastqdump_sra -f ERR2279063`
if [[ $tf == *"Pass -f to force download"* ]] ; then
    exit 1
fi
echo -e "$PASS SRA force download test passed"

##########
# iMicrobe
##########

## test sample listing and metadata download
#if [ `grabseqs imicrobe -o $TMPDIR/test_md_im -m META.csv -l p1 | wc -l` -ne 3 ]; then
#    exit 1
#fi
#echo -e "$PASS iMicrobe sample listing test passed"

## test metadata download
#if [ `cat $TMPDIR/test_md_im/META.csv | wc -l` -ne 3 ] ; then
#    exit 1
#fi
#echo -e "$PASS iMicrobe metadata test passed"

## paired sample listing
#ps=`grabseqs imicrobe -l s6398`
#if [ "$ps" != "s6398_1.fastq.gz,s6398_2.fastq.gz" ]; then
#    exit 1
#fi
#echo -e "$PASS iMicrobe single-sample listing test passed"

## download a tiny sample, .fasta-formatted
#grabseqs imicrobe -o $TMPDIR/test_tiny_im s710
#ls $TMPDIR/test_tiny_im/s710.fastq.gz  > /dev/null
#echo -e "$PASS iMicrobe fasta-formatted sample download test passed"

## download a tiny sample, .fastq-formatted paired
#grabseqs imicrobe -o $TMPDIR/test_tiny_im s6399
#ls $TMPDIR/test_tiny_im/s6399_1.fastq.gz  > /dev/null
#ls $TMPDIR/test_tiny_im/s6399_2.fastq.gz  > /dev/null
#echo -e "PASS iMicrobe fastq-formatted sample download test passed"

## test no clobber
#t=`grabseqs imicrobe -t 2 -o $TMPDIR/test_tiny_im s710`
#echo $t
#if [[ $t != *"Pass -f to force download"* ]] ; then
#    exit 1
#fi
#echo -e "$PASS iMicrobe no-clobber test passed"

## test force
#tf=`grabseqs imicrobe -t 2 -o $TMPDIR/test_tiny_im -f s710`
#if [[ $tf == *"Pass -f to force download"* ]] ; then
#    exit 1
#fi
#echo -e "$PASS iMicrobe force download test passed"


#########
# MG-RAST
#########

## test sample listing, metadata download
if [ `grabseqs mgrast -o $TMPDIR/test_md_mg -m META.csv -l mgp85479 | wc -l` -ne 5 ]; then
    exit 1
fi
echo -e "$PASS MG-RAST sample listing test passed"

## test metadata
if [ `cat $TMPDIR/test_md_mg/META.csv | wc -l` -ne 5 ] ; then
    exit 1
fi
echo -e "$PASS MG-RAST metadata test passed"

## download a tiny sample, .fastq-formatted
grabseqs mgrast -o $TMPDIR/test_tiny_mg mgm4793571.3
ls $TMPDIR/test_tiny_mg/mgm4793571.3.fastq.gz > /dev/null
echo -e "$PASS MG-RAST unpaired sample download test passed (fastq-formatted)"

## download a tiny sample, .fasta-formatted
grabseqs mgrast -o $TMPDIR/test_tiny_mg_fasta mgm4633450.3
ls $TMPDIR/test_tiny_mg_fasta/mgm4633450.3.fastq.gz > /dev/null
echo -e "$PASS MG-RAST fasta-formatted sample download test passed"

## test no clobber
u=`grabseqs mgrast -o $TMPDIR/test_tiny_mg mgm4793571.3`
echo $u
if [[ $u != *"Pass -f to force download"* ]] ; then
    exit 1
fi
echo -e "$PASS MG-RAST no-clobber test passed"

## test force
u=`grabseqs mgrast -o $TMPDIR/test_tiny_mg -f mgm4793571.3`
if [[ $u == *"Pass -f to force download"* ]] ; then
    exit 1
fi
echo -e "$PASS MG-RAST force download test passed"

# test conda install
conda install -c louiejtaylor -qy grabseqs 
echo -e "$PASS conda install test passed"

# cleanup
rm -r $TMPDIR
source deactivate
conda env remove -n grabseqs-unittest -qy > /dev/null

echo -e "$PASS all tests passed!"
