#!/bin/bash

mkdir -p ${PREFIX}/bin

cp ${SRC_DIR}/bin/grabseqs ${PREFIX}/bin
chmod +x ${PREFIX}/bin/grabseqs
