#/bin/bash

# setup
set -e

STARTING_DIR=$(pwd)

export PATH=${PATH}:${HOME}/miniconda3/bin

# set up temp locations
TMPLOC=/tmp

USER_TMPDIR=false
SKIP_IMICROBE=false
SKIP_SRA=false
SKIP_MGRAST=false

while getopts "d:t:imsvh" opt; do
  case $opt in
    d)
      USER_TMPDIR=true
      TMPLOC=`readlink -f $OPTARG`
      ;;
    i)
      SKIP_IMICROBE=true
      ;;
    m)
      SKIP_MGRAST=true
      ;;
    s)
      SKIP_SRA=true
      ;;
    t)
      RUN_TEST=$OPTARG
      ;;
    v)
      VERBOSE=true
      ;;
    h)
      echo "Run the grabseqs test suite."
      echo "  -d DIR       Use DIR rather than a temporary directory (remains after tests finish)"
      echo "  -t TEST      Run a specific test only"
      echo "  -i           Don't run iMicrobe tests"
      echo "  -m           Don't run MG-RAST tests"
      echo "  -s           Don't run SRA tests"
      echo "  -v           Run tests with verbose output"
      echo "  -h           Display this message and exit"
      exit 1
      ;;
    \?)
      echo "Unknown option - '$OPTARG'"
      exit 1
      ;;
  esac
done

TMPDIR=$TMPLOC/grabseqs_unittest
mkdir -p $TMPDIR
fs=`ls $TMPDIR | wc -l`

if [ $fs -ne 0 ] ; then
    echo "Directory $TMPDIR not empty. Clean it or specify a testing location with -d [loc]"
    exit 1
fi

GREEN="\x1B[32m"
RESET="\x1B[0m"
PASS="${GREEN}\u2714${RESET}"
FAIL="${RED}X${RESET}"

# environment and package install

function setup {

    CONDA_BASE=$(conda info --base) # see https://github.com/conda/conda/issues/7980
    source $CONDA_BASE/etc/profile.d/conda.sh # allows conda [de]activate in scripts
    verbose "Setting up conda environment..."
    conda env update --name=grabseqs-unittest --file environment.yml
    conda activate grabseqs-unittest
    # required for installing libs
    pip install setuptools
    verbose "Installing grabseqs library"
    python setup.py install

    # Fix CircleCI testing issue for iMicrobe
    if [ `echo $HOME | grep "/home/circleci" | wc -l` -eq 1 ]; then
        echo "Tests running on CircleCI, adding add'l dependency"
        pip uninstall "urllib3"
	pip install "urllib3"
	pip install "requests-html"
    fi
}

# functions copied and adapted from sunbeam-labs/sunbeam

function msg {
    echo -ne "${1}"
}

function verbose {
    if [ "$VERBOSE" = true ]; then
	echo -ne "${1}"
    fi
}

function broke {
    local RETCODE=$?
    msg "\nFailed command error output:\n`cat ${2}.err`\n"
    msg "${FAIL} (log: ${LOGFILE}.[out/err])\n"
    cleanup 1
}

function capture_output {
    msg "Running ${1}... "

    LOGFILE="${TMPDIR}/${1}"	
 
    set -o pipefail
    if [ "$VERBOSE" = true ]; then
	OUTPUT_STRING="> >(tee ${LOGFILE}.out) 2> >(tee ${LOGFILE}.err >&2)"
    else
	OUTPUT_STRING="> ${LOGFILE}.out 2> ${LOGFILE}.err"
    fi
    trap "broke ${1} ${LOGFILE} $?" exit
    eval "${1} ${OUTPUT_STRING}"
    set +o pipefail
    trap "cleanup $?" exit
    msg "${PASS}\n"
}

function cleanup {
    local TMPRC=$?
    local RETCODE=$TMPRC
    if [ ${1} -gt ${TMPRC} ]; then
	RETCODE=${1}
    else
	RETCODE=${TMPRC}
    fi
    cd $STARTING_DIR
    if [ $RETCODE -ne 0 ]; then
	msg "${RED}-- TESTS FAILED --${RESET}\n"
    else
	msg "${GREEN}-- TESTS SUCCEEDED --${RESET}\n"
    fi
    conda deactivate

    verbose "Deleting temporary conda environment \n"
    conda env remove -yqn grabseqs-unittest

    # Remove temp directory if created by us
    if [ "$USER_TMPDIR" = false ]; then
	verbose "Deleting temporary directory ${TMPDIR}\n"
        rm -rf $TMPDIR
    fi

    # Exit, maintaining previous return code
    exit $RETCODE

    echo -e "$PASS all tests passed!"
}

function run_test_suite {
    for testcase in $(declare -f | grep -o "^test[a-zA-Z_]*") ; do
	capture_output ${testcase}
    done
}

trap cleanup exit

capture_output setup

# read in tests
source tests/test_general.bash

if [ "$SKIP_IMICROBE" = false ]; then
    source tests/test_imicrobe.bash
fi

if [ "$SKIP_SRA" = false ]; then
    source tests/test_sra.bash
fi

if [ "$SKIP_MGRAST" = false ]; then
    source tests/test_mgrast.bash
fi


# Run single test, if specified, or all found tests otherwise
if [ ! -z ${RUN_TEST+x} ]; then
    capture_output ${RUN_TEST}
else
    run_test_suite
fi

