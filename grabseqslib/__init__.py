__all__ = ["utils","sra","mgrast","imicrobe"]

import os, sys, argparse

from grabseqslib.sra import get_sra_acc_metadata, run_fasterq_dump, add_sra_subparser
from grabseqslib.imicrobe import get_imicrobe_acc_metadata, download_imicrobe_sample, add_imicrobe_subparser
from grabseqslib.mgrast import get_mgrast_acc_metadata, download_mgrast_sample, add_mgrast_subparser

def main():

	# Top-level parser
	parser = argparse.ArgumentParser(prog="grabseqs",
		 description='Download metagenomic sequences from public datasets.')
	parser.add_argument('--version', '-v', action='version', version='%(prog)s 0.4.0')
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
	except AttributeError: # No subcommand provided (all subcomands have `-o`)
		print("Subcommand not specified, run `grabseqs -h` or  `grabseqs {repository} -h` for help")
		sys.exit(0)

	# Figure out which subparser to use
	try:
		if args.rastid:
			repo = "MG-RAST"
	except AttributeError:
		try:
			if args.imicrobeid:
				repo = "iMicrobe"
		except AttributeError:
			repo = "SRA"

	# Download samples!
	if repo == "MG-RAST":
		for rast_proj in args.rastid:
			target_list = get_mgrast_acc_metadata(rast_proj, args.metadata, args.outdir)
			for target in target_list:
				download_mgrast_sample(target, args.retries, args.threads, args.outdir, args.force, args.list)
	elif repo == "iMicrobe":
		for imicrobe_identifier in args.imicrobeid:
			target_list = get_imicrobe_acc_metadata(imicrobe_identifier)
			for target in target_list:
				download_imicrobe_sample(target, args.retries, args.threads, args.outdir, args.force, args.list)
	else:
		for sra_identifier in args.id:
			acclist = get_sra_acc_metadata(sra_identifier, args.metadata, args.outdir, args.list, args.no_SRR_parsing)

			for acc in acclist:
				run_fasterq_dump(acc, args.retries, args.threads, args.outdir, args.force, args.fastqdump)


