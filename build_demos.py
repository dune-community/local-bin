#!/usr/bin/env python

from __future__ import print_function
import ConfigParser
import os
from os.path import join
import subprocess
import sys

import common

filename = common.demos_cfg_filename


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
            raise Exception('build commands have to be of the form \'command_1\' (is {cmd})!'.format(cmd=build_command))
        build_command = build_command[1:-1].lstrip().rstrip()
        build_command = build_command.replace('$BASEDIR', '{BASEDIR}'.format(BASEDIR=common.BASEDIR()))
        build_command = build_command.replace('$SRCDIR', '{SRCDIR}'.format(SRCDIR=common.SRCDIR()))
        build_command = build_command.replace('$CXXFLAGS', '\'{CXXFLAGS}\''.format(CXXFLAGS=common.CXXFLAGS()))
        build_command = build_command.replace('$CC', '{CC}'.format(CC=common.CC()))
        build_command = build_command.replace('$CXX', '{CXX}'.format(CXX=common.CXX()))
        build_command = build_command.replace('$F77', '{F77}'.format(F77=common.F77()))
        print('  calling \'{build_command}\':'.format(build_command=build_command))
        ret += subprocess.call(build_command,
                               shell=True,
                               env=common.env(),
                               cwd=demo_dir,
                               stdout=sys.stdout,
                               stderr=sys.stderr)
        if ret != 0:
            return not bool (ret)
    return not bool(ret)
# build_library

# main
print('reading \'{filename}\': '.format(filename=filename.split('/')[-1]), end='')
config = ConfigParser.ConfigParser()
try:
    config.readfp(open(filename))
except:
    print('nothing to do (does not exist)')
    pass
demos = config.sections()
if len(demos) == 0:
    print('nothing to do (no demos specified)')
    exit
else:
    for demo in demos:
        print(demo + ' ', end='')
    print('')

reports = []
for demo in demos:
    print(demo + ':')
    reports.append(demo + ':')
    if not config.has_option(demo, 'build'):
        raise Exception('missing \'build=\'list_of\', \'some_commands\'\' in section \'[{demo}]\''.format(demo=demo))
    demo_is_built = build_demo(demo, config.get(demo, 'build'))
    if demo_is_built:
        if config.has_option(demo, 'msg'):
            msg = config.get(demo, 'msg').lstrip().rstrip()
            if not (msg[0] == '\'' and msg[-1] == '\''):
                print('WARNING: \'msg\' should be of the form \'some example message\'!')
                reports.append('  {msg}'.format(msg=msg))
            else:
                reports.append('  {msg}'.format(msg=msg[1:-1]))
        else:
            reports.append('  built successfuly')
    else:
        reports.append('  built failed')
if len(reports) > 0:
    print('===========================================================')
    print('the following demos are available, run \'. PATH.sh\' first:')
    print('===========================================================')
    for report in reports:
        print(report)
