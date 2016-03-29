#!/bin/bash

echo -ne "writing path definitions... "
./local/bin/gen_path.py
if [ $? == 0 ] ; then
  source PATH.sh
  echo "done (run 'source PATH.sh' from now on)"
else
  echo "failed" >&2
  exit 1
fi

echo "downloading external libraries:"
./local/bin/download_external_libraries.py 1
if [ $? != 0 ] ; then
  exit 1
fi

echo "building external libraries:"
./local/bin/build_external_libraries.py 1
if [ $? != 0 ] ; then
  exit 1
fi

echo "building dune modules:"
./local/bin/build_dune_modules.py 1
if [ $? != 0 ] ; then
  exit 1
fi

