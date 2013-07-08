#!/usr/bin/env python

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

filename = common.external_libraries_cfg_filename

verbose = True
if len(sys.argv) > 1:
    verbose = False


def download_library(library, src):
    if verbose:
        print('  downloading from \'{src}\'... '.format(src=src), end='')
    sys.stdout.flush()
    dest = join(common.SRCDIR(), src.split('/')[-1])
    filename = join(common.SRCDIR(), dest)
    filetype = ''
    if os.path.exists(filename):
        (filename, h) = urllib.urlretrieve(filename)
        filetype = h['Content-Type']
        if verbose:
            print('not necessary (already exists)')
    else:
        (filename, headers) = urllib.urlretrieve(src, dest)
        filetype = headers['Content-Type']
        if verbose:
            print('done')
    if verbose:
        print('  unpacking \'{filename}\' '.format(filename=filename.split('/')[-1]), end='')
    if filetype.startswith('application/x-gzip') or filetype.startswith('application/x-tar') or filetype.startswith('application/x-bzip'):
        tar = tarfile.open(filename)
        # get the leading directory name
        names = tar.getnames()
        extracted_dir_name = names[0].split('/')[0]
        if verbose:
            print('to \'{extracted_dir_name}\'... '.format(extracted_dir_name=extracted_dir_name), end='')
        if not os.path.abspath(join(common.SRCDIR(), extracted_dir_name)).startswith(common.SRCDIR()):
            if verbose:
                print('unsafe filename in tar: \'{unsafe_name}\', aborting!'.format(unsafe_name=extracted_dir_name))
            return False
        for name in names:
            if not (name.startswith(extracted_dir_name + '/') or name is extracted_dir_name):
                if verbose:
                    print('tars containing more than one toplevel dir not supported, aborting!')
                return False
        if os.path.exists(join(common.SRCDIR(), extracted_dir_name)):
            if verbose:
                print('not necessary (already exists)')
        else:
            tar.extractall(common.SRCDIR())
            if verbose:
                print('done')
        tar.close()
    else:
        if verbose:
            print('file is of wrong type (is \'{is_type}\'), aborting!'.format(is_type=filetype))
        return False
    if verbose:
        print('  moving \'{src}\' to \'{dest}\'... '.format(src=extracted_dir_name, dest=library), end='')
    sys.stdout.flush()
    if os.path.exists(join(common.SRCDIR(), library)):
        if verbose:
            print('not necessary (already exists)')
    else:
        shutil.move(join(common.SRCDIR(), extracted_dir_name), join(common.SRCDIR(), library))
        if verbose:
            print('done')
    return True
# def download_library


def git_clone_library(library, src):
    if verbose:
        print('  cloning \'{src}\':'.format(src=src))
    sys.stdout.flush()
    if os.path.exists(join(common.SRCDIR(), library)):
        if verbose:
            print('not necessary (already exists)')
        return True
    else:
        if verbose:
            ret = subprocess.call('git clone ' + src + ' ' + library,
                                  shell=True,
                                  env=common.env(),
                                  cwd=common.SRCDIR(),
                                  stdout=sys.stdout,
                                  stderr=sys.stderr)
        else:
            with open(os.devnull, "w") as devnull:
                ret = subprocess.call('git clone ' + src + ' ' + library,
                                      shell=True,
                                      env=common.env(),
                                      cwd=common.SRCDIR(),
                                      stdout=devnull,
                                      stderr=devnull)
        return not bool(ret)
# git_clone_library


# main
if verbose:
    print('reading \'{filename}\': '.format(filename=filename.split('/')[-1]), end='')
config = ConfigParser.ConfigParser()
try:
    config.readfp(open(filename))
except:
    raise Exception('Could not open \'{filename}\' with configparser!'.format(filename=filename))
libraries = config.sections()
if len(libraries) == 0:
    if verbose:
        print(' no external libraries specified')
    exit
else:
    for library in libraries:
        if verbose:
            print(library + ' ', end='')
    if verbose:
        print('')

failures = 0
for library in libraries:
    if verbose:
        print(library + ':')
    else:
        print('  ' + library + '... ', end='')
        sys.stdout.flush()
    success = False
    if config.has_option(library, 'git'):
        success = git_clone_library(library, config.get(library, 'git'))
    elif config.has_option(library, 'src'):
        success = download_library(library, config.get(library, 'src'))
    else:
        if verbose:
            print('missing \'src=some_url\' or \'git=some_git_url\' in section \'{library]\', aborting!'.format(library=library))
    if not verbose:
        if success:
            print('done')
        else:
            failures += 1
            print('failed')
if not verbose:
    if failures > 0:
        print('  call \'./local/bin/download_external_libraries.py\' manually to examine errors')
