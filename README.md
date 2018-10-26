# grabseqs

Utility to download reads from all samples relating to a single BioProject/SRP/ERP from NCBI SRA.

(in active development--tests and more features coming soon)

## Quick start

Install:

    conda install -c louiejtaylor -c bioconda grabseqs

Run:

    grabseqs sra SRP#######

## Options

Usage:

    usage: grabseqs sra [-h] [-o OUTDIR] [-m] [-t THREADS] [-r RETRIES] id

    positional arguments:
      id          BioProject or [E/S]RP number

    optional arguments:
      -h, --help  show this help message and exit
      -o OUTDIR   directory in which to save output. created if it doesn't exist.
      -m          save SRA metadata
      -t THREADS  threads to use (for fasterq-dump only)
      -r RETRIES  number of times to retry download
      
Downloads .fastq.gz files to `OUTDIR` (or the working directory if not specified). If the `-m` flag is passed, saves metadata to `OUTDIR`.

## Dependencies
  
   - Python 3 (argparse, requests, subprocess)
   - sra-tools>2.9
   - pigz

These are automatically installed through Conda--if you don't use Conda, make sure these are installed and put the executable (bin/grabseqs) somewhere useful.

## History

This project spawned out of/incorporates code from [hisss](https://github.com/louiejtaylor/hisss); many thanks to @ArwaAbbas for helping make this work!
