#!/usr/bin/env python

from __future__ import print_function
import ConfigParser
import os
from os.path import join
import subprocess
import sys

import common

filename = common.external_libraries_cfg_filename


def build_library(library, config):
    src_dir = join(common.SRCDIR(), library)
    if not os.path.isdir(src_dir):
        raise Exception('\'{path}\' is not a directory (did you forget to run \'./local/bin/download_external_libraries.py\'?)!'.format(path=src_dir))
    build_commands = config.get(library, 'build')
    abort = True
    if config.has_option(library, 'abort'):
        abort = config.getboolean(library, 'abort')
    for build_command in build_commands.split(','):
        build_command = build_command.lstrip().rstrip()
        if not (build_command[0] == '\'' and build_command[-1] == '\''):
            raise Exception('build commands have to be of the form \'command_1\' (is {cmd})!'.format(cmd=build_command))
        build_command = build_command[1:-1].lstrip().rstrip()
        build_command = build_command.replace('$BASEDIR', '{BASEDIR}'.format(BASEDIR=common.BASEDIR()))
        build_command = build_command.replace('$SRCDIR', '{SRCDIR}'.format(SRCDIR=common.SRCDIR()))
        build_command = build_command.replace('$CXXFLAGS', '\'{CXXFLAGS}\''.format(CXXFLAGS=common.CXXFLAGS()))
        build_command = build_command.replace('$CC', '{CC}'.format(CC=common.CC()))
        build_command = build_command.replace('$CXX', '{CXX}'.format(CXX=common.CXX()))
        build_command = build_command.replace('$F77', '{F77}'.format(F77=common.F77()))
        print('  calling \'{build_command}\':'.format(build_command=build_command))
        ret = subprocess.call(build_command,
                              shell=True,
                              env=common.env(),
                              cwd=src_dir,
                              stdout=sys.stdout,
                              stderr=sys.stderr)
        if ret != 0 and abort:
            break
# build_library

# main
print('reading \'{filename}\': '.format(filename=filename.split('/')[-1]), end='')
config = ConfigParser.ConfigParser()
try:
    config.readfp(open(filename))
except:
    raise Exception('Could not open \'{filename}\' with configparser!'.format(filename=filename))
libraries = config.sections()
if len(libraries) == 0:
    print(' no external libraries specified')
    exit
else:
    for library in libraries:
        print(library + ' ', end='')
    print('')

for library in libraries:
    print(library + ':')
    if not config.has_option(library, 'build'):
        raise Exception('missing \'build=\'list_of\', \'some_commands\'\' in section \'[{library}]\''.format(library=library))
    build_library(library, config)
