#!/usr/bin/env python

from __future__ import print_function
try:
    import ConfigParser as configparser
except ImportError:
    import configparser
import pytest
import urllib
import os
from os.path import join
import shutil
import sys
import tarfile
import subprocess

import common


log = common.get_logger('external_libraries.download')


def download_library(library, src):
    config = common.LocalConfig(allow_for_broken_config_opts=True)
    log.debug('  downloading from \'{src}\'... '.format(src=src), end='')
    dest = join(config.srcdir, os.path.basename(src))
    filename = join(config.srcdir, dest)
    if os.path.exists(filename):
        filename, h = urllib.urlretrieve(filename)
        filetype = h['Content-Type']
        log.debug('not necessary (already exists)')
    else:
        filename, headers = urllib.urlretrieve(src, dest)
        filetype = headers['Content-Type']
        log.debug('done')
    log.debug('  unpacking \'{filename}\' '.format(filename=filename.split('/')[-1]), end='')
    if filetype.startswith('application/x-gzip') or filetype.startswith('application/x-tar') or filetype.startswith(
            'application/x-bzip'):
        tar = tarfile.open(filename)
        # get the leading directory name
        names = tar.getnames()
        extracted_dir_name = names[0].split('/')[0]
        log.debug('to \'{extracted_dir_name}\'... '.format(extracted_dir_name=extracted_dir_name), end='')
        if not os.path.abspath(join(config.srcdir, extracted_dir_name)).startswith(config.srcdir):
            log.debug('unsafe filename in tar: \'{unsafe_name}\', aborting!'.format(unsafe_name=extracted_dir_name))
            return False
        for name in names:
            if not (name.startswith(extracted_dir_name + '/') or name is extracted_dir_name):
                log.debug('tars containing more than one toplevel dir not supported, aborting!')
                return False
        if os.path.exists(join(config.srcdir, extracted_dir_name)):
            log.debug('not necessary (already exists)')
        else:
            tar.extractall(config.srcdir)
            log.debug('done')
        tar.close()
    else:
        log.debug('file is of wrong type (is \'{is_type}\'), aborting!'.format(is_type=filetype))
        return False
    log.debug('  moving \'{src}\' to \'{dest}\'... '.format(src=extracted_dir_name, dest=library), end='')
    if os.path.exists(join(config.srcdir, library)):
        log.debug('not necessary (already exists)')
    else:
        shutil.move(join(config.srcdir, extracted_dir_name), join(config.srcdir, library))
        log.debug('done')
    return True

def git_clone_library(library, src):
    local_config = common.LocalConfig(allow_for_broken_config_opts=True)
    log.debug('  cloning \'{src}\':'.format(src=src))
    if os.path.exists(join(local_config.srcdir, library)):
        log.debug('not necessary (already exists)')
        return True
    else:
        with open(os.devnull, "w") as devnull:
            ret = subprocess.call('git clone ' + src + ' ' + library,
                                  shell=True,
                                  env=local_config.make_env(),
                                  cwd=local_config.srcdir,
                                  stdout=sys.stdout if common.VERBOSE else devnull,
                                  stderr=sys.stderr if common.VERBOSE else devnull)
        return not bool(ret)


def download_all():
    local_config = common.LocalConfig(allow_for_broken_config_opts=True)
    log.debug(
            'reading \'{filename}\': '.format(filename=os.path.basename(local_config.external_libraries_cfg_filename)),
            end='')
    config = configparser.ConfigParser()
    try:
        config.readfp(open(local_config.external_libraries_cfg_filename))
    except:
        raise Exception('Could not open \'{filename}\' with configparser!'.format(
            filename=local_config.external_libraries_cfg_filename))
    libraries = config.sections()
    if len(libraries) == 0:
        log.debug(' no external libraries specified')
        sys.exit(0)
    else:
        log.debug(' '.join(libraries))

    failures = 0
    for library in libraries:
        log.info('  ' + library + '... ', end='')
        log.debug('')
        success = False
        download = True
        if config.has_option(library, 'only_build'):
            download = not bool(config.get(library, 'only_build'))
        if download:
            if config.has_option(library, 'git'):
                success = git_clone_library(library, config.get(library, 'git'))
            elif config.has_option(library, 'src'):
                success = download_library(library, config.get(library, 'src'))
            else:
                log.debug('missing \'src=some_url\' or \'git=some_git_url\' in section \'{library}\', aborting!'.format(
                        library=library))
            if not common.VERBOSE:
                if success:
                    log.info('done')
                else:
                    failures += 1
                    log.info('failed')
        else:
            log.info('nothing to do, since \'only_build\' is True')
    if failures > 0:
        log.error('  call \'./local/bin/download_external_libraries.py\' manually to examine errors')
    sys.exit(failures)



TESTDATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'testdata')

@pytest.fixture(params=[os.path.join(root, fn)
                        for root,_, files in os.walk(os.path.join(TESTDATA_DIR, 'ext_configs')) for fn in files])
def config_filename(request):
    return request.param

def test_shipped_configs(config_filename):
    os.environ['OPTS'] = os.path.join(TESTDATA_DIR, '..', 'config.opts', 'clang')
    os.environ['INSTALL_PREFIX'] = '/tmp'
    download_all()


if __name__ == '__main__':
    download_all()