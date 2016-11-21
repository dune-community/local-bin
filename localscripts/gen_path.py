#!/usr/bin/env python2.7

from __future__ import print_function, absolute_import, with_statement

import string
from os.path import join

from localscripts import common

pathfile_tpl ='''
export BASEDIR=${BASEDIR}
export INSTALL_PREFIX=${INSTALL_PREFIX}
export PATH=${INSTALL_PREFIX}/bin:$PATH
export LD_LIBRARY_PATH=${INSTALL_PREFIX}/lib64:${INSTALL_PREFIX}/lib:$LD_LIBRARY_PATH
export PKG_CONFIG_PATH=${INSTALL_PREFIX}/lib64/pkgconfig:${INSTALL_PREFIX}/lib/pkgconfig:${INSTALL_PREFIX}/share/pkgconfig:$PKG_CONFIG_PATH
export CC=${CC}
export CXX=${CXX}
export F77=${F77}
export PYTHON_VERSION=2.7
[ -e ${INSTALL_PREFIX}/bin/activate ] && . ${INSTALL_PREFIX}/bin/activate
export OMP_NUM_THREADS=1
export SIMDB_PATH=${BASEDIR}/DATA
export QUEUE_DIRECTORY=${BASEDIR}/QUEUE
'''


def _fill_tpl(local_config):
    tpl = string.Template(pathfile_tpl)
    return tpl.safe_substitute(INSTALL_PREFIX=local_config.install_prefix,
                               BASEDIR=local_config.basedir,
                               CC=local_config.cc, CXX=local_config.cxx,
                               F77=local_config.f77)


def gen_path(config=None):
    local_config = config or common.LocalConfig()
    with open(join(local_config.basedir, 'PATH.sh'), 'wt') as pathfile:
        # see common._prep_build_command on how to make this more elegant
        pathfile.write(_fill_tpl(local_config))

