# grabseqs

Utility for simplifying bulk downloading data from next-generation sequencing repositories, like [NCBI SRA](https://www.ncbi.nlm.nih.gov/sra/), [MG-RAST](http://www.mg-rast.org/), and [iMicrobe](https://www.imicrobe.us/).

[![CircleCI](https://circleci.com/gh/louiejtaylor/grabseqs.svg?style=shield)](https://circleci.com/gh/louiejtaylor/grabseqs) [![Conda version](https://anaconda.org/louiejtaylor/grabseqs/badges/version.svg)](https://anaconda.org/louiejtaylor/grabseqs) [![Conda downloads](https://anaconda.org/louiejtaylor/grabseqs/badges/downloads.svg)](https://anaconda.org/louiejtaylor/grabseqs/files)

## Install

Install grabseqs and all dependencies [via conda](https://conda.io/projects/conda/en/latest/user-guide/getting-started.html):

    conda install grabseqs -c louiejtaylor -c bioconda -c conda-forge

Or with pip (and install the non-Python [dependencies](https://github.com/louiejtaylor/grabseqs#dependencies) yourself):

    pip install grabseqs
    
**Note:** If you're using SRA data, after you've installed sra-tools, run `vdb-config -i` and turn off local file caching unless you want extra copies of the downloaded sequences taking up space ([read more here](https://github.com/ncbi/sra-tools/wiki/Toolkit-Configuration)).

## Quick start

Download all samples from a single SRA Project:

    grabseqs sra SRP#######
    
Or any combination of projects (S/ERP), runs (S/ERR), BioProjects (PRJNA):

    grabseqs sra SRR######## ERP####### PRJNA######## ERR########

If you'd like to do a dry run and just get a list of samples that will be downloaded, pass `-l`:
    
    grabseqs sra -l SRP########

Similar syntax works for MG-RAST:

    grabseqs mgrast mgp##### mgm#######

And iMicrobe (prefixing the sample numbers with "s" and project numbers with "p"):

    grabseqs imicrobe p4 s3

## Detailed usage

See the [grabseqs FAQ](https://github.com/louiejtaylor/grabseqs/blob/master/faq/FAQ.md) for detailed troubleshooting tips!

Fun options:

    grabseqs sra -t 10 -m metadata.csv -o proj/ -r 3 SRP#######

(translation: use 10 threads, save metadata to `proj/metadata.csv`, download to the dir `proj/`, retry failed downloads 3x, get all samples from SRP#######)
    
If you'd like to do a dry run and only get a list of samples that will be downloaded, pass `-l`:
    
    grabseqs sra -l SRP########

If you'd like to pass your own arguments to `fasterq-dump` to get data in a slightly different format, you can do so like this:

    grabseqs sra SRP####### -r 0 --custom_fqdump_args="--split-spot"

Full usage:

    grabseqs sra [-h] [-m METADATA] [-o OUTDIR] [-r RETRIES] [-t THREADS]
                 [-f] [-l] [--no_parsing] [--parse_run_ids]
                 [--use_fastq_dump]
                 id [id ...]

    positional arguments:
      id                One or more BioProject, ERR/SRR or ERP/SRP number(s)

    optional arguments:
      -h, --help        show this help message and exit
      -m METADATA       filename in which to save SRA metadata (.csv format,
                        relative to OUTDIR)
      -o OUTDIR         directory in which to save output. created if it doesn't
                        exist
      -r RETRIES        number of times to retry download
      -t THREADS        threads to use (for fasterq-dump/pigz)
      -f                force re-download of files
      -l                list (but do not download) samples to be grabbed
      --parse_run_ids   parse SRR/ERR identifers (do not pass straight to fasterq-
                        dump)
      --custom_fqdump_args CUSTOM_FQD_ARGS
                        "string" containing args to pass to fastq-dump
      --use_fastq_dump  use legacy fastq-dump instead of fasterq-dump (no
                        multithreaded downloading)
      
Downloads .fastq.gz files to `OUTDIR` (or the working directory if not specified). If the `-m` flag is passed, saves metadata to `OUTDIR` with filename `METADATA` in csv format.

Similar options are available for downloading from MG-RAST:

    grabseqs mgrast [-h] [-m METADATA] [-o OUTDIR] [-r RETRIES]
                    [-t THREADS] [-f] [-l]
                    rastid [rastid ...]

And iMicrobe:

    grabseqs imicrobe [-h] [-m METADATA] [-o OUTDIR] [-r RETRIES]
                      [-t THREADS] [-f] [-l]
                      imicrobeid [imicrobeid ...]

## Troubleshooting

See the [grabseqs FAQ](https://github.com/louiejtaylor/grabseqs/blob/master/faq/FAQ.md) for detailed troubleshooting tips. If the FAQs don't fix your problem, feel free to [open an issue](https://github.com/louiejtaylor/grabseqs/issues)!

## Dependencies
  
   - Python 3 (argparse, requests, subprocess, pandas)
   - sra-tools>2.9
   - pigz
   - wget

If you use conda, these will be installed for you!

------------

## Changelog

**Dev version (not yet released)**
 - coming soon!

**0.7.0** (2020-01-29)
 - Allow users to pass custom args to fast(er)q-dump
 - Minor re-writes of download handling code for easier readability

**0.6.1** (2019-12-20)
 - Validate compressed files (fix #8 and #34)
 
**0.6.0** (2019-12-12)
 - Gracefully handle incomplete or missing dependencies
 - Major rewrite of test suite

**0.5.2** (2019-12-05)
 - Improvements to work with multiple versions of Python 3

**0.5.1** (2019-11-23)
 - Hotfix handling outdated versions of sra-tools

**0.5.0** (2019-04-11)
 - Metadata available for all sources in .csv format

## History

This project spawned out of/incorporates code from [hisss](https://github.com/louiejtaylor/hisss); many thanks to [ArwaAbbas](https://github.com/ArwaAbbas) for helping make this work!
