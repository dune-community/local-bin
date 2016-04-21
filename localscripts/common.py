#!/usr/bin/env python

from __future__ import print_function, absolute_import, with_statement
import os
import pytest
import types
from os.path import join
import logging
import subprocess
import sys
import itertools
from string import Template
import shlex
from tempfile import NamedTemporaryFile

VERBOSE = len(sys.argv) <= 1
logging.basicConfig()

CONFIG_DEFAULTS = {'cc': 'gcc', 'cxx': 'g++', 'f77': 'gfortran'}


class LocalConfig(object):
    def __init__(self, allow_for_broken_config_opts=False, basedir=None, external_libraries=None):
        # define directories
        self.basedir = basedir or os.path.abspath(join(os.path.dirname(sys.argv[0]), '..', '..'))
        self.install_prefix = os.environ.get('INSTALL_PREFIX', join(self.basedir, 'local'))
        self.srcdir = join(self.install_prefix, 'src')
        try:
            os.makedirs(self.srcdir)
        except OSError as os_error:
            if os_error.errno != os.errno.EEXIST:
                raise os_error

        self.external_libraries_cfg_filename = external_libraries or join(self.basedir, 'external-libraries.cfg')
        self.dune_modules_cfg_filename = join(self.basedir, 'dune-modules.cfg')
        self.demos_cfg_filename = join(self.basedir, 'demos.cfg')

        self.cxx_flags = ''
        self.config_opts_filename = ''
        self.boost_toolsets = {'gcc-{}.{}'.format(i, j): 'gcc' for i, j in itertools.product(range(4, 7), range(10))}
        self.boost_toolsets.update({'icc': 'intel-linux', 'clang': 'clang'})
        self.config_opts = {}
        if allow_for_broken_config_opts:
            try:
                self._parse_config_opts()
            except RuntimeError:
                for i in ('cc', 'cxx', 'f77'):
                    setattr(self, i, CONFIG_DEFAULTS[i])
        else:
            self._parse_config_opts()

    def _parse_config_opts(self):
        # get CC from environment
        self.config_opts = self._get_config_opts(os.environ)

        # then read CC, CXX and F77
        def find_opt(string, default):
            cc = os.environ.get(string)
            if cc is not None:
                return cc
            self.config_opts.get(string, default)

        self.cc = find_opt('CC', default='gcc')
        self.cxx = find_opt('CXX', default='g++')
        self.f77 = find_opt('F77', default='gfortran')

    def _read_opts_file(self, filename):
        # makes sure to throw IOError if file is missing
        open(filename).read()
        env = os.environ.copy()
        # prints only shell variables after sourcing the opts file
        shell_vars = subprocess.check_output('set -o posix ; source {} ; set '.format(filename),
                                             env=env, universal_newlines=True, shell=True, executable='/bin/bash')
        parsed_vars = {}
        for line in shlex.split(shell_vars):
            try:
                sep_idx = line.index('=')
                parsed_vars[line[:sep_idx]] = shlex.split(line[sep_idx+1:])
            except ValueError:
                pass #means we hit IFS or similar in parsed_vars
        return parsed_vars

    def _try_opts(self, env):
        if 'OPTS' in env:
            possibles = (join(self.basedir, env['OPTS']), join(self.basedir, 'config.opts', env['OPTS']))
            for filename in possibles:
                try:
                    return filename, self._read_opts_file(filename)
                except IOError:
                    continue
            raise IOError('Environment defined OPTS not discovered in {}'.format(possibles))
        if 'CC' not in env:
            raise RuntimeError('You either have to set OPTS or CC in order to specify a config.opts file!')
        cc = os.path.basename(env['CC'])
        search_dirs = (self.basedir, join(self.basedir, 'opts'), join(self.basedir, 'config.opts'))
        prefixes = ('config.opts.', '',)
        for filename in (join(dirname, pref + cc) for dirname, pref in
                         itertools.product(search_dirs, prefixes)):
            try:
                return filename, self._read_opts_file(filename)
            except IOError:
                continue
        raise IOError('No suitable opts file for CC {} in anyof {} x {}'.format(cc, search_dirs, prefixes))

    def _get_config_opts(self, env):
        try:
            self.config_opts_filename, config_opts = env['OPTS'], self._read_opts_file(env['OPTS'])
        except (IOError, KeyError):
            self.config_opts_filename, config_opts = self._try_opts(env)

        def set_cxx_flags_from(configure_flags, flag_arg):
            for arg in configure_flags:
                if arg.startswith(flag_arg):
                    cxx_flags = shlex.split(arg[len(flag_arg)+1:].strip().strip('=').strip('\\').strip(), posix=True)
                    cxx_flags = [ii for ii in cxx_flags if ii != '\n']
                    self.cxx_flags = ' '.join(cxx_flags)
                    return
            raise RuntimeError(configure_flags)

        if 'CONFIGURE_FLAGS' in config_opts:
            set_cxx_flags_from(config_opts['CONFIGURE_FLAGS'], flag_arg='CXXFLAGS')
        elif 'CMAKE_FLAGS' in config_opts:
            set_cxx_flags_from(config_opts['CMAKE_FLAGS'], flag_arg='-DCMAKE_CXX_FLAGS')
        else:
            raise RuntimeError('found neither CMAKE_FLAGS nor CONFIGURE_FLAGS in opts file {}\n{}'.format(
                self.config_opts_filename, config_opts))
        return config_opts

    def make_env(self):
        env = os.environ.copy()
        env['CC'] = self.cc
        env['CXX'] = self.cxx
        env['F77'] = self.f77
        env['CXXFLAGS'] = self.cxx_flags
        env['basedir'] = self.basedir
        env['BASEDIR'] = self.basedir
        env['SRCDIR'] = self.srcdir
        env['INSTALL_PREFIX'] = self.install_prefix
        env['BOOST_TOOLSET'] = self.boost_toolsets.get(os.path.basename(self.cc), 'gcc')
        env['BOOST_ROOT'] = env['INSTALL_PREFIX']
        path = join(self.install_prefix, 'bin')
        if 'PATH' in env:
            path += ':' + env['PATH']
        env['PATH'] = path
        ld_library_path = join(self.install_prefix, 'lib')
        if 'LD_LIBRARY_PATH' in env:
            ld_library_path += ':' + env['LD_LIBRARY_PATH']
        env['LD_LIBRARY_PATH'] = ld_library_path
        pkg_config_path = join(self.install_prefix, 'lib', 'pkgconfig')
        if 'PKG_CONFIG_PATH' in env:
            pkg_config_path += ':' + env['PKG_CONFIG_PATH']
        env['PKG_CONFIG_PATH'] = pkg_config_path
        return env

    def command_sep(self):
        return '\n'


def _prep_build_command(verbose, local_config, build_command):
    build_command = build_command.lstrip().rstrip()
    if not (build_command[0] == '\'' and build_command[-1] == '\''):
        if verbose:
            print('build commands have to be of the form \'command_1\' (is {cmd}), aborting!'.format(cmd=build_command))
    build_command = Template(build_command[1:-1].lstrip().rstrip())
    subst = local_config.make_env()
    build_command = build_command.safe_substitute(subst)
    return build_command


class LineEndStreamhandler(logging.StreamHandler):

    def emit(self, record):
        # noinspection PyBroadException
        try:
            msg = self.format(record)
            if not hasattr(types, "UnicodeType"):  #if no unicode support...
                self.stream.write(msg)
            else:
                try:
                    if getattr(self.stream, 'encoding', None) is not None:
                        self.stream.write(msg.encode(self.stream.encoding))
                    else:
                        self.stream.write(msg)
                except UnicodeError:
                    self.stream.write(msg.encode("UTF-8"))
            try:
                end = record.end
            except AttributeError:
                end = os.linesep
            self.stream.write(end)
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)


def get_logger(name=__file__):
    log = logging.getLogger(name)
    log_lvl = logging.DEBUG if VERBOSE else logging.INFO

    handler = LineEndStreamhandler(stream=sys.stdout)
    myFormatter = logging.Formatter('%(message)s')
    handler.setFormatter(myFormatter)
    log.handlers = [handler]
    log.setLevel(log_lvl)
    # monkey patch to allow passing end=str as a kwarg like the print_function does
    old_log = log._log

    def mlog(_, msg, *args, **kwargs):
        if 'end' in kwargs:
            kwargs['extra'] = {'end': kwargs['end']}
            del kwargs['end']
        old_log(msg, *args, **kwargs)
    log._log = types.MethodType(mlog, log)
    log.propagate = False
    return log


def process_commands(local_config, commands, cwd):
    ret = 0
    log = get_logger('process_commands')
    for build_command in commands.split(local_config.command_sep()):
        build_command = _prep_build_command(VERBOSE, local_config, build_command)
        log.debug(BraceMessage('  calling \'{build_command}\':', build_command=build_command))
        with open(os.devnull, 'wb') as devnull:
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


class BraceMessage(object):
    def __init__(self, fmt, *args, **kwargs):
        self.fmt = fmt
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        return self.fmt.format(*self.args, **self.kwargs)


TESTDATA_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'testdata'))
CONFIG_DIR = os.path.join(TESTDATA_DIR, 'config.opts')

@pytest.fixture(params=[os.path.join(CONFIG_DIR, fn)
                        for fn in os.listdir(CONFIG_DIR) if os.path.isfile(os.path.join(CONFIG_DIR, fn))])
def config_filename(request):
    print('Checking {}'.format(request.param))
    return request.param


def mk_config(*args, **kwargs):
    return LocalConfig(basedir=TESTDATA_DIR, *args, **kwargs)


def test_shipped_configs(config_filename):
    os.environ['OPTS'] = config_filename
    os.environ['INSTALL_PREFIX'] = '/tmp'
    cfg = mk_config()
    assert cfg.config_opts_filename == config_filename


def test_missing():
    os.environ['INSTALL_PREFIX'] = '/tmp'

    os.environ['OPTS'] = 'nosuch.opts'
    with pytest.raises(IOError) as err:
        mk_config()
    assert 'Environment defined OPTS not discovered' in str(err.value)

    with NamedTemporaryFile(dir=TESTDATA_DIR, mode='wt') as tmp:
        tmp.write('CF=;;')
        os.environ['OPTS'] = tmp.name
        cfg = mk_config(allow_for_broken_config_opts=True)
        assert cfg.cxx == 'g++' and cfg.f77 == 'gfortran' and cfg.cc == 'gcc'
        assert cfg.cxx_flags == ''

    del os.environ['OPTS']
    with pytest.raises(RuntimeError) as err:
        mk_config()
    assert 'You either have to set OPTS or CC in order to specify a config.opts file' in str(err.value)

    os.environ['CC'] = 'nosuch.compiler'
    with pytest.raises(IOError) as err:
        mk_config()
    assert 'No suitable opts file for CC' in str(err.value)



