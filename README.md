# grabseqs

Utility for simplifying bulk downloading data from next-generation sequencing repositories, like [NCBI SRA](https://www.ncbi.nlm.nih.gov/sra/) or [MG-RAST](http://www.mg-rast.org/).

[![CircleCI](https://circleci.com/gh/louiejtaylor/grabseqs.svg?style=shield)](https://circleci.com/gh/louiejtaylor/grabseqs)

## Install

Install grabseqs and all dependencies [via conda](https://anaconda.org/louiejtaylor/grabseqs):

    conda install -c louiejtaylor -c bioconda grabseqs

Or with pip (and install the [dependencies](https://github.com/louiejtaylor/grabseqs#dependencies) yourself):

    pip install grabseqs

## Quick start

Download all samples from a single SRA Project:

    grabseqs sra SRP#######
    
Download a collection of runs individually:

    grabseqs sra SRR######## SRR######## SRR########
    
Or any combination of the above:

    grabseqs sra SRR######## ERP####### PRJNA######## ERR########

Similar syntax works for MG-RAST:

    grabseqs mgrast mgp##### mgm#######

## Detailed usage

Fun options:

    grabseqs sra -t 10 -m -o data/ -r 3 SRP#######

(translation: use 10 threads, save metadata, download to the dir `data/`, retry failed downloads 3x, get all samples from SRP#######)
    
If you'd like to do a dry run and just get a list of samples that will be downloaded, pass `-l`:
    
    grabseqs sra -l SRP########


Full usage:

    usage: grabseqs sra [-h] [-o OUTDIR] [-r RETRIES] [-t THREADS] [-f] [-l] [-m]
                        id [id ...]
                        
    positional arguments:
      id          One or more BioProject, ERR/SRR or ERP/SRP number(s)
      
    optional arguments:
      -h, --help        show this help message and exit
      -o OUTDIR         directory in which to save output. created if it doesn't exist
      -r RETRIES        number of times to retry download
      -t THREADS        threads to use (for fasterq-dump/pigz)
      -f                force re-download of files
      -l                list (but do not download) samples to be grabbed
      -m                save SRA metadata
      --no_parsing      do not parse SRR/ERR (pass straight to fasterq-dump)
      --use_fastq_dump  use legacy fastq-dump instead of fasterq-dump (no
                        multithreaded downloading)
 
Downloads .fastq.gz files to `OUTDIR` (or the working directory if not specified). If the `-m` flag is passed, saves metadata to `OUTDIR`.

Similar options are available for downloading from MG-RAST:

    usage: grabseqs mgrast [-h] [-o OUTDIR] [-r RETRIES] [-t THREADS] [-f] [-l]
                           [-m] rastid [rastid ...]
    positional arguments:
      rastid      One or more MG-RAST project or sample identifiers (mgp####/mgm######)

    optional arguments:
      -h, --help  show this help message and exit
      -o OUTDIR   directory in which to save output. created if it doesn't exist
      -r RETRIES  number of times to retry download
      -t THREADS  threads to use (for pigz)
      -f          force re-download of files
      -l          list (but do not download) samples to be grabbed
      -m          save metadata

## Dependencies
  
   - Python 3 (argparse, requests, subprocess)
   - sra-tools>2.9
   - pigz
   - wget

If you use conda, these will be installed for you!

## History

This project spawned out of/incorporates code from [hisss](https://github.com/louiejtaylor/hisss); many thanks to [ArwaAbbas](https://github.com/ArwaAbbas) for helping make this work!
