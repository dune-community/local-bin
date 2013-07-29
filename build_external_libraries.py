#!/usr/bin/env python2.7

from __future__ import print_function
import ConfigParser
import os
from os.path import join
import subprocess
import sys

import common

filename = common.external_libraries_cfg_filename

verbose = True
if len(sys.argv) > 1:
    verbose = False


def build_library(library, config):
    no_dir = False
    if config.has_option(library, 'only_build'):
        no_dir = bool(config.get(library, 'only_build'))
    if no_dir:
        src_dir = common.SRCDIR()
    else:
        src_dir = join(common.SRCDIR(), library)
    if not os.path.isdir(src_dir):
        raise Exception('\'{path}\' is not a directory (did you forget to run \'./local/bin/download_external_libraries.py\'?)!'.format(path=src_dir))
    build_commands = config.get(library, 'build')
#    abort = True
#    if config.has_option(library, 'abort'):
#        abort = config.getboolean(library, 'abort')
    ret = 0
    for build_command in build_commands.split(','):
        build_command = build_command.lstrip().rstrip()
        if not (build_command[0] == '\'' and build_command[-1] == '\''):
            if verbose:
                ('build commands have to be of the form \'command_1\' (is {cmd}), aborting!'.format(cmd=build_command))
                return False
        build_command = build_command[1:-1].lstrip().rstrip()
        build_command = build_command.replace('$BASEDIR', '{BASEDIR}'.format(BASEDIR=common.BASEDIR()))
        build_command = build_command.replace('$SRCDIR', '{SRCDIR}'.format(SRCDIR=common.SRCDIR()))
        build_command = build_command.replace('$CXXFLAGS', '\'{CXXFLAGS}\''.format(CXXFLAGS=common.CXXFLAGS()))
        build_command = build_command.replace('$CC', '{CC}'.format(CC=common.CC()))
        build_command = build_command.replace('$CXX', '{CXX}'.format(CXX=common.CXX()))
        build_command = build_command.replace('$F77', '{F77}'.format(F77=common.F77()))
        if verbose:
            print('  calling \'{build_command}\':'.format(build_command=build_command))
            ret += subprocess.call(build_command,
                                  shell=True,
                                  env=common.env(),
                                  cwd=src_dir,
                                  stdout=sys.stdout,
                                  stderr=sys.stderr)
        else:
            with open(os.devnull, "w") as devnull:
                ret += subprocess.call(build_command,
                                      shell=True,
                                      env=common.env(),
                                      cwd=src_dir,
                                      stdout=devnull,
                                      stderr=devnull)
        if ret != 0:
            return not bool(ret)
    return not bool(ret)
# build_library

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
    print(' no external libraries specified')
    exit
else:
    for library in libraries:
        if verbose:
            print(library + ' ', end='')
    if verbose:
        print('')

reports = []
failure = 0
for library in libraries:
    if not verbose:
        print('  ' + library + '... ', end='')
        sys.stdout.flush()
    success = False
    if not config.has_option(library, 'build'):
        if verbose:
            print('missing \'build=\'list_of\', \'some_commands\'\' in section \'[{library}]\', aborting!'.format(library=library))
    else:
        success = build_library(library, config)
    if success:
        if not verbose:
            print('done')
        else:
            reports.append(library + ': succeeded')
    else:
        if not verbose:
            failure += 1
            print('failed')
        else:
            reports.append(library + ': failed')

if verbose:
    if len(reports) > 0:
        print('================================================')
        print('tried to build the following external libraries:')
        print('================================================')
        for report in reports:
            print(report)
else:
    if failure > 0:
        print('  call \'./local/bin/build_external_libraries.py\' manually to examine errors')
