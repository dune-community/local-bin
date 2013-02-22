#!/bin/bash

# create log dir
LOG_DIR=$(mktemp -d /tmp/dune_demos.XXXXXXXX)
LOG_FILE=$LOG_DIR/test.log
touch $LOG_FILE &> /dev/null
if [ $? != 0 ] ; then
  echo "Error: could not create: $LOG_DIR/test.log." >&2
  exit 1
else
  rm $LOG_FILE &> /dev/null
fi

echo -ne "writing path definitions... "
LOG_FILE=$LOG_DIR/gen_PATH.log
./local/bin/gen_path.py &> $LOG_FILE
if [ $? == 0 ] ; then
  source PATH &>> $LOG_FILE
  echo "done (run '. PATH.sh' from now on)"
else
  echo "failed (see $LOG_FILE for details)" >&2
  exit 1
fi

echo "downloading external libraries:"
LOG_FILE=$LOG_DIR/download_external_libraries.log
./local/bin/download_external_libraries.py 1
#if [ $? == 0 ] ; then
  #echo "done"
#else
  #echo "failed (see $LOG_FILE for details)" >&2
  #exit 1
#fi

echo "building external libraries:"
LOG_FILE=$LOG_DIR/build_external_libraries.log
./local/bin/build_external_libraries.py 1
#if [ $? == 0 ] ; then
  #echo "done"
#else
  #echo "failed (see $LOG_FILE for details)" >&2
  #exit 1
#fi

echo "building dune modules:"
LOG_FILE=$LOG_DIR/build_dune_modules.log
./local/bin/build_dune_modules.py 1
#if [ $? == 0 ] ; then
  #echo "done"
#else
  #echo "failed (see $LOG_FILE for details)" >&2
  #exit 1
#fi

echo "building demos:"
./local/bin/build_demos.py 1
