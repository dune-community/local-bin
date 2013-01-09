#!/usr/bin/env python

from __future__ import print_function
import ConfigParser
import urllib
import os
from os.path import join
import shutil
import sys
import tarfile

import common

filename='external-libraries.cfg'

def download_library(library, src):
    print('  downloading \'{library}\' from \'{src}\'... '.format(library=library, src=src), end='')
    sys.stdout.flush()
    dest = join(common.SRCDIR(),src.split('/')[-1])
    filename = join(common.SRCDIR(), dest)
    filetype = ''
    if os.path.exists(filename):
        (filename, h) = urllib.urlretrieve(filename)
        filetype = h['Content-Type']
        print('not necessary (already exists)')
    else:
        (filename, headers) = urllib.urlretrieve(src, dest)
        filetype = headers['Content-Type']
        print('done')
    print('  unpacking \'{filename}\' '.format(filename=filename.split('/')[-1]), end='')
    if filetype.startswith('application/x-gzip') or filetype.startswith('application/x-tar'):
        tar = tarfile.open(filename)
        # get the leading directory name
        names = tar.getnames()
        extracted_dir_name = names[0].split('/')[0]
        print('to \'{extracted_dir_name}\'... '.format(extracted_dir_name=extracted_dir_name), end='')
        if not os.path.abspath(join(common.SRCDIR(), extracted_dir_name)).startswith(common.SRCDIR()):
            raise Exception('unsafe filename in tar: \'{unsafe_name}\'!'.format(unsafe_name=extracted_dir_name))
        for name in names:
            if not name.startswith(extracted_dir_name):
                raise Exception('tars containing more than one toplevel dir not supported!')
        if os.path.exists(join(common.SRCDIR(), extracted_dir_name)):
            print('not necessary (already exists)')
        else:
            tar.extractall(common.SRCDIR())
            print('done')
        tar.close()
    else:
        raise Exception('file is of wrong type (is \'{is_type}\')!'.format(is_type=filetype))
    print('  moving \'{src}\' -> \'{dest}\'... '.format(src=extracted_dir_name, dest=library), end = '')
    sys.stdout.flush()
    if os.path.exists(join(common.SRCDIR(), library)):
        print('not necessary (already exists)')
    else:
        shutil.move(join(common.SRCDIR(), extracted_dir_name), join(common.SRCDIR(), library))
        print('done')
# def download_library

# main
print('reading \'{filename}\': '.format(filename=filename), end='')
config = ConfigParser.ConfigParser()
try:
    config.readfp(open(filename))
except:
    raise Exception('Could not open \'{filename}\' with configparser!'.format(filename=filename))
libraries=config.sections()
if len(libraries) == 0:
    print(' no external libraries specified')
    exit
else:
    for library in libraries:
        print(library + ' ', end='')
    print('')

for library in libraries:
    print(library + ':')
    if not config.has_option(library, 'src'):
        raise Exception('missing \'src=some_url\' in section \'{library]\''.format(library=library))
    download_library(library, config.get(library, 'src'))
