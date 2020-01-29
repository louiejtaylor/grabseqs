# test to see whether install succeeded
function test_grabseqs_installed {
    grabseqs -v
    grabseqs -h
}

# test missing sra-tools
function test_grabseqs_no_sratools {
    conda remove sra-tools -qy
    if grabseqs sra -o $TMPDIR/test_no_sra-tools ERR2279063; then
        exit 1
    fi
    conda install sra-tools>2.9 -c bioconda -qy
}

# test missing pigz
function test_grabseqs_no_pigz {
    if which pigz; then
        echo "pigz installed outside of conda, cannot test whether it is missing"
    else
        conda remove pigz -qy
        u=`grabseqs mgrast -o $TMPDIR/test_nopigz mgm4633450.3`
        echo $u
        if [[ $u != *"pigz not found, using gzip"* ]] ; then
            exit 1
        fi
        conda install -c anaconda pigz -qy
   fi
}

# test conda install
function test_grabseqs_conda_install {
    conda deactivate
    conda create -n grabseqs-unittest-conda -qy
    conda activate grabseqs-unittest-conda
    conda install -c louiejtaylor -c bioconda -c conda-forge -qy grabseqs
    conda deactivate
    conda env remove -yqn grabseqs-unittest-conda
    conda activate grabseqs-unittest
}

# test install with python3.7 (issue #38)
function test_grabseqs_conda_newer_python {
    conda deactivate
    conda create -n grabseqs-unittest-py37 -qy
    conda activate grabseqs-unittest-py37
    conda install python=3.7 -qy
    conda install -c louiejtaylor -c bioconda -c conda-forge grabseqs -qy
    conda deactivate
    conda env remove -yqn grabseqs-unittest-py37
    conda activate grabseqs-unittest
}
