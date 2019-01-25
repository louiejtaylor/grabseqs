import os, glob, gzip
from subprocess import call
from requests_html import HTMLSession

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

def check_filetype(fp):
	"""
	Function to classify downloaded files as gzipped or not,
	and in FASTQ, FASTA, or not based on contents. Returns a 
	formatted extension (i.e. '.fastq', 'fasta.gz') corresponding
	to the filetype or an empty string if the filetype is not 
	recognized.
	"""
	try:
		f = gzip.open(fp)
		first_b = f.readline()
		gz = ".gz"
		first = first_b.decode("ascii")
	except OSError: # file not gzipped
		f.close()
		f = open(fp, 'r')
		first = f.readline()
		f.close()
		gz = ""
	if len(first) == 0:
		return ""
	if first[0] == ">":
		return "fasta"+gz
	elif first[0] == "@":
		return "fastq"+gz
	else:
		return ""

def fasta_to_fastq(fp_fa, fp_fq, zipped, dummy_char = "I"):
	"""
	Function to convert fasta (at `fp_fa`) to fastq (at `fp_fq`)
	possibly zipped, adding a `dummy_score`.
	"""
	if len(dummy_char) != 1:
		raise Exception("FASTQ dummy quality char must be only one char.")

	fq = open(fp_fq, 'w')

	seq = -1
	if zipped:
		f = gzip(fp_fa)
	else:
		f = open(fp_fa)
	for line in f.readlines():
		if line[0] == '>':
			if seq == -1:
				fq.write('@'+line[1:])
			else:
				fq.write(seq+'\n')
				fq.write('+\n')	
				fq.write(dummy_char*len(seq)+'\n')
				fq.write('@'+line[1:])
			seq = ''
		else:
			seq += line.strip()

	f.close()

	if len(seq) > 0:
		fq.write(seq+'\n')
		fq.write('+\n')
		fq.write(dummy_char*len(seq)+'\n')

	fq.close()

