#!/usr/bin/env python

from __future__ import print_function
import ConfigParser
import subprocess
import sys

import common

filename = common.dune_modules_cfg_filename

# read config opts
print('reading \'{filename}\''.format(filename=filename.split('/')[-1]), end='')
config = ConfigParser.ConfigParser()
try:
    config.readfp(open(filename))
except:
    print(': not possible', end='')
    pass
#    raise Exception('Could not open \'{filename}\' with configparser!'.format(filename=filename))
# extract all commands
commands = []
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
                                + ' {a_}').format(config_opts=common.config_opts_filename(),
                                                 dune_module=dune_module,
                                                 a_=a_))
    else:
        for a_ in all_.split():
            commands.append('./dune-common/bin/dunecontrol --opts={config_opts} {a_}'.format(config_opts=common.config_opts_filename(),
                                                                                             a_=a_))
else:
    commands.append('./dune-common/bin/dunecontrol --opts={config_opts} all'.
                    format(config_opts=common.config_opts_filename()))
# execute all commands
print(', will be calling:')
for command in commands:
    print('  ' + command)
for command in commands:
    print('calling ' + command + ':')
    ret = subprocess.call(command,
                          shell=True,
                          env=common.env(),
                          cwd=common.BASEDIR(),
                          stdout=sys.stdout,
                          stderr=sys.stderr)
    if ret != 0:
        sys.exit(1)
