# grabseqs

Utility to download reads from all samples relating to a single BioProject/SRP/ERP from NCBI SRA.

(in active development--tests/Conda release coming soon)

## Running

Run like:

    grabseqs sra SRP#######
    
Usage:

    usage: grabseqs sra [-h] [-o OUTDIR] [-m] [-t THREADS] [-r RETRIES] id

    positional arguments:
      id          BioProject or [E/S]RP number

    optional arguments:
      -h, --help  show this help message and exit
      -o OUTDIR   directory in which to save output. created if it doesn't exist.
      -m          save SRA metadata
      -t THREADS  threads to use (for fasterq-dump/pigz)
      -r RETRIES  number of times to retry download
      
 Downloads unzipped (for now) .fastq files to `OUTDIR` (or the working directory if not specified).
      
## Dependencies
  
   - Python 3 (argparse, requests, subprocess)
   - sra-tools
   - pigz

Pass the `requirements.txt` from this repository to Conda to painlessly install all dependencies:
    
    conda install -c bioconda --file requirements.txt 

## Install

Conda recipe coming soon. In the meantime you can clone the repo:

    git clone https://github.com/louiejtaylor/grabseqs

Then run as above:

    cd grabseqs
    ./grabseqs sra SRP#######
