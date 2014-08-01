#!/usr/bin/env python

from __future__ import print_function
import os
from os.path import join
import logging
import subprocess
import sys

VERBOSE = len(sys.argv) <= 1
logging.basicConfig()

class LocalConfig(object):
    def __init__(self):
        # define directories
        self.basedir = os.path.abspath(join(os.path.dirname(sys.argv[0]), '..', '..'))
        self.srcdir = join(self.basedir, 'local', 'src')
        try:
            os.mkdir(self.srcdir)
        except OSError as os_error:
            if os_error.errno != 17:
                raise os_error

        self.external_libraries_cfg_filename = join(self.basedir, 'external-libraries.cfg')
        self.dune_modules_cfg_filename = join(self.basedir, 'dune-modules.cfg')
        self.demos_cfg_filename = join(self.basedir, 'demos.cfg')

        self.cc = ''
        self.cxx = ''
        self.f77 = ''
        self.cxx_flags = ''
        self.config_opts_filename = ''
        self.boost_toolsets = {'gcc-4.{}'.format(i): 'gcc' for i in range(4, 18)}
        self.boost_toolsets.update({'icc': 'intel-linux', 'clang': 'clang'})
        self._parse_config_opts()

    def _parse_config_opts(self):
        # get CC from environment
        if not os.environ.has_key('CC'):
            raise Exception('ERROR: missing environment variable \'CC\'!')
        self.config_opts = self._get_config_opts(os.environ['CC'])

        # then read CC, CXX and F77
        def find_that_is_not_one_of(string, rest):
            exceptional_msg = 'ERROR: no suitable \'{}=some_exe\' found in \'{}\'!'.format(string,
                                                                                           self.config_opts_filename)
            # print('config_opts = \'{config_opts}\''.format(config_opts=config_opts))
            after = self.config_opts[self.config_opts.index(string) + len(string):]
            # print('after = \'{after}\''.format(after=after))
            if after[0] != '=' or after[1] == ' ':
                raise Exception(exceptional_msg)
            possible = after[1:].split('=')[0].split()[0]
            if possible in rest:
                raise Exception(exceptional_msg)
            else:
                return possible

        self.cc = find_that_is_not_one_of('CC', ['CXX', 'F77', 'CXXFLAGS'])
        self.cxx = find_that_is_not_one_of('CXX', ['CC', 'F77', 'CXXFLAGS'])
        self.f77 = find_that_is_not_one_of('F77', ['CC', 'CXX', 'CXXFLAGS'])

    def _get_config_opts(self, env_CC):
        def _try_opts():
            _config_opts_filename = 'config.opts.' + os.path.basename(env_CC)
            for dir_name in (self.basedir, os.path.join(self.basedir, 'opts')):
                # read corresponding config.opts
                filename = join(dir_name, _config_opts_filename)
                try:
                    return filename, open(filename).read()
                except IOError:
                    continue
            else:
                raise IOError('ERROR: could not read from \'{}\'!'.format(_config_opts_filename))

        self.config_opts_filename, config_opts = _try_opts()
        config_opts = config_opts.replace('CONFIGURE_FLAGS=', '').replace('"', '').replace('\\', '').replace('\n', ' ')

        # read and remove CXXFLAGS first
        self.cxx_flags = config_opts.split('CXXFLAGS')[1]
        config_opts = config_opts.split('CXXFLAGS')[0]
        if self.cxx_flags[0] != '=':
            raise Exception(
                'ERROR: no suitable \'CXXFLAGS=\'some_flags\'\' found in \'{}\'!'.format(self.config_opts_filename))
        self.cxx_flags = self.cxx_flags[1:]
        if self.cxx_flags[0] == '\'':
            self.cxx_flags = self.cxx_flags[1:]
            tmp = self.cxx_flags
            self.cxx_flags = self.cxx_flags[:self.cxx_flags.index('\'')]
            config_opts += ' ' + tmp[tmp.index('\'') + 1:]
        else:
            tmp = self.cxx_flags
            self.cxx_flags = self.cxx_flags.split(' ')[0]
            config_opts += ' ' + tmp[tmp.index(self.cxx_flags) + len(self.cxx_flags):]
        return config_opts

    def make_env(self):
        env = os.environ.copy()
        env['CC'] = self.cc
        env['CXX'] = self.cxx
        env['F77'] = self.f77
        env['CXXFLAGS'] = self.cxx_flags
        env['basedir'] = self.basedir
        env['SRCDIR'] = self.srcdir
        env['BOOST_TOOLSET'] = self.boost_toolsets.get(os.path.basename(self.cc), 'gcc')
        env['BOOST_ROOT'] = join(self.basedir, 'local')
        path = join(self.basedir, 'local', 'bin')
        if 'PATH' in env:
            path += ':' + env['PATH']
        env['PATH'] = path
        ld_library_path = join(self.basedir, 'local', 'lib')
        if 'LD_LIBRARY_PATH' in env:
            ld_library_path += ':' + env['LD_LIBRARY_PATH']
        env['LD_LIBRARY_PATH'] = ld_library_path
        pkg_config_path = join(self.basedir, 'local', 'lib', 'pkgconfig')
        if 'PKG_CONFIG_PATH' in env:
            pkg_config_path += ':' + env['PKG_CONFIG_PATH']
        env['PKG_CONFIG_PATH'] = pkg_config_path
        return env

    def command_sep(self):
        return ','


def _prep_build_command(verbose, local_config, build_command):
    build_command = build_command.lstrip().rstrip()
    if not (build_command[0] == '\'' and build_command[-1] == '\''):
        if verbose:
            print('build commands have to be of the form \'command_1\' (is {cmd}), aborting!'.format(cmd=build_command))

    build_command = build_command[1:-1].lstrip().rstrip()
    build_command = build_command.replace('$BASEDIR', '{BASEDIR}'.format(BASEDIR=local_config.basedir))
    build_command = build_command.replace('$SRCDIR', '{SRCDIR}'.format(SRCDIR=local_config.srcdir))
    build_command = build_command.replace('$CXXFLAGS', '\'{CXXFLAGS}\''.format(CXXFLAGS=local_config.cxx_flags))
    build_command = build_command.replace('$CC', '{CC}'.format(CC=local_config.cc))
    build_command = build_command.replace('$CXX', '{CXX}'.format(CXX=local_config.cxx))
    build_command = build_command.replace('$F77', '{F77}'.format(F77=local_config.f77))
    return build_command


def get_logger(name=__file__):
    log = logging.getLogger(name)
    log_lvl = logging.DEBUG if VERBOSE else logging.INFO
    log.setLevel(log_lvl)
    return log


def process_commands(local_config, commands, cwd):
    ret = 0
    log = get_logger('process_commands')
    for build_command in commands.split(local_config.command_sep()):
        build_command = _prep_build_command(VERBOSE, local_config, build_command)
        log.debug('  calling \'{build_command}\':'.format(build_command=build_command))
        with open(os.devnull, "w") as devnull:
            err = sys.stderr if VERBOSE else devnull
            out = sys.stdout if VERBOSE else devnull
            ret += subprocess.call(build_command,
                                   shell=True,
                                   env=local_config.make_env(),
                                   cwd=cwd,
                                   stdout=out,
                                   stderr=err)
        if ret != 0:
            return not bool(ret)
    return not bool(ret)