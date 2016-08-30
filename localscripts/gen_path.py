#!/usr/bin/env python2.7

from __future__ import print_function, absolute_import, with_statement

import string
import os
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


class DummyConfig(object):
    cc = 'compiler'
    cxx = 'cxx_compiler'
    f77 = 'fortran_compiler'
    install_prefix = '/home'
    basedir = '/tmp'
    expected = '''
export BASEDIR=/tmp
export INSTALL_PREFIX=/home
export PATH=/home/bin:$PATH
export LD_LIBRARY_PATH=/home/lib64:/home/lib:$LD_LIBRARY_PATH
export PKG_CONFIG_PATH=/home/lib64/pkgconfig:/home/lib/pkgconfig:/home/share/pkgconfig:$PKG_CONFIG_PATH
export CC=compiler
export CXX=cxx_compiler
export F77=fortran_compiler
export PYTHON_VERSION=2.7
[ -e /home/bin/activate ] && . /home/bin/activate
export OMP_NUM_THREADS=1
export SIMDB_PATH=/tmp/DATA
export QUEUE_DIRECTORY=/tmp/QUEUE
'''


def test_template():
    config = DummyConfig()
    assert config.expected == _fill_tpl(config)


config_filename = common.config_filename


def test_shipped_configs(config_filename):
    os.environ['OPTS'] = config_filename
    os.environ['INSTALL_PREFIX'] = '/tmp'
    cfg = common.mk_config()
    tpl = _fill_tpl(cfg)
    # issue #4
    assert 'none' not in tpl.lower()
    gen_path(cfg)
