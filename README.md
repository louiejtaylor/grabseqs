# grabseqs

Utility for simplifying bulk downloading data from NCBI SRA.

(in active development--tests and more repositories [MG-RAST] coming soon)

## Quick start

Install:

    conda install -c louiejtaylor -c bioconda grabseqs

Download all samples from a single SRA Project:

    grabseqs sra SRP#######
    
Download a collection of runs individually:

    grabseqs sra SRR######## SRR######## SRR########
    
Or any combination of the above:

    grabseqs sra SRR######## ERP####### PRJNA######## ERR########

## Usage

Fun options:

    grabseqs sra -t 10 -m -o data/ -r 3 SRP#######

(translation: use 10 threads, save metadata, download to the dir `data/`, retry failed downloads 3x, get all samples from SRP#######)

Full usage:

    usage: grabseqs sra [-h] [-o OUTDIR] [-m] [-t THREADS] [-r RETRIES]
                    id [id ...]

    positional arguments:
      id          One or more BioProject, ERR/SRR or ERP/SRP number(s)

    optional arguments:
      -h, --help  show this help message and exit
      -o OUTDIR   directory in which to save output. created if it doesn't exist
      -m          save SRA metadata
      -t THREADS  threads to use (for fasterq-dump/pigz)
      -r RETRIES  number of times to retry download
      
Downloads .fastq.gz files to `OUTDIR` (or the working directory if not specified). If the `-m` flag is passed, saves metadata to `OUTDIR`.

## Dependencies
  
   - Python 3 (argparse, requests, subprocess)
   - sra-tools>2.9
   - pigz

These are automatically installed through Conda--if you don't use Conda, make sure these are installed, then put the executable (bin/grabseqs) somewhere useful.

## History

This project spawned out of/incorporates code from [hisss](https://github.com/louiejtaylor/hisss); many thanks to [ArwaAbbas](https://github.com/ArwaAbbas) for helping make this work!
