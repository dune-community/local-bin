#!/usr/bin/env python2.7

from __future__ import print_function
import ConfigParser
import os
from os.path import join
import subprocess
import sys

import common

filename = common.demos_cfg_filename


verbose = True
if len(sys.argv) > 1:
    verbose = False


def build_demo(demo, build_commands):
    demo_dir = join(common.BASEDIR(), 'demos')
    try:
        os.mkdir(demo_dir)
    except OSError, os_error:
        if os_error.errno != 17:
            raise os_error
    ret = 0
    for build_command in build_commands.split(','):
        build_command = build_command.lstrip().rstrip()
        if not (build_command[0] == '\'' and build_command[-1] == '\''):
            if verbose:
                print('build commands have to be of the form \'command_1\' (is {cmd}), aborting!'.format(cmd=build_command))
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
                                   cwd=demo_dir,
                                   stdout=sys.stdout,
                                   stderr=sys.stderr)
        else:
            with open(os.devnull, "w") as devnull:
                ret += subprocess.call(build_command,
                                       shell=True,
                                       env=common.env(),
                                       cwd=demo_dir,
                                       stdout=devnull,
                                       stderr=devnull)
        if ret != 0:
            return not bool(ret)
    return not bool(ret)

# main
if verbose:
    print('reading \'{filename}\': '.format(filename=filename.split('/')[-1]), end='')
config = ConfigParser.ConfigParser()
try:
    config.readfp(open(filename))
except:
    if verbose:
        print('nothing to do (does not exist)')
    pass
demos = config.sections()
if len(demos) == 0:
    print('nothing to do (no demos specified)')
    exit
else:
    for demo in demos:
        if verbose:
            print(demo + ' ', end='')
    if verbose:
        print('')

reports = []
failure = 0
for demo in demos:
    if verbose:
        print(demo + ':')
    else:
        print('  ' + demo + '... ', end='')
        sys.stdout.flush()
    reports.append(demo + ':')
    if not config.has_option(demo, 'build'):
        if verbose:
            print('missing \'build=\'list_of\', \'some_commands\'\' in section \'[{demo}]\', aborting!'.format(demo=demo))
        else:
            print('failed')
    else:
        demo_is_built = build_demo(demo, config.get(demo, 'build'))
        if demo_is_built:
            if not verbose:
                print('done')
            if config.has_option(demo, 'msg'):
                msg = config.get(demo, 'msg').lstrip().rstrip()
                if not (msg[0] == '\'' and msg[-1] == '\''):
                    if verbose:
                        print('WARNING: \'msg\' should be of the form \'some example message\'!')
                    reports.append('  {msg}'.format(msg=msg))
                    if not verbose:
                        print('   \'' + msg + '\'')
                else:
                    reports.append('  {msg}'.format(msg=msg[1:-1]))
                    if not verbose:
                        print('   \'' + msg[1:-1] + '\'')
            else:
                reports.append('  built successfuly')
        else:
            failure += 1
            if verbose:
                reports.append('  build failed')
            else:
                print('failed')
if verbose:
    if len(reports) > 0:
        print('===========================================================')
        print('the following demos are available, run \'. PATH.sh\' first:')
        print('===========================================================')
        for report in reports:
            print(report)
else:
    if failure > 0:
        print('  call \'./local/bin/build_demos.py\' manually to examine errors')
sys.exit(failure)
