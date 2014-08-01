#!/usr/bin/env python2.7

from __future__ import print_function
import ConfigParser
import os
from os.path import join
import sys

import common


log = common.get_logger('demos.build')
VERBOSE = common.VERBOSE

def build_demo(build_commands):
    local_config = common.LocalConfig()
    demo_dir = join(local_config.basedir, 'demos')
    try:
        os.mkdir(demo_dir)
    except OSError, os_error:
        if os_error.errno != 17:
            raise os_error
    return common.process_commands(local_config, build_commands, demo_dir)

if __name__ == '__main__':
    local_config = common.LocalConfig()
    filename = local_config.demos_cfg_filename
    if VERBOSE:
        print('reading \'{filename}\': '.format(filename=os.path.basename(filename), end=''))
    config = ConfigParser.ConfigParser()
    try:
        config.readfp(open(filename))
    except IOError:
        if VERBOSE:
            print('nothing to do (does not exist)')
        pass
    demos = config.sections()
    if len(demos) == 0:
        print('nothing to do (no demos specified)')
        sys.exit(0)
    else:
        for demo in demos:
            if VERBOSE:
                print(demo + ' ', end='')
        if VERBOSE:
            print('')

    reports = []
    failure = 0
    for demo in demos:
        if VERBOSE:
            print(demo + ':')
        else:
            print('  ' + demo + '... ', end='')
            sys.stdout.flush()
        reports.append(demo + ':')
        if not config.has_option(demo, 'build'):
            if VERBOSE:
                print('missing \'build=\'list_of\', \'some_commands\'\' in section \'[{demo}]\', aborting!'.format(demo=demo))
            else:
                print('failed')
        else:
            demo_is_built = build_demo(config.get(demo, 'build'))
            if demo_is_built:
                if not VERBOSE:
                    print('done')
                if config.has_option(demo, 'msg'):
                    msg = config.get(demo, 'msg').lstrip().rstrip()
                    if not (msg[0] == '\'' and msg[-1] == '\''):
                        if VERBOSE:
                            print('WARNING: \'msg\' should be of the form \'some example message\'!')
                        reports.append('  {msg}'.format(msg=msg))
                        if not VERBOSE:
                            print('   \'' + msg + '\'')
                    else:
                        reports.append('  {msg}'.format(msg=msg[1:-1]))
                        if not VERBOSE:
                            print('   \'' + msg[1:-1] + '\'')
                else:
                    reports.append('  built successfuly')
            else:
                failure += 1
                if VERBOSE:
                    reports.append('  build failed')
                else:
                    print('failed')
    if VERBOSE:
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
