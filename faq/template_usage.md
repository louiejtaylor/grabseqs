# Adding support for new modules

We provide a [Python template](https://github.com/louiejtaylor/grabseqs/blob/master/template.py) 
to facilitate adding support for new repositories, and welcome pull requests! This page walks
through the process of building out that template for a hypothetical new repository, `newrepo`.

## Background

### Grabseqs anatomy

The grabseqs functionality is contained within a package called `grabseqslib`, to disambiguate
between the command-line tool and the package providing the functionality. `grabseqslib` includes
multiple modules: one per repository (e.g. `sra` and `mgrast`), as well as a `utils` module 
containing general functions used by each module. Finally, `__init__.py` creates the base argument
parser and passes command-line arguments to be processed by repository-specific logic.

New repositories will likely be comprised of an additional module (e.g. `newrepo.py`), as well as
a few lines of logic in `__init__.py` to handle argument parsing.

### Repository structure

Generally, grabseqs is built on the assumption that repositories contain "projects", consisting of
one or more "samples". This assumption has held thus far from both a data generation perspective 
(usually in a study you sequence a number of samples related to a research question) and is also 
useful from a data re-use perspective (you'd often like to reanalyze all or a subset of the samples
from a given study). Simple data re-use was the core motivation for developing grabseqs.
This relationship is often reflected in the accession numbers for samples/projects, and can be
exploited in automating sample access--for example, MG-RAST project IDs are prefixed by "mgp", 
whereas sample (metagenome) names are prefixed by "mgm".

Repository metadata is also an important point to consider. Is there programmatically-acessible
metadata? If so, is it available on the project-level, sample-level, or both? For example, when
accessing data from NCBI's SRA, you can request detailed, sample-level metadata from the API
given only a project accession number, which greatly simplifies metadata processing. For MG-RAST
and iMicrobe, on the other hand, APIs map project information to sample numbers, which then must
be queried individually for sample-level metadata.

## Adding support for `newrepo`

Now, we'll walk step-by-step through adding support for a new repository, `newrepo`, to grabseqs.
The end goal is to be able to run the following command:

    grabseqs newrepo samp1234 proj123

Where "samp1234" is an example sample accession to be downloaded, and "proj123" is an example 
project accession number.

If you'd like to eventually make a pull request back into this repository, we recommend making a fork
of this repository to work with. Either way, you'll likely want a local copy to work with, so clone away!

### Step 1: Make a new module

We recommend starting with a copy of [`template.py`](https://github.com/louiejtaylor/grabseqs/blob/master/template.py),
as it lays out the structure used in all the other grabseqs modules. Make a copy of this file in the
`grabseqslib` directory, with a name that makes sense--for our example we'll call it `newrepo.py`.

This template module contains four functions. We'll name them after `newrepo`, so they are:

 - `add_newrepo_subparser`: adds an argparse subparser for handling arguments to the grabseqs
command-line tool for your repo
 - `process_newrepo`: controller function for handling input project/sample accession numbers
 - `map_newrepo_project_acc`: function to map project accession numbers to sample accession numbers
for downloading
 - `download_newrepo_sample`: function to handle downloading of reads given a sample accession number

These functions handle 99% of the work for newrepo downloads, and we'll walk through filling them out
one-by-one.

### Step 2: Add the `newrepo` subparser

The `add_newrepo_subparser` function is likely mostly done for you in the template. There are a number of 
options that you'll likely use for any repository (e.g. specifying an output directory, number of retries,
forcing re-download of already-existing files, multithreading, and listing/dry-running \[rather than 
downloading\] samples matching a particular query). These options are pre-specified for you and shouldn't
be tweaked much for consistency with other repository subparsers. If metadata is not programmatically 
available from `newrepo`, remove the `-m` option.

If you'd like to include additional functions above and beyond these default options, you may add them to 
the argparser object within this function. See the `sra.py` file for examples of other options--there are
a variety of options for the `grabseqs sra` subparser above and beyond the default options.

You may have noticed that this function isn't quite hooked up to the main argparse instance yet. That's okay;
we'll do this at the end when we edit `__init__.py`.

### Step 3: Add the controller logic

From here on out, it's a good idea to have a good handle on the questions addressed in the "Repository 
structure" section above. Important questions include:

 - How can I programmatically access data, metadata, and map project accession numbers to sample accession 
 numbers? E.g. is there an API endpoint (used in MG-RAST, iMicrobe metadata/downloads/mapping and 
 SRA metadata/mapping) or a tool to aid in downloading (used in SRA downloads)?
 - Is metadata available? If so, is sample-level metadata accessible from a project accession number
 (easiest)?
 
The answers to these questions determine how the `process_newrepo` controller function will be structured.
The example in `template.py` assumes that metadata is available, and that sample-level metadata is present
in the project-sample mapping step. Thus, the controller generally functions like so:

    # begin looping through accession numbers passed by user
    for newrepo_identifier in args.newrepoid:
        
        # for each project identifier, map it to sample identifiers and grab metadata (a pandas dataframe)
        sample_list, metadata_agg = map_newrepo_project_acc(newrepo_identifier, metadata_agg)
        
        # for each sample mapped to by the passed project identifier
        for sample in sample_list:
            
            # download that sample
            download_newrepo_sample(acc,
                                    args.retries,
                                    args.threads,
                                    args.outdir,
                                    args.force,
                                    args.list)
 
Actual metadata saving is handled in a repository-agnostic fashion--the `process_newrepo` function will
return the pandas dataframe containing metadata, which will then be saved in a safe/non-clobber-y way
(with no additional effort necessary on your part).
 
Now, let's go write the actual mapping logic.
 
### Step 4: Map project accessions to sample accessions

The `map_newrepo_project_acc` maps project to sample accession numbers, returning a list of sample accession
numbers. Depending on metadata availability, you may also access sample metadata in this mapping step, and
it seems prudent to only make one API call when necessary, so we've written the example using this slightly
more complicated workflow--this is also used in the SRA and MG-RAST modules.

Generally, you can pass one or more project or sample accessions to grabseqs. Depending on from where metadata is 
obtained, you'll either want to avoid `map_newrepo_project_acc` altogether if a sample accession number is
passed; or grab metadata and return a singleton list (containing the sample accession number) and metadata to your
controller function. An example of using the pandas.DataFrame.append() method to concatenate multiple metadata
tables is included in this function in the template file.

The code here is dependent on the format of the project-sample map. SRA provides mapping information in csv format;
the MG-RAST API returns JSON maps--feel free to use that code for inspiration. Your workflow might look something like
this (based on the MG-RAST JSON workflow and using the `json` and `requests` libraries), where `pacc` is the 
accession number:

    # initialize vars
    sample_list = []
    metadata_df = pd.DataFrame()
    
    # hit api
    metadata_json = json.loads(requests.get("http://api.newrepo.gov/metadata/export/"+str(pacc)).text)
    
    for sample in metadata_json["samples"]:
        sample_list.append(sample["value"])
        # additional logic to add metadata lines to metadata_df

If the user would like to list \[but not download\] the available samples (-l) and information on read paired-ness
is available here, i.e. from a metadata table, this can be tested for here (and then return an empty 
`sample_list` to prevent downstream downloading). For an example of this workflow, see the `sra.py` module.

### Step 5: Download samples!

A bit of of boilerplate is included already, handling the `-f` (force) option:

    # Make sure to check that the sample isn't already downloaded
    if not force:
        # using check_existing from utils.py
        found = check_existing(loc, acc)
        if found != False:
            print("found existing file matching acc:" + acc + ", skipping download. Pass -f to force download")
            return False

You can build the expected paths for the eventual downloaded reads like so:

    paired = True
    # using build_paths from utils.py
    file_paths = build_paths(acc, loc, paired)

Generally, unless there's a tool like NCBI's fasterq-dump that downloads both reads in one command, it's 
just easier to iterate through file paths (i.e. either one unpaired, or two paired). 

If the file is directly available from an API URL, the `fetch_file` function from `grabseqs.utils` should serve 
you well (it uses `wget`, a grabseqs dependency):

    seq_urls = ["http://api.newrepo.gov/data/"+str(acc)+"_R1.fastq",
                "http://api.newrepo.gov/data/"+str(acc)+"_R2.fastq"]
    
    for i in range(len(seq_urls)):
    
        print("Downloading accession "+acc+" from newrepo")
        
        # fetch_file should work for most things where a URL is available
        retcode = fetch_file(seq_urls[i],file_paths[i],retries)

        # There are a number of things you may want to do here: check and handle
        # downloaded file integrity, convert to .fastq (see mgrast.py for an example
        # of a scenario dealing with .fastx in general), etc.

        print("Compressing .fastq")
        gzip_files(file_paths, zip_func, threads)

If metadata is only available on a sample-wise basis, you may want to do metadata handling in this function
as well, or in a separate function if two API calls are necessary. See `mgrast.py` for an example of metadata
handling at the sample level. If 

Regarding sample listing/dry-running (-l)--if the information about whether samples are paired or unpaired is 
only available from a sample-specific source, it usually makes more sense to look that up here, and then just 
skip the downloading part. For an example of this workflow, see the `mgrast.py` module.

Now we've written all the logic for argument parsing, metadata wrangling, project-sample accession mapping, and
raw data downloading! We just have to hook it all together to the main grabseqs program.

### Step 6: Hooking up subparser and controller functions

Here, you need to edit `__init__.py`. This should be fairly self explanatory based on what's already 
present for the other submodules, but you'll need to add the following:

 - Import your new functions:
```{python}
from grabseqslib.sra import process_sra, add_sra_subparser
from grabseqslib.imicrobe import process_imicrobe, add_imicrobe_subparser
from grabseqslib.mgrast import process_mgrast, add_mgrast_subparser
from grabseqslib.newrepo import process_newrepo, add_newrepo_subparser
```
 - Add your new subparser:
```{python}
add_sra_subparser(subpa)
add_imicrobe_subparser(subpa)
add_mgrast_subparser(subpa)
add_mgrast_subparser(subpa)
```
 - Check to see if the user called your subparser:
```{python}
try:
    if args.newrepoid:
        repo = "newrepo"
```
 - Finally, add a case for your controller function:
```{python}
if repo == "SRA":
    metadata_agg = process_sra(args, zip_func)
elif repo == "MG-RAST":
    metadata_agg = process_mgrast(args, zip_func)
elif repo == "iMicrobe":
    metadata_agg = process_imicrobe(args, zip_func)
elif repo == "newrepo":
    metadata_agg = process_newrepo(args, zip_func)
```

## What next?

So, you've added a new repository--that's awesome (and thank you!!)! Feel free to open a pull request. We 
run grabseqs through a rigorous set of automated tests on every commit/weekly, so please write a new test 
or three testing data/metadata downloading, or any edge cases that you encounter that other users/developers
might not know about.
