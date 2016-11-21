#!/usr/bin/env python

from __future__ import print_function, absolute_import, with_statement

import os
import pytest
from tempfile import NamedTemporaryFile

from localscripts.common import LocalConfig

TESTDATA_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data'))
CONFIG_DIR = os.path.join(TESTDATA_DIR, 'config.opts')


@pytest.fixture(params=[os.path.join(CONFIG_DIR, fn)
                        for fn in os.listdir(CONFIG_DIR) if os.path.isfile(os.path.join(CONFIG_DIR, fn))])
def config_filename(request):
    print('Checking {}'.format(request.param))
    return request.param


def mk_config(*args, **kwargs):
    return LocalConfig(basedir=TESTDATA_DIR, *args, **kwargs)


def test_shipped_configs(config_filename):
    os.environ['OPTS'] = config_filename
    os.environ['INSTALL_PREFIX'] = '/tmp'
    cfg = mk_config()
    assert cfg.config_opts_filename == config_filename
    assert cfg.cc is not None


def test_nested_newlines():
    os.environ['OPTS'] = os.path.join(CONFIG_DIR, 'nested_newlines')
    os.environ['INSTALL_PREFIX'] = '/tmp'
    cfg = mk_config()
    assert cfg.cxx_flags == '-DDEBUG -g3 -ggdb -std=c++11 -O2 -w -ftest-coverage -fPIC -DDXT_DISABLE_LARGE_TESTS=1'


def test_missing():
    os.environ['INSTALL_PREFIX'] = '/tmp'

    os.environ['OPTS'] = 'nosuch.opts'
    with pytest.raises(IOError) as err:
        mk_config()
    assert 'Environment defined OPTS not discovered' in str(err.value)

    with NamedTemporaryFile(dir=TESTDATA_DIR, mode='wt') as tmp:
        tmp.write('CF=;;')
        os.environ['OPTS'] = tmp.name
        cfg = mk_config(allow_for_broken_config_opts=True)
        assert cfg.cxx == 'g++' and cfg.f77 == 'gfortran' and cfg.cc == 'gcc'
        assert cfg.cxx_flags == ''

    del os.environ['OPTS']
    with pytest.raises(RuntimeError) as err:
        mk_config()
    assert 'You either have to set OPTS or CC in order to specify a config.opts file' in str(err.value)

    os.environ['CC'] = 'nosuch.compiler'
    with pytest.raises(IOError) as err:
        mk_config()
    assert 'No suitable opts file for CC' in str(err.value)



