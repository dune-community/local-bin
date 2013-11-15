#!/bin/bash

BASEDIR=$PWD
PSTATS_FILE=$BASEDIR/profile_output.pstats
SVG_FILE=$BASEDIR/profile_output.svg
echo "calling 'python ${@}' in cProfile mode:"
python -m cProfile -o $PSTATS_FILE "${@}"
[ -e $PSTATS_FILE ] && gprof2dot -f pstats $PSTATS_FILE | dot -Tsvg -o $SVG_FILE
if [ -e $SVG_FILE ] ; then
	echo ""
	echo "finished profiling, run"
       	echo "  'eog ${SVG_FILE/$PWD\//}'"
	echo "or"
	echo "  'runsnake ${PSTATS_FILE/$PWD\//}'"
	exit 0
else
	echo ""
	echo "profiling failed"
	exit 1
fi
