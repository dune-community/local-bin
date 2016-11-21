#!/usr/bin/env python

from __future__ import print_function, absolute_import, with_statement

import pytest
import os

from localscripts.test import common as test_common
from localscripts import common
from localscripts.download_external_libraries import download_all


TESTDATA_DIR = test_common.TESTDATA_DIR


@pytest.fixture(params=[os.path.join(root, fn)
                        for root, _, files in os.walk(os.path.join(TESTDATA_DIR, 'ext_configs')) for fn in files])
def config_filename(request):
    return request.param


def test_shipped_configs(config_filename):
    os.environ['OPTS'] = os.path.join(TESTDATA_DIR, 'config.opts', 'clang')
    os.environ['INSTALL_PREFIX'] = '/tmp'
    fails = download_all(local_config=test_common.mk_config(external_libraries=config_filename))
    assert fails == 0


if __name__ == '__main__':
    sys.exit(download_all())
