#!/bin/bash

cd ..

python3 setup.py sdist bdist_wheel

twine upload dist/*

rm -r grabseqs.egg-info/
rm -r build/
rm -r dist/

cd conda-recipe

bash conda-build.sh
