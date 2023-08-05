# copyright 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""narval bot configuration"""

__docformat__ = "restructuredtext en"

import os, os.path as osp
import sys
import logging

from logilab.common.configuration import Configuration, Method
from logilab.common.logging_ext import set_log_methods
from logilab.common.pyro_ext import ns_group_and_id
from logilab.common.textutils import splitstrip

from cubicweb import BadConnectionId, ConfigurationError
from cubicweb.dbapi import ProgrammingError
from cubicweb.toolsutils import read_config
from Pyro import errors

_PARENT_DIR = osp.abspath(osp.normpath(osp.join(osp.dirname(__file__), '..')))
if osp.exists(osp.join(_PARENT_DIR, '.hg')):
    MODE = 'dev'
else:
    MODE = 'installed'


class NarvalConfiguration(Configuration):
    options = (
        # main options
        ('plugins',
         {'type' : 'csv',
          'default': MODE == 'dev' and osp.join(_PARENT_DIR, 'plugins')
          or '/var/lib/narval/plugins',
          'help': 'comma separated list of plugins (eg python modules or '
          'directories) that should be loaded at startup. For directories, '
          'all .py file in there will be loaded.',
          'group': 'main', 'level': 2,
          }),

        # process control
        ('threads',
         {'type' : 'int', 'short': 'T',
          'default': 2,
          'help': 'number of plans which may be run in parallel',
          'group': 'process-control', 'level': 2,
          }),
        ('max-cpu-time',
         {'type' : 'time',
          'default': None,
          'help': 'maximum CPU Time in second that may be used to execute a test.',
          'group': 'process-control', 'level': 2,
          }),
        ('max-time',
         {'type' : 'time',
          'default': None,
          'help': 'maximum Real Time in second that may be used to execute a test.',
          'group': 'process-control', 'level': 2,
          }),
        ('max-memory',
         {'type' : 'bytes',
          'default': None,
          'help': 'maximum Memory in bytes the test can allocate.',
          'group': 'process-control', 'level': 2,
          }),
        ('max-reprieve',
         {'type' : 'time',
          'default': 60,
          'help': 'delay in second while the test try to abort nicely (reporting '
          'the error and cleaning up the environement before it\'s killed).',
          'group': 'process-control', 'level': 2,
          }),
        # server control
        ('uid',
         {'type' : 'string',
          'default': None,
          'help': 'if this option is set, use the specified user to start \
the daemon rather than the user running the command',
          'group': 'pyro-server', 'level': 1,
          }),
        ('log-file',
         {'type' : 'string',
          'default': Method('_log_file'),
          'help': 'file where output logs should be written',
          'group': 'pyro-server', 'level': 2,
          }),
       ('log-threshold',
         {'type' : 'string', # XXX use a dedicated type?
          'default': 'DEBUG',
          'help': 'server\'s log level',
          'group': 'pyro-server', 'level': 1,
          }),
        ('host',
         {'type' : 'string',
          'default': None,
          'help': 'host name if not correctly detectable through gethostname. '\
          'You can also specify a port using <host>:<port> notation (will be '\
          'choosen randomly if not set (recommended)).',
          'group': 'pyro-server', 'level': 1,
          }),
        ('pyro-id',
         {'type' : 'string',
          'default': 'narval',
          'help': 'identifier of the narval bot in the pyro name-server.',
          'group': 'pyro-server', 'level': 2,
          }),
        ('pyro-ns-host',
         {'type' : 'string',
          'default': '',
          'help': 'Pyro name server\'s host where the bot is registered. If not '\
          'set, will be detected by a broadcast query. You can also specify a '\
          'port using <host>:<port> notation.',
          'group': 'pyro-server', 'level': 1,
          }),

        )

    def __init__(self):
        Configuration.__init__(self)
        self.load_file_configuration(self.configuration_file)
        self.cnx_infos, self.aliases = connection_infos()

    if MODE == 'dev':
        _default_conf_file = osp.expanduser('~/etc/narval.ini')
        _default_pid_file = '/tmp/narval.pid'
        _default_log_file = '/tmp/narval.log'
    else:
        _default_conf_file = '/etc/narval.ini'
        _default_pid_file = '/var/run/narval/narval.pid'
        _default_log_file = '/var/log/narval/narval.log'

    @property
    def configuration_file(self):
        return os.environ.get('NARVALRC', self._default_conf_file)

    def _pid_file(self):
        return self._default_pid_file

    def _log_file(self):
        return self._default_log_file

    def cnxh(self, cwinstid):
        assert cwinstid
        cwinstid = self.aliases.get(cwinstid, cwinstid)
        return ConnectionHandler(cwinstid, self['pyro-ns-host'],
                                 self.cnx_infos.get(cwinstid, {}))


def _load_plugin(logger, module):
    logger.info('loading extra module %s', module)
    try:
        mod = __import__(module)
        logger.debug('module file imported: %s', mod.__file__)
    except ImportError:
        logger.error('cant import %s', module, exc_info=True)
    except Exception, ex:
        logger.exception('while loading %s: %s', module, ex)

def load_plugins(logger, plugins):
    loaded = set()
    for module in plugins:
        if osp.isdir(module):
            if not module in sys.path:
                sys.path.insert(0, module)
            for fname in os.listdir(module):
                basename, ext = osp.splitext(fname)
                if ext in ('.py', '.pyc', '.pyo', '.pyd') and basename not in loaded:
                    _load_plugin(logger, basename)
                    loaded.add(basename)
        elif module not in loaded:
            _load_plugin(logger, module)
            loaded.add(module)


if MODE == 'dev':
    _DEFAULT_SOURCES_FILE = osp.expanduser('~/etc/narval-cw-sources.ini')
else:
    _DEFAULT_SOURCES_FILE = '/etc/narval-cw-sources.ini'
_CW_SOURCES_FILE = os.environ.get('NARVALSOURCES', _DEFAULT_SOURCES_FILE)

def connection_infos():
    aliases = {}
    if osp.exists(_CW_SOURCES_FILE):
        cnxinfos = read_config(_CW_SOURCES_FILE)
        for cwinstid, instinfo in cnxinfos.items():
            nsgroup, instid = ns_group_and_id(cwinstid, defaultnsgroup=None)
            if instinfo.get('pyro-ns-group', nsgroup) != nsgroup:
                raise ConfigurationError('conflicting values for pyro-ns-group')
            nsgroup = instinfo.get('pyro-ns-group', nsgroup or 'cubicweb')
            if nsgroup[0] != ':':
                nsgroup = ':' + nsgroup
            qinstid = '%s.%s' % (nsgroup, instid)
            if 'aliases' in instinfo:
                for alias in splitstrip(instinfo['aliases']):
                    aliasnsgroup, aliasinstid = ns_group_and_id(
                        alias, defaultnsgroup=nsgroup)
                    qalias = '%s.%s' % (aliasnsgroup, aliasinstid)
                    assert qalias not in aliases, 'duplicated alias %s' % qalias
                    aliases[qalias] = qinstid
            if cwinstid != qinstid:
                cnxinfos[qinstid] = cnxinfos.pop(cwinstid)
    else:
        cnxinfos = {}
    return cnxinfos, aliases


class ConnectionHandler(object):
    """handle connection to a cubicweb repository"""

    def __init__(self, cwinstid, nshost=None, cnxinfo=None):
        if not cwinstid:
            raise ConfigurationError('you must specify main cubicweb instance '
                                     'identifier in the configuration file or using '
                                     'the --cw-inst-id option')
        if cnxinfo is None:
            cnxinfo = connection_infos()[0].get(cwinstid, {})
        nsgroup, instid = ns_group_and_id(cwinstid, defaultnsgroup=None)
        self.cwinstid = instid
        self.cnxinfo = cnxinfo
        if nsgroup:
            if cnxinfo.get('pyro-ns-group', nsgroup) != nsgroup:
                raise ConfigurationError('conflicting values for pyro-ns-group')
            cnxinfo['pyro-ns-group'] = nsgroup
        else:
            nsgroup = ':cubicweb'
        self.cwqinstid = '%s.%s' % (nsgroup, self.cwinstid)
        if nshost and not 'pyro-ns-host' in cnxinfo:
            cnxinfo['pyro-ns-host'] = nshost
        self.cnx = self.cw = self._cu = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def connect(self):
        from cubicweb import AuthenticationError
        from cubicweb.dbapi import connect
        user = self.cnxinfo.get('user', 'narval')
        password = self.cnxinfo.get('password', 'narval0')
        group = self.cnxinfo.get('pyro-ns-group', None)
        host = self.cnxinfo.get('pyro-ns-host', None)
        try:
            logger = logging.getLogger('cubicweb')
            logger.setLevel(logging.ERROR)
            self.cnx = connect(database=self.cwinstid, login=user,
                               password=password, group=group, host=host,
                               initlog=False)
        except AuthenticationError:
            raise
        except Exception, ex:
            self.critical('error while trying to connect to instance %r: %s',
                          self.cwinstid, ex)
            return None
        else:
            self.cnx.load_appobjects(subpath=('entities',))
            # don't get the cursor until load_appobjects has been called
            self.cw = self.cnx.request()
            self._cu = self.cnx.cursor(self.cw)
            return self.cnx

    def pending_plans(self):
        if self.cnx is None and not self.connect():
            raise Exception('can\'t connect to %s; check logs for details.'
                            % (self.cwinstid))
        return self.execute(
            'Any X WHERE X is_instance_of Plan, X execution_status "ready"').entities()

    def plan(self, eid):
        if self.cnx is None and not self.connect():
            raise Exception('can\'t connect to %s; check logs for details.'
                            % (self.cwinstid))
        rset = self.execute('Any X,XO,XS,XP,XR WHERE X eid %(x)s, X options XO,'
                            'X execution_status XS, X priority XP, X execution_of XR',
                            {'x': eid})
        if not rset:
            raise Exception('cant get plan %s in instance %s.'
                            % (eid, self.cwinstid))
        return rset.get_entity(0, 0)

    def execute(self, rql, kwargs=None, reconnect=True):
        try:
            return self._cu.execute(rql, kwargs)
        except (BadConnectionId, errors.PyroError):
            if reconnect and self.connect():
                return self.execute(rql, kwargs, reconnect=False)
            raise

    def commit(self):
        self.cnx.commit()

    def close(self):
        if self.cnx is not None:
            try:
                self.cnx.close()
            except (ProgrammingError, BadConnectionId, errors.PyroError):
                pass

LOGGER = logging.getLogger('narval.cubicweb')
set_log_methods(ConnectionHandler, LOGGER)


def resource_reached(self, exc, context=None):
    """method for logger to handle RessourceError"""
    if isinstance(exc, MemoryError):
        limit = 'memory'
    else:
        limit = exc.limit
    if context is not None:
        msg = '%s resource limit reached, While %s' % (limit, context)
    else:
        msg = '%s resource limit reached' % limit
    self.critical(msg,exc_info=True)
