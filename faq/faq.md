# grabseqs FAQ

This page provides a few, hopefully helpful, hints that go above and beyond the [README](https://github.com/louiejtaylor/grabseqs/blob/master/README.md).

Sections: [General](#general-faqs) | [SRA](#sra-faqs) | [MG-RAST](#mg-rast-faqs) | [iMicrobe](#imicrobe-faqs)

## General FAQs

 - **What if I have a file containing a list of many accessions I want to download, and don't want to type them all on the command-line?**

Let's say you have a newline-separated list of SRA accession numbers in a file called `acc.txt`. You can pass those through to grabseqs like so:
 
     grabseqs sra $(cat acc.txt)

 - **I can't install on Python version 3.X through conda**

Installation and release through conda explicitly uses Python versions 3.6 and 3.7 (as of Jan 2020). If you're using a different version of Python 3, try installing the grabseqs [requirements](https://github.com/louiejtaylor/grabseqs/blob/master/environment.yml) only via conda, then installing the grabseqs package through pip (`pip install grabseqs`) since the PyPI package is not built for a specific Python 3 minor version.

 - **The reads aren't downloading, why?**

Many possibilites here, and often they are respository-dependent. General tips: 

1) Make sure your internet connection is good (and that you have permission to download files on whatever system you're using). 

2) Try again later. Sporadic connection problems are common. 

3) Make sure the reads are available/have been released to the public. Grabseqs only accesses publically available reads, so if you can't download from the SRA/iMicrobe/MG-RAST website without logging in, neither can grabseqs.

 - **What format are reads?**

Reads are saved as gzipped FASTQ files (extension `.fastq.gz`). If the repository data is in .fasta format, dummy quality scores are added.

 - **How is the metadata formatted?**

Metadata is downloaded and stored in .csv format (to the filename specified by the `-m` flag, e.g. `-m metadata.csv`). Metadata is appended if the filename already exists (assuming the file specified is in proper .csv format). Column names in the repository metadata are maintained. We do not recommend combining metadata from different repositories--while this will work without error, we do not parse/rename columns from each repository.

 - **Can you/can I add X repository?**

Since downloading from repositories is modular, adding new repositories is hopefully simple. We provide a [template](https://github.com/louiejtaylor/grabseqs/blob/master/template.py) for adding new repositories--each new repo is essentially handled as a separate argparse subparser

 - **Who/what do I cite?**

We would appreciate you referencing our GitHub page if you find this tool useful. More importantly, be fair to and appreciative of the researchers who generate the data, and the organizations who make the data available to the public. At minimum, citation of the paper/dataset(/repository) is appropriate. It is your responsibility to abide by the guidelines of the groups/repositories who make data available. Open data faciliates collaboration--if you're not sure, ask!

[Top](#grabseqs-faq)

## SRA FAQs

 - **What default arguments do you use for calling fasterq/fastq-dump?**

We use arguments that remove technical reads, return gzipped fastq files (when available), and split paired reads into separate files (with a third file for reads without a mate). Specifically, the commands look like:

    fasterq-dump -e {thread_num} -f -3 SRR#########
    # or
    fastq-dump --gzip --split-3 --skip-technical SRR#########
    # both of these can have "-O /path/to/outdir/" optionally 
    # appended before the accession if specified by the user

For the current version of the code, see the `run_fasterq_dump` function within the [sra.py module](https://github.com/louiejtaylor/grabseqs/blob/master/grabseqslib/sra.py).

If you'd like to pass your own arguments to either of these functions, use the `--custom_fqdump_args` parameter like so:

    grabseqs sra SRP####### -r 0 --custom_fqdump_args="--split-spot --include-technical --progress"

 - **Why am I running out of space?**
 
 If you're going to be using SRA data, after you've installed sra-tools, run `vdb-config -i` and turn off local file caching unless you want extra copies of the downloaded sequences taking up space ([read more here](https://github.com/ncbi/sra-tools/wiki/Toolkit-Configuration)).

 - **My reads are not paired properly.**

Sometimes fasterq-dump filters out reads but won't also filter the mate, and I haven't figured out why, or how to circumvent it. Try adding the `--use_fastq_dump` flag--it seems that fastq-dump handles this situation better.

[Top](#grabseqs-faq)

## MG-RAST FAQs

 - **My accession can't be found by grabseqs.**

Many of the projects in MG-RAST are not publically accessible. If you're having trouble with a particular accession number or project, go to the [MG-RAST website](http://www.mg-rast.org/) and make sure you can download it by hand first. **Please do this first, as a number of samples which were previously available for download are now unavailable.** If this works fine, please [open an issue](https://github.com/louiejtaylor/grabseqs/issues) and we'll check it out!

[Top](#grabseqs-faq)

## iMicrobe FAQs

 - **My iMicrobe download isn't working.**

As with MG-RAST, many of the iMicrobe projects are not available to the public. If you're having download troubles, see whether you can download a test sample manually from [the iMicrobe website](https://www.imicrobe.us/). iMicrobe seems to have reads stored a lot of different ways. For iMicrobe, we handle reads that are either in .fastq or .fasta (adding dummy scores in .fastq conversion), either .gzipped or not, and either paired or unpaired. If you come across reads that are in another format, or you can download from the website but not through grabseqs, please [open an issue](https://github.com/louiejtaylor/grabseqs/issues) and we'll take a look.

[Top](#grabseqs-faq)
