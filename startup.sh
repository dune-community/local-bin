#!/bin/bash
BASEDIR="$(cd "$(dirname ${BASH_SOURCE[0]})" ; cd .. ;  pwd -P )"

cd ${BASEDIR}

echo -ne "writing path definitions... "
./bin/gen_path.py
if [ $? == 0 ] ; then
  source PATH.sh
  echo "done (run 'source PATH.sh' from now on)"
else
  echo "failed" >&2
  exit 1
fi

echo "downloading external libraries:"
./bin/download_external_libraries.py
if [ $? != 0 ] ; then
  exit 1
fi

echo "building external libraries:"
./bin/build_external_libraries.py
if [ $? != 0 ] ; then
  exit 1
fi

echo "building dune modules:"
dune_setup ${1}
if [ $? != 0 ] ; then
  exit 1
fi

