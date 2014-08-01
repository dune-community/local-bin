#!/usr/bin/env python2.7

from __future__ import print_function
import ConfigParser
import subprocess
import sys
import os


import common

log = common.get_logger('dune-modules.build')
VERBOSE = common.VERBOSE

if __name__ == '__main__':
    local_config = common.LocalConfig()
    filename = local_config.dune_modules_cfg_filename
    # read config opts
    if VERBOSE:
        print('reading \'{filename}\''.format(filename=filename.split('/')[-1]), end='')
    config = ConfigParser.ConfigParser()
    try:
        config.readfp(open(filename))
    except IOError:
        if VERBOSE:
            print(': does not exist, calling duncontrol')
        ret = subprocess.call('./dune-common/bin/dunecontrol --opts={} all'.format(local_config.config_opts_filename),
                              shell=True,
                              env=local_config.make_env(),
                              cwd=local_config.basedir,
                              stdout=sys.stdout,
                              stderr=sys.stderr)
        sys.exit(ret)

    # extract all commands
    commands = []
    short_commands = []
    if 'general' in config.sections():
        all_ = 'all'
        if config.has_option('general', 'all'):
            all_ = config.get('general', 'all')
            assert(len(all_) > 0)
        if config.has_option('general', 'order'):
            dune_modules = config.get('general', 'order')
            assert(len(dune_modules) > 0)
            for dune_module in dune_modules.split():
                local_all = all_
                if config.has_section(dune_module) and config.has_option(dune_module, 'all'):
                    local_all = config.get(dune_module, 'all')
                    assert(len(local_all) > 0)
                for a_ in local_all.split():
                    commands.append(('./dune-common/bin/dunecontrol'
                                    + ' --opts={config_opts}'
                                    + ' --only={dune_module}'
                                    + ' {a_}').format(config_opts=local_config.config_opts_filename,
                                                    dune_module=dune_module,
                                                    a_=a_))
                    short_commands.append(('{dune_module}:' + ' {a_}').format(dune_module=dune_module,
                                                                            a_=a_))
        else:
            for a_ in all_.split():
                commands.append('./dune-common/bin/dunecontrol --opts={config_opts} {a_}'.format(config_opts=local_config.config_opts_filename,
                                                                                                a_=a_))
    else:
        commands.append('./dune-common/bin/dunecontrol --opts={config_opts} all'.
                        format(config_opts=local_config.config_opts_filename))
    # execute all commands
    if VERBOSE:
        print(', will be calling:')
        for command in commands:
            print('  ' + command)
    ret = 0

    # TODO use common.process_commands?
    for command, short_command in zip(commands, short_commands):
        ret = 1
        if VERBOSE:
            print('calling ' + command + ':')
            ret = subprocess.call(command,
                                shell=True,
                                env=local_config.make_env(),
                                cwd=local_config.basedir,
                                stdout=sys.stdout,
                                stderr=sys.stderr)
        else:
            print('  ' + short_command + '... ', end='')
            sys.stdout.flush()
            with open(os.devnull, "w") as devnull:
                ret = subprocess.call(command,
                                    shell=True,
                                    env=local_config.make_env(),
                                    cwd=local_config.basedir,
                                    stdout=devnull,
                                    stderr=devnull)
            if ret == 0:
                print('done')
            else:
                print('failed')
        if ret != 0:
            sys.exit(1)

    sys.exit(ret)
