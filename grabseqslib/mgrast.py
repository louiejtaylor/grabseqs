import requests, argparse, sys, os, time, json, glob
from subprocess import call

from grabseqslib.utils import check_existing, fetch_file, check_filetype, fasta_to_fastq

def add_mgrast_subparser(subparser):
	"""
	Function to add the MG-RAST subparser.
	"""

	parser_rast = subparser.add_parser('mgrast', help="download from MG-RAST")
	parser_rast.add_argument('rastid', type=str, nargs='+', 
				help="One or more MG-RAST project or sample identifiers (mgp####/mgm######)")

	parser_rast.add_argument('-o', dest="outdir", type=str, default="",
				help="directory in which to save output. created if it doesn't exist")
	parser_rast.add_argument('-r',dest="retries", type=int, default=0,
				help="number of times to retry download")
	parser_rast.add_argument('-t',dest="threads", type=int, default=1,
				help="threads to use (for pigz)")

	parser_rast.add_argument('-f', dest="force", action="store_true",
				help = "force re-download of files")
	parser_rast.add_argument('-l', dest="list", action="store_true",
				help="list (but do not download) samples to be grabbed")
	parser_rast.add_argument('-m', dest="metadata", action="store_true",
				help="save metadata")


def get_mgrast_acc_metadata(pacc, save = False, loc = ''):
	"""
	Function to get list of MG-RAST sample accession numbers from a particular 
	project. Takes project accession number `pacc` and returns a list of mgm
	accession numbers. Optional arguments to `save` metadata .csv in a specified
	`loc`ation.
	"""
	if pacc[:3] == "mgm":
		return [pacc]
	elif pacc[:3] != "mgp":
		raise NameError("Unknown prefix: " + pacc[:3] + ". Should be 'mgm' or 'mgp'.")
	metadata_json = json.loads(requests.get("http://api.metagenomics.anl.gov/metadata/export/"+pacc).text)
	sample_list = []
	for sample in metadata_json["samples"]:
		sample_list.append(sample["libraries"][0]["data"]["metagenome_id"]["value"]) #metadata: ["data"]
	if save:
		f = open(os.path.join(loc,pacc+".json"), 'w')
		f.write(str(metadata_json))
		f.close()
		#TODO: Save metadata detail

	return sample_list

def download_mgrast_sample(acc, retries = 0, threads = 1, loc='', force=False, list_only=False):
	"""
	Helper function to download original (uploaded) MG-RAST `acc`ession,
	with support for a particular number of `retries`. Can use multiple
	`threads` with pigz (if data are not already compressed on arrival).
	"""
	read_stages = ["050.1", "050.2"] # R1 and R2 (if paired)

	metadata_json = json.loads(requests.get("http://api.metagenomics.anl.gov/download/"+acc).text)
	stages_to_grab = []
	for stage in metadata_json["data"]:
		if stage["file_id"] in read_stages:
			stages_to_grab.append(stage["file_id"])
	stages_to_grab = sorted(stages_to_grab) # sort because json

	if len(stages_to_grab) == 0:
		raise Exception("No reads found for accession: "+acc)
	else:
		if len(stages_to_grab) == 1:
			fext = [""] # unpaired, no ext
		else:
			fext = ["_"+str(i+1) for i in range(len(stages_to_grab))] # paired
	if list_only:
		print(','.join([acc+ext+".fastq.gz" for ext in fext]))
	else:
		if not force:
			found = check_existing(loc, acc)
			if found != False:
				print("found existing file matching acc:" + acc + ", skipping download. Pass -f to force download")
				return False

		fa_paths = [os.path.join(loc,acc+ext+".fasta") for ext in fext]
		fq_paths = [os.path.join(loc,acc+ext+".fastq") for ext in fext]

		for i in range(len(fa_paths)):
			fa_path = fa_paths[i]
			fq_path = fq_paths[i]
			file_url = "http://api.metagenomics.anl.gov/download/"+acc+"?file="+stages_to_grab[i]
			retcode = fetch_file(file_url,fa_path,retries)
			ftype = check_filetype(fa_path)
			gzipped = ftype.endswith('.gz')
			if ftype.startswith("fasta"):
				print("Converting .fasta to .fastq (adding dummy quality scores), compressing")
				fasta_to_fastq(fa_path, fq_path, gzipped)
				retcode = call(["rm "+fa_path], shell=True) # get rid of old fasta
				rzip = call(["pigz -f -p "+ str(threads) + ' ' + fq_path], shell=True)
			elif ftype.startswith("fastq"):
				if gzipped:
					print("downloaded file in .fastq.gz format already!")
					call(["mv", fa_path, fq_path+".gz"])
				else:
					print("downloaded file in .fastq format already, compressing .fastq")
					call(["mv", fa_path, fq_path])
					rzip = call(["pigz -f -p "+ str(threads) + ' ' + fq_path], shell=True)
			else:
				print("requested sample "+acc+" does not appear to be in .fasta or .fastq format. This may be because it is not publically accessible from MG-RAST.")
