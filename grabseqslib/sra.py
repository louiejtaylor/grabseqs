import requests, argparse, sys, os, time, glob
from subprocess import call

def add_sra_subparser(subparser):
	"""
	Function to add subparser for SRA data.
	"""
	parser_sra = subparser.add_parser('sra', help="download from SRA")
	parser_sra.add_argument('id', type=str, nargs='+', 
				help="One or more BioProject, ERR/SRR or ERP/SRP number(s)")

	parser_sra.add_argument('-o', dest="outdir", type=str, default="",
				help="directory in which to save output. created if it doesn't exist")
	parser_sra.add_argument('-r',dest="retries", type=int, default=2,
				help="number of times to retry download")
	parser_sra.add_argument('-t',dest="threads", type=int, default=1,
				help="threads to use (for fasterq-dump/pigz)")

	parser_sra.add_argument('-f', dest="force", action="store_true",
				help = "force re-download of files")
	parser_sra.add_argument('-l', dest="list", action="store_true",
				help="list (but do not download) samples to be grabbed")
	parser_sra.add_argument('-m', dest="metadata", action="store_true",
				help="save SRA metadata")
	parser_sra.add_argument('--no_parsing', dest="no_SRR_parsing", action="store_true",
				help="do not parse SRR/ERR (pass straight to fasterq-dump)")
	parser_sra.add_argument("--use_fastq_dump", dest="fastqdump", action="store_true",
				help="use legacy fastq-dump instead of fasterq-dump (no multithreaded downloading)")


def get_sra_acc_metadata(pacc, save = False, loc = '', list_only = False, no_SRR_parsing = False):
	"""
	Function to get list of SRA accession numbers from a particular project.
	Takes project accession number `pacc` and returns a list of SRA 
	accession numbers. Optional arguments to `save` metadata .csv in a specified
	`loc`ation.
	Originally featured in: https://github.com/louiejtaylor/hisss
	"""
	pacc = pacc.strip()
	metadata = requests.get("http://trace.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?save=efetch&db=sra&rettype=runinfo&term="+pacc)
	if save:
		f = open(os.path.join(loc,pacc+".tsv"), 'w')
		f.write(metadata.text)
		f.close()
	lines = [l.split(',') for l in metadata.text.split("\n")]
	try:
		run_col = lines[0].index("Run")
	except IndexError:
		raise IndexError("Could not find samples for accession: "+pacc+". If this accession number is valid, try re-running.")
	run_list = [l[run_col] for l in lines[1:] if len(l[run_col]) > 0]
	if list_only:
		layout_col = lines[0].index("LibraryLayout")
		layout_list = [l[layout_col] for l in lines[1:] if len(l[run_col]) > 0]
		for i in range(len(layout_list)):
			if layout_list[i] == "SINGLE":
				print(run_list[i]+".fastq.gz")
			elif layout_list[i] == "PAIRED":
				print(run_list[i]+"_1.fastq.gz,"+run_list[i]+"_2.fastq.gz")
			else:
				raise Exception("Unknown library layout: "+layout_list[i])
		return []
	else:
		if no_SRR_parsing:
			if pacc.startswith('SRR') or pacc.startswith('ERR'):
				return [pacc]
		return run_list

def run_fasterq_dump(acc, retries = 2, threads = 1, loc='', force=False, fastqdump=False):
	"""
	Helper function to run fast(er)q-dump to grab a particular `acc`ession,
	with support for a particular number of `retries`. Can use multiple
	`threads`.
	"""
	skip = False
	retcode = 1
	while retries >= 0:
		if not force:
			if loc == '':
				loc_to_search = os.getcwd()
			else:
				loc_to_search = loc
			try:
				existing = [f for f in os.listdir(loc_to_search) if f.endswith('fastq.gz')]
			except FileNotFoundError:
				existing = []
			for f in existing:
				if (acc + '.' in f) or (acc + '_' in f):
					print("found file: " + f + "  matching " + acc + ", skipping download. Pass -f to force download")
					skip = True
					break
		if not skip:
			if fastqdump:
				print("downloading " + acc + " using fastq-dump")
				cmd = ["fastq-dump", "--gzip", "--split-3", "--skip-technical"]
			else:
				print("downloading " + acc + " using fasterq-dump")
				cmd = ["fasterq-dump", "-e", str(threads), "-f", "-3"]
			if loc != "":
				cmd = cmd + ['-O', loc]	
			cmd = cmd + [acc]
			retcode = call(cmd)
			rgzip = 0
			if retcode == 0:
				if not fastqdump:
					rgzip = call(["pigz -f -p "+ str(threads) + ' ' + os.path.join(loc,acc+'*'+'fastq')], shell=True)
				if rgzip == 0: #pigz exit code is zero even if file not found -_-
					if len(glob.glob(os.path.join(loc,acc+'*'+'fastq.gz'))) > 0:
						break

			# only here if downloading and zipping failed
			print("SRA download for acc "+acc+" failed, retrying "+str(retries)+" more times.")
			if retries > 0:
				time.sleep(100) #TODO?: user-modifiable
				retries -= 1
			else:
				raise Exception("download for "+acc+" failed. fasterq-dump returned "+str(retcode)+", pigz returned "+str(rgzip)+".")
		else:
			break
