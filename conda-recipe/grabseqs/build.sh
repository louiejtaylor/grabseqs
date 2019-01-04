#!/bin/bash

mkdir -p ${PREFIX}/bin

python ${SRC_DIR}/setup.py

cp ${SRC_DIR}/bin/grabseqs ${PREFIX}/bin
chmod +x ${PREFIX}/bin/grabseqs
