#!/bin/bash

# Assumes `conda config --set anaconda_upload yes` has
# been run--otherwise just upload manually per the 
# instructions from conda-build.

conda-build -c bioconda grabseqs
