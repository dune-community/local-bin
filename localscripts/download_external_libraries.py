#!/usr/bin/env python

from __future__ import print_function, absolute_import, with_statement

import mimetypes
import traceback
import sys
import os
from os.path import join
import shutil
import tarfile
import subprocess
try:
    import ConfigParser as configparser
except ImportError:
    import configparser
import requests
from localscripts import common
from localscripts.common import BraceMessage as Br

log = common.get_logger('external_libraries.download')


class DownloadException(Exception):
    pass


def download_library(local_config, library, src):
    log.debug(Br('  downloading from \'{src}\'... ', src=src), end='')
    dest = join(local_config.srcdir, os.path.basename(src))
    filename = join(local_config.srcdir, dest)
    if os.path.exists(filename):
        r = None
        filetype, _ = mimetypes.guess_type(filename)
        log.debug('not necessary (already exists)')
    else:
        r = requests.get(src)
        filetype = r.headers['content-type']
        log.debug('done')
    log.debug(Br('  unpacking \'{filename}\' ', filename=filename.split('/')[-1]), end='')
    if filetype.startswith('application/x-gzip') or filetype.startswith('application/x-tar') or filetype.startswith(
            'application/x-bzip') or filetype.startswith('application/gzip') or filetype.startswith(
                'application/octet-stream'):
        if r is not None:
            with open(dest, 'wb') as f:
                f.write(r.content)
        tar = tarfile.open(filename)
        # get the leading directory name
        names = tar.getnames()
        extracted_dir_name = names[0].split('/')[0]
        log.debug(Br('to \'{extracted_dir_name}\'... ', extracted_dir_name=extracted_dir_name), end='')
        if not os.path.abspath(join(local_config.srcdir, extracted_dir_name)).startswith(local_config.srcdir):
            raise DownloadException(
                'unsafe filename in tar: \'{unsafe_name}\', aborting!'.format(unsafe_name=extracted_dir_name))
        for name in names:
            if not (name.startswith(extracted_dir_name + '/') or name == extracted_dir_name):
                raise DownloadException('tars containing more than one toplevel dir not supported, aborting!')

        if os.path.exists(join(local_config.srcdir, extracted_dir_name)):
            log.debug('not necessary (already exists)')
        else:
            tar.extractall(local_config.srcdir)
            log.debug('done')
        tar.close()
    else:
        raise DownloadException('file is of wrong type (is \'{is_type}\'), aborting!'.format(is_type=filetype))

    log.debug(Br('  moving \'{src}\' to \'{dest}\'... ', src=extracted_dir_name, dest=library), end='')
    if os.path.exists(join(local_config.srcdir, library)):
        log.debug('not necessary (already exists)')
    else:
        shutil.move(join(local_config.srcdir, extracted_dir_name), join(local_config.srcdir, library))
        log.debug('done')


def git_clone_library(local_config, library, src):
    log.debug(Br('  cloning \'{src}\':', src=src))
    if os.path.exists(join(local_config.srcdir, library)):
        log.debug('not necessary (already exists)')
    else:
        with open(os.devnull, 'wt') as devnull:
            subprocess.check_call(
                'git clone ' + src + ' ' + library,
                shell=True,
                env=local_config.make_env(),
                cwd=local_config.srcdir,
                stdout=sys.stdout if common.VERBOSE else devnull,
                stderr=sys.stderr if common.VERBOSE else devnull)


def download_all(local_config):
    local_config = local_config or common.LocalConfig(allow_for_broken_config_opts=True)
    log.debug(
        Br('reading \'{filename}\': ', filename=os.path.basename(local_config.external_libraries_cfg_filename)),
        end='')
    ext_libs_config = configparser.ConfigParser()
    try:
        ext_libs_config.readfp(open(local_config.external_libraries_cfg_filename, mode='rt'))
    except:
        raise Exception('Could not open \'{filename}\' with configparser!'.format(
            filename=local_config.external_libraries_cfg_filename))
    libraries = ext_libs_config.sections()
    if len(libraries) == 0:
        log.debug(' no external libraries specified')
        return 0
    else:
        log.debug(' '.join(libraries))

    failures = 0
    for library in libraries:
        log.info('  ' + library + '... ', end='')
        log.debug('')

        if ext_libs_config.has_option(library, 'only_build') and ext_libs_config.getboolean(library, 'only_build'):
            log.info('nothing to do, since \'only_build\' is True')
            continue
        try:
            if ext_libs_config.has_option(library, 'git'):
                git_clone_library(local_config=local_config, library=library, src=ext_libs_config.get(library, 'git'))
            elif ext_libs_config.has_option(library, 'src'):
                download_library(local_config=local_config, library=library, src=ext_libs_config.get(library, 'src'))
            else:
                log.debug(
                    Br('missing \'src=some_url\' or \'git=some_git_url\' in section \'{library}\', aborting!',
                       library=library))
            log.info('done')
        except Exception:
            failures += 1
            log.info('failed')
            log.debug(traceback.format_exc())

    if failures > 0:
        log.critical('  call \'./local/bin/download_external_libraries.py\' manually to examine errors')
    return failures
