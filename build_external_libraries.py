#!/usr/bin/env python2.7

from __future__ import with_statement

import ConfigParser
import os
from os.path import join
import subprocess
import sys
import logging
import common

filename = common.external_libraries_cfg_filename

verbose = len(sys.argv) <= 1

log = logging.getLogger('external_libraries.build')
log_lvl = logging.DEBUG if verbose else logging.INFO
log.setLevel(log_lvl)

def build_library(library, config):
    no_dir = config.getboolean(library, 'only_build')
    src_dir = common.SRCDIR() if no_dir else join(common.SRCDIR(), library)
    if not os.path.isdir(src_dir):
        raise Exception('\'{path}\' is not a directory (did you forget to run \'./local/bin/download_external_libraries.py\'?)!'.format(path=src_dir))
    build_commands = config.get(library, 'build')
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
        log.debug('  calling \'{build_command}\':'.format(build_command=build_command))
        with open(os.devnull, "w") as devnull:
            err = sys.stderr if verbose else devnull
            out = sys.stdout if verbose else devnull
            ret += subprocess.call(build_command,
                                  shell=True,
                                  env=common.env(),
                                  cwd=src_dir,
                                  stdout=out,
                                  stderr=err)
        if ret != 0:
            return not bool(ret)
    return not bool(ret)
# build_library

# main
log.debug('reading \'{filename}\': '.format(filename=filename.split('/')[-1]))
config = ConfigParser.SafeConfigParser({'only_build': 'False'})
if not os.path.isfile(filename):
    raise Exception('Could not open \'{filename}\' with configparser!'.format(filename=filename))
config.read(filename)
libraries = config.sections()
if len(libraries) == 0:
    raise Exception(' no external libraries specified')
else:
    for library in libraries:
        log.debug(library + ' ')
    log.debug('')

reports = []
failure = 0
for library in libraries:
    log.info('  ' + library + '... ')
    if not config.has_option(library, 'build'):
        raise Exception('missing \'build=\'list_of\', \'some_commands\'\' in section \'[{library}]\', aborting!'.format(library=library))
    success = build_library(library, config)
    if success:
        log.info('done')
        reports.append(library + ': succeeded')
    else:
        failure += 1
        log.info('failed')
        reports.append(library + ': failed')

if verbose:
    if len(reports) > 0:
        log.debug('''
================================================
tried to build the following external libraries:
================================================''')
        for report in reports:
            log.debug(report)
else:
    if failure > 0:
        log.critical('  call \'./local/bin/build_external_libraries.py\' manually to examine errors')
sys.exit(failure)
