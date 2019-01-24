import requests, argparse, sys, os, time, json, glob, re
from subprocess import call
from requests_html import HTMLSession

from grabseqslib.utils import check_existing, fetch_file

def add_imicrobe_subparser(subparser):
	"""
	Function to add a subparser for the iMicrobe repository.
	"""

	### Base args: should be in every parser
	parser_imicrobe = subparser.add_parser('imicrobe', help="download from iMicrobe")

	parser_imicrobe.add_argument('imicrobeid', type=str, nargs='+', 
				help="One or more iMicrobe project or sample identifiers (p##/s###)")

	parser_imicrobe.add_argument('-o', dest="outdir", type=str, default="",
				help="directory in which to save output. created if it doesn't exist")
	parser_imicrobe.add_argument('-r',dest="retries", type=int, default=0,
				help="number of times to retry download")
	parser_imicrobe.add_argument('-t',dest="threads", type=int, default=1,
				help="threads to use (for pigz)")

	parser_imicrobe.add_argument('-f', dest="force", action="store_true",
				help = "force re-download of files")
	parser_imicrobe.add_argument('-l', dest="list", action="store_true",
				help="list (but do not download) samples to be grabbed")

	### OPTIONAL: Use if metadata are available
	parser_imicrobe.add_argument('-m', dest="metadata", action="store_true",
				help="save metadata")


def get_imicrobe_acc_metadata(pacc):
	"""
	Function to get list of iMicrobe sample accession numbers from a particular
	project. Takes project accession number `pacc` and returns a list of iMicrobe
	accession numbers.
	"""

	# Check accession format
	pacc = pacc.lower()
	if pacc.startswith("p"):
		pacc = pacc[1:]
	elif pacc.startswith("s"):
		return [pacc]
	else:
		raise(Exception("iMicrobe accession numbers should be prefixed with 'p' (project) or 's' (sample)"))

	# Grab sample info
	session = HTMLSession()
	r = session.get('https://www.imicrobe.us/#/projects/'+pacc)
	r.html.render(sleep = 1)

	sample_list = []
	for l in r.html.element("a"):
		i = l.items()
		try:
			if i[0][1].startswith("#/samples/"):
				sample_list.append(i[0][1][10:]) # add sample ID only
		except IndexError:
			continue
	session.close()

	# Format and return sample accession numbers
	return ["s"+ sID for sID in sample_list]

def download_imicrobe_sample(acc, retries = 0, threads = 1, loc='', force=False, list_only=False):
	"""
	Helper function to download sequences given an iMicrobe `acc`ession,
	with support for a particular number of `retries`. Can use multiple
	`threads` with pigz (if data are not already compressed on arrival).
	"""

	# LISTING OPTION 2: If the information about whether samples are paired or
	# unpaired is only available from a sample-specific page, it usually makes more
	# sense to look that up here, and then just skip the downloading part. For an
	# example of this, see the mg-rast.py module
	if not acc.startswith("s"):
		raise Exception("iMicrobe sample accession numbers should be prefixed with 's'")

	download_paths = _parse_imicrobe_readpath(acc[1:]) # get paths
	d_n = len(download_paths.keys())
	if d_n == 1:
		fext = [""]
	elif d_n == 2:
		fext = ["_1", "_2"]
	elif d_n == 0:
		raise Exception("No reads found for sample #: "+acc+". Check https://www.imicrobe.us/#/samples/"+acc[1:]+" to confirm that it exists, and open an issue if existing reads were not found.")
	else:
		raise Exception("More than two read files found for "+acc+"--not sure what to do with "+str(d_n) +" reads.")
	if list_only:
		print(','.join([acc+ext+".fastq.gz" for ext in fext]))
		return False

	# Make sure to check that the sample isn't already downloaded
	if not force:
		found = check_existing(loc, acc)
		if found != False:
			print("found existing file matching acc:" + acc + ", skipping download. Pass -f to force download")
			return False

	# Need to know this
	paired = True

	# Generally, unless there's a tool like fasterq-dump that downloads both reads,
	# it's just easier to iterate through file paths (i.e. either one unpaired, or
	# two paired).
	seq_urls = []
	file_paths = build_paths(acc, loc, paired) #see utils.py for details

	for i in range(len(seq_urls)):
		print("Downloading sample "+acc+" from iMicrobe")
		# fetch_file should work for most things where a URL is available
		#retcode = fetch_file(seq_urls[i],file_paths[i],retries)

		# There are a number of things you may want to do here: check and handle
		# downloaded file integrity, convert to .fastq (see mgrast.py for an example
		# of a scenario dealing with .fastx in general), retries, etc.

		print("Compressing .fastq")
		#rzip = call(["pigz -f -p "+ str(threads) + ' ' + file_paths[i]], shell=True)

	return True

def _parse_imicrobe_readpath(acc):
	"""
	Helper function to parse sample download paths from a sample page.
	Takes an `acc` with no prefix. Returns a dictionary with download paths
	for one or two reads like: {1:"url"} or {1:"url1", 2:"url2"}.
	"""
	acc = str(acc)
	session = HTMLSession()
	r = session.get('https://www.imicrobe.us/#/samples/'+acc)
	r.html.render(scrolldown=2, sleep=3)
	file_links = list(r.html.links)
	# Find one or two links immediately followed by "Reads column (or equivalent)
	reads_colnames = ["Reads","Reads FASTQ", "upload.fastq"]
	
	for c in reads_colnames:
		hits = [m.start() for m in re.finditer("<td>"+c+"</td>", r.html.html)]
		if len(hits) > 0:
			break
	link_indices = [r.html.html.index('"'+l+'"') for l in file_links]
	read_links = {}
	for j in range(len(hits)):
		read_links[j+1] = file_links[_closest_below_index(link_indices, hits[j])]

	return read_links

def _closest_below_index(l,n):
	"""
	Helper function. Returns index of closest number in `l`
	to `n`, without going over.
	"""
	best = -1
	best_i = -1
	for i in range(len(l)):
		if l[i] < n:
			if n - l[i] < n - best:
				best_i = i
				best = l[i]
	return best_i
