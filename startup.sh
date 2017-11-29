#!/bin/bash

set -e

export OPTS="${1}"

BASEDIR="$(cd "$(dirname ${BASH_SOURCE[0]})" ; cd .. ;  pwd -P )"
cd ${BASEDIR}

echo -ne "writing path definitions... "
./bin/gen_path.py
source PATH.sh
echo "done (run 'source PATH.sh' from now on)"

echo "downloading external libraries:"
./bin/download_external_libraries.py

echo "building external libraries:"
./bin/build_external_libraries.py

echo "building dune modules:"
dune_setup ${OPTS}

