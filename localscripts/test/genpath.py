#!/usr/bin/env python

from __future__ import print_function, absolute_import, with_statement

import os
import pytest

from localscripts.common import LocalConfig
from localscripts.test.common import mk_config, config_filename
from localscripts.gen_path import _fill_tpl, gen_path

class DummyConfig(object):
    cc = 'compiler'
    cxx = 'cxx_compiler'
    f77 = 'fortran_compiler'
    install_prefix = '/home'
    basedir = '/tmp'
    expected = '''
export BASEDIR=/tmp
export INSTALL_PREFIX=/home
export PATH=${INSTALL_PREFIX}/bin:$PATH
export LD_LIBRARY_PATH=${INSTALL_PREFIX}/lib64:${INSTALL_PREFIX}/lib:$LD_LIBRARY_PATH
export PKG_CONFIG_PATH=${INSTALL_PREFIX}/lib64/pkgconfig:${INSTALL_PREFIX}/lib/pkgconfig:${INSTALL_PREFIX}/share/pkgconfig:$PKG_CONFIG_PATH
export CC=compiler
export CXX=cxx_compiler
export F77=fortran_compiler
[ -e ${INSTALL_PREFIX}/bin/activate ] && . ${INSTALL_PREFIX}/bin/activate
export OMP_NUM_THREADS=1
'''


def test_template():
    config = DummyConfig()
    assert config.expected == _fill_tpl(config)


def test_shipped_configs(config_filename):
    os.environ['OPTS'] = config_filename
    os.environ['INSTALL_PREFIX'] = '/tmp'
    cfg = mk_config()
    tpl = _fill_tpl(cfg)
    # issue #4
    assert 'none' not in tpl.lower()
    gen_path(cfg)

