#!/usr/bin/env python

from __future__ import print_function, absolute_import, with_statement

try:
    import ConfigParser as configparser
except ImportError:
    import configparser
import os
from os.path import join
import sys

from localscripts import common

VERBOSE = len(sys.argv) <= 1
log = common.get_logger('external_libraries.build')


def build_library(library, config, local_config):
    no_dir = config.getboolean(library, 'only_build')
    src_dir = local_config.srcdir if no_dir else join(local_config.srcdir, library)
    if not os.path.isdir(src_dir):
        raise Exception(
            '\'{path}\' is not a directory (did you forget to run \'./local/bin/download_external_libraries.py\'?)!'.format(


                path=src_dir))
    build_commands = config.get(library, 'build')
    return common.process_commands(local_config, build_commands, src_dir)


def build_all():
    local_config = common.LocalConfig()
    filename = local_config.external_libraries_cfg_filename
    log.debug('reading \'{}\': '.format(os.path.basename(filename)))
    config = configparser.SafeConfigParser({'only_build': 'False'})
    if not os.path.isfile(filename):
        raise Exception('Could not open \'{}\' with configparser!'.format(filename))
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
            raise Exception(
                'missing \'build=\'list_of\', \'some_commands\'\' in section \'[{library}]\', aborting!'.format(
                    library=library))
        success = build_library(library, config, local_config)
        if success:
            log.info('done')
            reports.append(library + ': succeeded')
        else:
            failure += 1
            log.info('failed')
            reports.append(library + ': failed')

    if len(reports) > 0:
        log.debug('''
    ================================================
    tried to build the following external libraries:
    ================================================''')
        for report in reports:
            log.debug(report)
    if failure > 0:
        log.critical('  call \'./local/bin/build_external_libraries.py\' manually to examine errors')
    return failure
