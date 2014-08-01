#!/usr/bin/env python2.7

from __future__ import print_function
import ConfigParser
import urllib
import os
from os.path import join
import shutil
import sys
import tarfile
import subprocess


import common


log = common.get_logger('external_libraries.download')
VERBOSE = common.VERBOSE

def download_library(library, src):
    config = common.LocalConfig()
    if VERBOSE:
        print('  downloading from \'{src}\'... '.format(src=src), end='')
    sys.stdout.flush()
    dest = join(config.srcdir, os.path.basename(src))
    filename = join(config.srcdir, dest)
    if os.path.exists(filename):
        filename, h = urllib.urlretrieve(filename)
        filetype = h['Content-Type']
        if VERBOSE:
            print('not necessary (already exists)')
    else:
        filename, headers = urllib.urlretrieve(src, dest)
        filetype = headers['Content-Type']
        if VERBOSE:
            print('done')
    if VERBOSE:
        print('  unpacking \'{filename}\' '.format(filename=filename.split('/')[-1]), end='')
    if filetype.startswith('application/x-gzip') or filetype.startswith('application/x-tar') or filetype.startswith('application/x-bzip'):
        tar = tarfile.open(filename)
        # get the leading directory name
        names = tar.getnames()
        extracted_dir_name = names[0].split('/')[0]
        if VERBOSE:
            print('to \'{extracted_dir_name}\'... '.format(extracted_dir_name=extracted_dir_name), end='')
        if not os.path.abspath(join(config.srcdir, extracted_dir_name)).startswith(config.srcdir):
            if VERBOSE:
                print('unsafe filename in tar: \'{unsafe_name}\', aborting!'.format(unsafe_name=extracted_dir_name))
            return False
        for name in names:
            if not (name.startswith(extracted_dir_name + '/') or name is extracted_dir_name):
                if VERBOSE:
                    print('tars containing more than one toplevel dir not supported, aborting!')
                return False
        if os.path.exists(join(config.srcdir, extracted_dir_name)):
            if VERBOSE:
                print('not necessary (already exists)')
        else:
            tar.extractall(config.srcdir)
            if VERBOSE:
                print('done')
        tar.close()
    else:
        if VERBOSE:
            print('file is of wrong type (is \'{is_type}\'), aborting!'.format(is_type=filetype))
        return False
    if VERBOSE:
        print('  moving \'{src}\' to \'{dest}\'... '.format(src=extracted_dir_name, dest=library), end='')
    sys.stdout.flush()
    if os.path.exists(join(config.srcdir, library)):
        if VERBOSE:
            print('not necessary (already exists)')
    else:
        shutil.move(join(config.srcdir, extracted_dir_name), join(config.srcdir, library))
        if VERBOSE:
            print('done')
    return True
# def download_library


def git_clone_library(library, src):
    local_config = common.LocalConfig()
    if VERBOSE:
        print('  cloning \'{src}\':'.format(src=src))
    sys.stdout.flush()
    if os.path.exists(join(local_config.srcdir, library)):
        if VERBOSE:
            print('not necessary (already exists)')
        return True
    else:
        if VERBOSE:
            ret = subprocess.call('git clone ' + src + ' ' + library,
                                  shell=True,
                                  env=local_config.make_env(),
                                  cwd=local_config.srcdir,
                                  stdout=sys.stdout,
                                  stderr=sys.stderr)
        else:
            with open(os.devnull, "w") as devnull:
                ret = subprocess.call('git clone ' + src + ' ' + library,
                                      shell=True,
                                      env=local_config.make_env(),
                                      cwd=local_config.srcdir,
                                      stdout=devnull,
                                      stderr=devnull)
        return not bool(ret)
# git_clone_library


if __name__ == '__main__':
    local_config = common.LocalConfig()
    if VERBOSE:
        print('reading \'{filename}\': '.format(filename=os.path.basename(local_config.external_libraries_cfg_filename)), end='')
    config = ConfigParser.ConfigParser()
    try:
        config.readfp(open(local_config.external_libraries_cfg_filename))
    except:
        raise Exception('Could not open \'{filename}\' with configparser!'.format(filename=local_config.external_libraries_cfg_filename))
    libraries = config.sections()
    if len(libraries) == 0:
        if VERBOSE:
            print(' no external libraries specified')
        sys.exit(0)
    else:
        for library in libraries:
            if VERBOSE:
                print(library + ' ', end='')
        if VERBOSE:
            print('')

    failures = 0
    for library in libraries:
        if VERBOSE:
            print(library + ':')
        else:
            print('  ' + library + '... ', end='')
            sys.stdout.flush()
        success = False
        download=True
        if config.has_option(library, 'only_build'):
            download = not bool(config.get(library, 'only_build'))
        if download:
            if config.has_option(library, 'git'):
                success = git_clone_library(library, config.get(library, 'git'))
            elif config.has_option(library, 'src'):
                success = download_library(library, config.get(library, 'src'))
            else:
                if VERBOSE:
                    print('missing \'src=some_url\' or \'git=some_git_url\' in section \'{library}\', aborting!'.format(library=library))
            if not VERBOSE:
                if success:
                    print('done')
                else:
                    failures += 1
                    print('failed')
        else:
            print('nothing to do, since \'only_build\' is True')
    if not VERBOSE:
        if failures > 0:
            print('  call \'./local/bin/download_external_libraries.py\' manually to examine errors')
    sys.exit(failures)
