#!/usr/bin/env python2.7

from __future__ import print_function
from os.path import join

import common as common

if __name__ == '__main__':
    local_config = common.LocalConfig()
    with open(join(local_config.basedir, 'PATH.sh'), 'w') as pathfile:
        pathfile.write('export basedir={basedir}\n'.format(BASEDIR=local_config.basedir))
        pathfile.write('export PATH=${basedir}/local/bin:$PATH\n')
        pathfile.write('export LD_LIBRARY_PATH=${basedir}/local/lib64:${basedir}/local/lib:$LD_LIBRARY_PATH\n')
        pathfile.write(
            'export PKG_CONFIG_PATH=${basedir}/local/lib64/pkgconfig:${basedir}/local/lib/pkgconfig:${basedir}/local/share/pkgconfig:$PKG_CONFIG_PATH\n')
        pathfile.write('export CC={CC}\n'.format(CC=local_config.cc))
        pathfile.write('export CXX={CXX}\n'.format(CXX=local_config.cxx))
        pathfile.write('export F77={F77}\n'.format(F77=local_config.f77))
        pathfile.write('export PYTHON_VERSION=2.7\n')
        pathfile.write('[ -e $basedir/virtualenv/bin/activate ] && . $basedir/virtualenv/bin/activate\n')
