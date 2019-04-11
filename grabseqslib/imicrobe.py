import requests, argparse, sys, os, time, json, glob, re
import pandas as pd
from io import StringIO
from subprocess import call
from requests_html import HTMLSession
from grabseqslib.utils import check_existing, fetch_file, build_paths, check_filetype, fasta_to_fastq

def add_imicrobe_subparser(subparser):
	"""
	Function to add a subparser for the iMicrobe repository.
	"""

	### Base args: should be in every parser
	parser_imicrobe = subparser.add_parser('imicrobe', help="download from iMicrobe")

	parser_imicrobe.add_argument('imicrobeid', type=str, nargs='+', 
				help="One or more iMicrobe project or sample identifiers (p##/s###)")

	parser_imicrobe.add_argument('-m', dest="metadata", type=str, default="",
				help="filename in which to save metadata (.csv format, relative to OUTDIR)")
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

def download_imicrobe_sample(acc, retries = 0, threads = 1, loc='', force=False, list_only=False, download_metadata=False, metadata_agg = None):
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

	download_paths, metadata_agg = _parse_imicrobe_readpath_metadata(acc[1:], download_metadata, metadata_agg) # get paths and metadata
	d_n = len(download_paths.keys())
	if d_n == 1:
		fext = [""]
		paired = False
	elif d_n == 2:
		fext = ["_1", "_2"]
		paired = True
	elif d_n == 0:
		raise Exception("No reads found for sample #: "+acc+". Check https://www.imicrobe.us/#/samples/"+acc[1:]+" to confirm that it exists, and open an issue on the grabseqs repo (github.com/louiejtaylor/grabseqs/issues) if existing reads were not found.")
	else:
		raise Exception("More than two read files found for "+acc+"--not sure what to do with "+str(d_n) +" reads.")
	if list_only:
		print(','.join([acc+ext+".fastq.gz" for ext in fext]))
		return metadata_agg

	# Generally, unless there's a tool like fasterq-dump that downloads both reads,
	# it's just easier to iterate through file paths (i.e. either one unpaired, or
	# two paired).

	fx_paths = build_paths(acc, loc, paired, ".fastx")
	fq_paths = build_paths(acc, loc, paired)

	# Make sure to check that the sample isn't already downloaded
	if not force:
		found = check_existing(loc, acc)
		if found != False:
			print("found existing file matching acc:" + acc + ", skipping download. Pass -f to force download")
			return metadata_agg

	for i in list(sorted(download_paths.keys())):
		print("Downloading sample "+acc+" from iMicrobe")
		# fetch_file should work for most things where a URL is available
		fx_path = fx_paths[i-1]
		fq_path = fq_paths[i-1]
		retcode = fetch_file(download_paths[i],fx_path,retries)

		# There are a number of things you may want to do here: check and handle
		# downloaded file integrity, convert to .fastq (see mgrast.py for an example
		# of a scenario dealing with .fastx in general), retries, etc.
		ftype = check_filetype(fx_path)
		gzipped = ftype.endswith('.gz')

		if ftype.startswith("fasta"):
			print("Converting .fasta to .fastq (adding dummy quality scores), compressing")
			fasta_to_fastq(fx_path, fq_path, gzipped)
			retcode = call(["rm "+fx_path], shell=True) # get rid of old fasta
			rzip = call(["pigz -f -p "+ str(threads) + ' ' + fq_path], shell=True)
		elif ftype.startswith("fastq"):
			if gzipped:
				print("downloaded file in .fastq.gz format already!")
				call(["mv", fx_path, fq_path+".gz"])
			else:
				print("downloaded file in .fastq format already, compressing .fastq")
				call(["mv", fx_path, fq_path])
				rzip = call(["pigz -f -p "+ str(threads) + ' ' + fq_path], shell=True)
		else:
			print("requested sample "+acc+" does not appear to be in .fasta or .fastq format.")
	return metadata_agg

def _parse_imicrobe_readpath_metadata(acc, download_metadata, metadata_agg):
	"""
	Helper function to parse sample download paths from a sample page.
	Takes an `acc` with no prefix. Returns a dictionary with download paths
	for one or two reads like: {1:"url"} or {1:"url1", 2:"url2"}. Also returns
	aggregated metadata.
	"""
	acc = str(acc)
	session = HTMLSession()
	r = session.get('https://www.imicrobe.us/#/samples/'+acc)
	r.html.render(scrolldown=4, sleep=4)
	file_links = list(r.html.links)
	# Find one or two links immediately followed by "Reads column (or equivalent)
	reads_colnames = ["Reads FASTQ", "Reads", "FASTQ", "upload.fastq"]

	for c in reads_colnames:
		hits = [m.start() for m in re.finditer("<td>"+c+"</td>", r.html.html)]
		if len(hits) > 0:
			break
	link_indices = []
	working_file_links = []
	for l in file_links:
		try:
			link_indices.append(r.html.html.index('"'+l+'"'))
			working_file_links.append(l)
		except ValueError: # sometimes they are formatted differently (if added by the project owner?)
			continue
	read_links = {}
	for j in range(len(hits)):
		read_links[j+1] = working_file_links[_closest_below_index(link_indices, hits[j])].replace("http://datacommons.cyverse.org/browse", "https://de.cyverse.org/anon-files")

	if download_metadata:
		html_str = str(r.html.html)
		relevant_section = html_str[html_str.index("<h2>Attributes"):html_str.index("<h2>Files")]
		table_only = relevant_section[relevant_section.index("<tbody>")+7:relevant_section.index("</tbody>")].replace(',',';')
		formatted_table = table_only.replace('</tr><tr>', '\n').replace('</td><td>', ',').replace('<tr>','').replace('<td>','').replace('</tr>','').replace('</td>','')
		listed_table = [z.split(',') for z in formatted_table.split('\n')]
		transposed_table =[[z[0] for z in listed_table],[z[1] for z in listed_table]]
		formatted_table = ','.join(transposed_table[0]) + '\n' + ','.join(transposed_table[1])
		if type(metadata_agg) == type(None):
			metadata_agg = pd.read_csv(StringIO(formatted_table))
		else:
			metadata_agg = metadata_agg.append(pd.read_csv(StringIO(formatted_table)),sort=True)
	return read_links, metadata_agg

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
