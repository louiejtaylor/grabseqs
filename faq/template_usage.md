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
forcing re-download of already-existing files, multithreading, and listing [rather than downloading] samples
matching a particular query). These options are pre-specified for you and shouldn't be tweaked much for 
consistency with other repository subparsers. If metadata is not programmatically available from `newrepo`,
remove the `-m` option.

If you'd like to include additional functions above and beyond these default options, you may add them to 
the argparser object within this function. See the `sra.py` file for examples of other options--there are
a variety of options for the `grabseqs sra` subparser above and beyond the default options.

You may have noticed that this function isn't quite hooked up to the main argparse instance yet. That's okay;
we'll do this at the end when we edit `__init__.py`.

