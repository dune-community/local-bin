#!/usr/bin/env python2.7

from __future__ import print_function, absolute_import, with_statement

import string
from os.path import join

from localscripts import common

pathfile_tpl = '''
export BASEDIR=${BASEDIR}
export INSTALL_PREFIX=${INSTALL_PREFIX}
export PATH=${_INST_PREF_}/bin:$PATH
export LD_LIBRARY_PATH=${_INST_PREF_}/lib64:${_INST_PREF_}/lib:$LD_LIBRARY_PATH
export PKG_CONFIG_PATH=${_INST_PREF_}/lib64/pkgconfig:${_INST_PREF_}/lib/pkgconfig:${_INST_PREF_}/share/pkgconfig:$PKG_CONFIG_PATH
export CC=${CC}
export CXX=${CXX}
export F77=${F77}
[ -e ${_INST_PREF_}/bin/activate ] && . ${_INST_PREF_}/bin/activate
export OMP_NUM_THREADS=1
'''


def _fill_tpl(local_config):
    tpl = string.Template(pathfile_tpl)
    return tpl.safe_substitute(
        INSTALL_PREFIX=local_config.install_prefix,
        BASEDIR=local_config.basedir,
        CC=local_config.cc,
        CXX=local_config.cxx,
        F77=local_config.f77,
        _INST_PREF_="${INSTALL_PREFIX}")


def gen_path(local_config):
    local_config = local_config or common.LocalConfig()
    with open(join(local_config.basedir, 'PATH.sh'), 'wt') as pathfile:
        # see common._prep_build_command on how to make this more elegant
        pathfile.write(_fill_tpl(local_config))
