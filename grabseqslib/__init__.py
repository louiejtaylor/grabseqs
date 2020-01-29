__all__ = ["utils","sra","mgrast","imicrobe"]

import os, sys, argparse, warnings, shutil
import pandas as pd

from pathlib import Path
from grabseqslib.sra import process_sra, add_sra_subparser
from grabseqslib.imicrobe import process_imicrobe, add_imicrobe_subparser
from grabseqslib.mgrast import process_mgrast, add_mgrast_subparser

def main():
    '''
    Command-line argument-handling function
    '''
    # Set up parsers
    parser = argparse.ArgumentParser(prog="grabseqs",
         description='Download metagenomic sequences from public datasets.')
    parser.add_argument('--version', '-v', action='version', version='%(prog)s 0.7.0')
    subpa = parser.add_subparsers(help='repositories available')

    add_sra_subparser(subpa)
    add_imicrobe_subparser(subpa)
    add_mgrast_subparser(subpa)

    args = parser.parse_args()
    # Make output directories if they don't exist
    try:
        if args.outdir != "":
            if not os.path.exists(args.outdir):
                os.makedirs(args.outdir)
    except AttributeError: 
        # No subcommand provided (all subcomands have `-o`)
        print("Subcommand not specified, run `grabseqs -h` or  `grabseqs {repository} -h` for help")
        sys.exit(0)

    # Figure out which subparser was called
    try:
        if args.rastid:
            repo = "MG-RAST"
    except AttributeError:
        try:
            if args.imicrobeid:
                repo = "iMicrobe"
        except AttributeError:
            repo = "SRA"

    # Check deps
    zip_func = "gzip"
    if shutil.which("pigz"):
        zip_func = "pigz"
    else:
        print("pigz not found, using gzip")

    metadata_agg = None

    # Download samples
    if repo == "SRA":
        metadata_agg = process_sra(args, zip_func)

    elif repo == "MG-RAST":
        metadata_agg = process_mgrast(args, zip_func)

    elif repo == "iMicrobe":
        metadata_agg = process_imicrobe(args, zip_func)

    # Handle metadata
    if args.metadata != "":
        md_path = Path(args.outdir) / Path(args.metadata)
        if not os.path.isfile(md_path):
            metadata_agg.to_csv(md_path, index = False)
            print("Metadata saved to new file: " + str(md_path))
        else:
            metadata_i = pd.read_csv(md_path)
            metadata_f = metadata_i.append(metadata_agg,sort=True)
            metadata_f.to_csv(md_path, index = False)
            print("Metadata appended to existing file: " + str(md_path))
