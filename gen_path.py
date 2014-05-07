#!/usr/bin/env python2.7

from __future__ import print_function
from os.path import join

import common as common

with open(join(common.BASEDIR(), 'PATH.sh'), 'w') as pathfile:
    pathfile.write('export BASEDIR={BASEDIR}\n'.format(BASEDIR=common.BASEDIR()))
    pathfile.write('export PATH=${BASEDIR}/local/bin:$PATH\n')
    pathfile.write('export LD_LIBRARY_PATH=${BASEDIR}/local/lib64:${BASEDIR}/local/lib:$LD_LIBRARY_PATH\n')
    pathfile.write('export PKG_CONFIG_PATH=${BASEDIR}/local/lib64/pkgconfig:${BASEDIR}/local/lib/pkgconfig:${BASEDIR}/local/share/pkgconfig:$PKG_CONFIG_PATH\n')
    #pathfile.write('export CC={CC}\n'.format(CC=common.CC()))
    #pathfile.write('export CXX={CXX}\n'.format(CXX=common.CXX()))
    #pathfile.write('export F77={F77}\n'.format(F77=common.F77()))
    pathfile.write('export PYTHON_VERSION=2.7\n')
    pathfile.write('[ -e $BASEDIR/virtualenv/bin/activate ] && . $BASEDIR/virtualenv/bin/activate\n')
