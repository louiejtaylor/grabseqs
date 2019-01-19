import os, glob
from subprocess import call

def check_existing(save_loc, acc):
	"""
	Function to check for single- or paired-end reads
	in a given `save_loc` for a particular `acc`ession.
	Returns "paired" if paired reads found, "single" if
	unpaired reads found, "both" if single- and paired-
	end reads found, and False if nothing matching that 
	accession was found.
	"""
	if save_loc == '':
		loc_to_search = os.getcwd()
	else:
		loc_to_search = save_loc
	try:
		existing = [f for f in os.listdir(loc_to_search) if f.endswith('fastq.gz')]
	except FileNotFoundError:
		return False
	paired = False
	unpaired = False
	for f in existing:
		if acc + '.fastq.gz' in f:
			unpaired = True
		if (acc + '_1.fastq.gz' in f) or (acc + '_2.fastq.gz' in f):
			paired = True
	if unpaired == True and paired == True:
		return "both"
	elif paired == True:
		return "paired"
	elif unpaired == True:
		return "unpaired"
	else:
		return False

def fetch_file(url, outfile, retries = 0):
	"""
	Function to fetch a remote file from a `url`,
	writing to `outfile` with a particular number of
	`retries`.
	"""
	wget_cmd = ["wget", "-O", outfile, url]
	retcode = call(wget_cmd)
	return retcode

def build_paths(acc, loc, paired, ext = ".fastq"):
	"""
	Builds paths for saving downloaded files from a given
	`acc` in a particular `loc`, depending on whether or
	not they are `paired`. Can specify any `ext`. Returns
	a list of paths of length 1 or 2.
	"""
	if paired:
		suffix = ["_1", "_2"]
	else:

		suffix = [""]
	return [os.path.join(loc,acc+s+ext) for s in suffix]
	
