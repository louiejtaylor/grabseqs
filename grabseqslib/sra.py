import requests, time, shutil, sys
import pandas as pd
from io import StringIO
from subprocess import call
from grabseqslib.utils import check_existing, build_paths, gzip_files

def process_sra(args, zip_func):
    """
    High-level logic for SRA download processing. Takes
    `args` from grabseqslib argument parser and `zip_func`
    """
    # check deps
    dep_list = ["fastq-dump", "fasterq-dump"]
    deps_have = [shutil.which(dep) for dep in dep_list]
    if (not deps_have[0]) and (not deps_have[1]): # no sra-tools
        print("Neither fastq-dump nor fasterq-dump found; one is required. Please install sra-tools")
        sys.exit(1)
    elif not deps_have[1]:
        use_fastq_dump = True
    else:
        use_fastq_dump = args.fastqdump

    metadata_agg = None

    for sra_identifier in args.id:
        # get targets and metadata
        acclist, metadata_agg = get_sra_acc_metadata(sra_identifier,
                                                     args.outdir,
                                                     args.list,
                                                     not args.SRR_parsing,
                                                     metadata_agg)
        for acc in acclist:
            # get samples
            run_fasterq_dump(acc,
                             args.retries,
                             args.threads,
                             args.outdir,
                             args.force,
                             use_fastq_dump,
                             args.custom_fqd_args,
                             zip_func)

    return metadata_agg


def add_sra_subparser(subparser):
    """
    Function to add subparser for SRA data.
    """
    # Parser
    parser_sra = subparser.add_parser('sra', help="download from SRA")
    parser_sra.add_argument('id', type=str, nargs='+', 
                help="One or more BioProject, ERR/SRR or ERP/SRP number(s)")

    # Options
    parser_sra.add_argument('-m', dest="metadata", type=str, default="",
                help="filename in which to save SRA metadata (.csv format, relative to OUTDIR)")
    parser_sra.add_argument('-o', dest="outdir", type=str, default="",
                help="directory in which to save output. created if it doesn't exist")
    parser_sra.add_argument('-r',dest="retries", type=int, default=2,
                help="number of times to retry download")
    parser_sra.add_argument('-t',dest="threads", type=int, default=1,
                help="threads to use (for fasterq-dump/pigz)")

    # General flags
    parser_sra.add_argument('-f', dest="force", action="store_true",
                help = "force re-download of files")
    parser_sra.add_argument('-l', dest="list", action="store_true",
                help="list (but do not download) samples to be grabbed")

    # SRA-specific flags
    parser_sra.add_argument('--parse_run_ids', dest="SRR_parsing", action="store_true", 
                                help="parse SRR/ERR identifers (do not pass straight to fasterq-dump)")
    parser_sra.add_argument("--use_fastq_dump", dest="fastqdump", action="store_true",
                help="use legacy fastq-dump instead of fasterq-dump (no multithreaded downloading)")
    parser_sra.add_argument("--custom_fqdump_args", dest="custom_fqd_args", type=str, default="",
                help="'string' containing args to pass to fast(er)q-dump")

    # LEGACY: this will be removed in the next major version as this is now default.
    parser_sra.add_argument('--no_parsing', dest="no_SRR_parsing", action="store_true", 
                help="Legacy option to not parse SRR IDs (now default)")


def get_sra_acc_metadata(pacc, loc = '', list_only = False, no_SRR_parsing = True, metadata_agg = None):
    """
    Function to get list of SRA accession numbers from a particular project.
    Takes project accession number `pacc` and returns a list of SRA 
    accession numbers. Optional arguments to `save` metadata .csv in a specified
    `loc`ation.
    Originally featured in: https://github.com/louiejtaylor/hisss
    """
    # Grab metadata for given accession number    
    pacc = pacc.strip()
    metadata = requests.get("http://trace.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?save=efetch&db=sra&rettype=runinfo&term="+pacc)    
    lines = [l.split(',') for l in metadata.text.split("\n")]
    try:
        run_col = lines[0].index("Run")
    except IndexError: # "Run" column always present unless search failed
        raise IndexError("Could not find samples for accession: "+pacc+". If this accession number is valid, try re-running.")

    # Generate list of runs to download
    run_list = [l[run_col] for l in lines[1:] if len(l[run_col]) > 0]

    # Aggregate metadata if multiple samples/projects are being asked for
    if type(metadata_agg) == type(None):
        metadata_agg = pd.read_csv(StringIO(metadata.text))
    else:
        metadata_agg = metadata_agg.append(pd.read_csv(StringIO(metadata.text)),sort=True)

    if list_only: 
        # Do not download but read metadata and say what will be downloaded
        layout_col = lines[0].index("LibraryLayout")
        if no_SRR_parsing and (pacc.startswith('SRR') or pacc.startswith('ERR')):
            layout_list = [l[layout_col] for l in lines[1:] if len(l[run_col]) > 0 and l[run_col] == pacc]
            run_list = [pacc]
        else:
            layout_list = [l[layout_col] for l in lines[1:] if len(l[run_col]) > 0]
            
        # Print filenames that should come down (assuming the repo metadata is correct)
        for i in range(len(layout_list)):
            if layout_list[i] == "SINGLE":
                print(run_list[i]+".fastq.gz")
            elif layout_list[i] == "PAIRED":
                print(run_list[i]+"_1.fastq.gz,"+run_list[i]+"_2.fastq.gz")
            else:
                raise Exception("Unknown library layout: "+layout_list[i])
                
        # If we're here, we're listing and not downloading. So we don't return any accessions to download 
        # (empty list), but the user may still want the aggregated metadata
        return [], metadata_agg
    else:
        if no_SRR_parsing: # default, if given a Run return a Run
            if pacc.startswith('SRR') or pacc.startswith('ERR'):
                return [pacc], metadata_agg
        # otherwise, return all the Run accessions associated with whatever identifier was passed.
        return run_list, metadata_agg

def run_fasterq_dump(acc, retries = 2, threads = 1, loc='', force=False, fastqdump=False, custom_args="", zip_func="gzip"):
    """
    Helper function to run fast(er)q-dump to grab a particular `acc`ession,
    with support for a particular number of `retries`. Can use multiple
    `threads`.
    """
    skip = False
    retcode = 1
    while retries >= 0:
        if not force:
            found = check_existing(loc, acc)
            if found != False:
                print("found existing file matching acc:" + acc + ", skipping download. Pass -f to force download")
                skip = True
                break
        if not skip:
            if len(custom_args) == 0:
                if fastqdump: # use legacy fastq-dump
                    cmd = ["fastq-dump", "--gzip", "--split-3", "--skip-technical"]
                else:
                    cmd = ["fasterq-dump", "-e", str(threads), "-f", "-3"]
            else:
                suffix = "er"
                if fastqdump:
                    suffix = ""
                prog_to_run = "fast" + suffix + "q-dump"
                cmd = [prog_to_run] + custom_args.split(' ')
            if loc != "":
                cmd = cmd + ['-O', loc]
            cmd = cmd + [acc]
            print("running: "+" ".join(cmd))
            retcode = call(cmd)
            rgzip = 0
            if retcode == 0:
                if not fastqdump:
                    # zip all possible output files for that acc
                    fnames = build_paths(acc, loc, False) + build_paths(acc, loc, True)
                    rgzip = gzip_files(fnames, zip_func, threads)
                if rgzip == 0:
                    if check_existing(loc, acc) != False:
                        break

            # only here if downloading and zipping failed
            print("SRA download for acc "+acc+" failed, retrying "+str(retries)+" more times.")
            if retries > 0:
                time.sleep(100) #TODO?: user-modifiable
                retries -= 1
            else:
                raise Exception("download for "+acc+" failed. fast(er)q-dump returned "+str(retcode)+", pigz returned "+str(rgzip)+".")
        else:
            break

