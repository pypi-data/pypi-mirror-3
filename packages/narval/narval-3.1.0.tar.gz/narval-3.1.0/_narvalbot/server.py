# Copyright (c) 2003-2010 LOGILAB S.A. (Paris, FRANCE).
# http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""Narval bot waiting for pyro connection"""

from __future__ import with_statement

__docformat__ = "restructuredtext en"

import os
import sys
import select
import warnings
import signal
import stat
import logging
from os.path import exists, join, normpath
from subprocess import Popen
from tempfile import TemporaryFile
from threading import Thread, Lock, Timer, currentThread
from datetime import datetime, timedelta

from Pyro import config
# disable multithread support so we can share a connection to the cw
# instlication. Since each commands should be very quickly acheived, this should
# not be a penalty
config.PYRO_MULTITHREADED = False
config.PYRO_STDLOGGING = True
config.PYRO_TRACELEVEL = 3
config.PYRO_TRACEBACK_USER_LEVEL = 3
config.PYRO_DETAILED_TRACEBACK = 1
config.PYRO_STORAGE = '/tmp' # XXX

from logilab.common import tasksqueue, pyro_ext as pyro
from logilab.common.logging_ext import set_log_methods, init_log
from logilab.common.daemon import daemonize, setugid
from logilab.common.configuration import format_option_value

from narvalbot import MODE, NarvalConfiguration, load_plugins, main


class NarvalTask(tasksqueue.Task):

    def __init__(self, cwinstid, plan):
        super(NarvalTask, self).__init__('%s.%s' % (cwinstid, plan.eid),
                                         plan.priority)
        self.cwinstid = cwinstid
        self.planeid = plan.eid
        self.options = plan.options_dict()

    def as_dict(self):
        return {'instanceid': self.cwinstid,
                'eid': self.planeid}

    def run_command(self, config):
        cmd = ['narval', 'run-plan', self.cwinstid, str(self.planeid)]
        for optname, optdef in main.RunPlanCommand.options:
            value = self.options.get(optname, config[optname])
            fvalue = format_option_value(optdef, value)
            if fvalue:
                cmd.append('--'+optname)
                cmd.append(str(fvalue))
        return cmd


class NarvalProcessManager(object):
    def __init__(self, config=None):
        """make the repository available as a PyRO object"""
        self.config = config or NarvalConfiguration()
        #args = self.config.load_command_line_configuration()
        self._queue = tasksqueue.PrioritizedTasksQueue()
        self._quiting = None
        self._running_tasks = set()
        self._lock = Lock()
        # interval of time where plan queued while there is an identical plan
        # running will be ignored
        self._skip_duplicate_time_delta = timedelta(seconds=15) # XXX
        # load plugins if necessary, to get info about them in available_*
        # methods
        if self.config['plugins']:
            load_plugins(self, self.config['plugins'])

    def start(self, cwids=None, debug=False, force=False, pidfile=None):
        config = self.config
        self.cwids = cwids or config.cnx_infos.keys()
        if debug:
            logthreshold = config['log-threshold'] = 'DEBUG'
        else:
            logthreshold = config['log-threshold']
        init_log(debug, logthreshold=logthreshold, logfile=config['log-file'])
        pyro.set_pyro_log_threshold(getattr(logging, logthreshold))
        if force:
            pyro.ns_unregister(config['pyro-id'], defaultnsgroup='narval',
                               nshost=config['pyro-ns-host'])
        self._install_sig_handlers()
        self._daemon = pyro.register_object(self, config['pyro-id'],
                                            defaultnsgroup='narval',
                                            daemonhost=config['host'],
                                            nshost=config['pyro-ns-host'])
        # go ! (don't daemonize in debug mode)
        if not debug and daemonize(pidfile):
            return
        # change process uid
        if config['uid']:
            setugid(config['uid'])
        self._loop()

    def _loop(self, req_timeout=0.5):
        """enter the service loop"""
        # init the process queue
        for cwinstid in self.cwids:
            try:
                with self.config.cnxh(cwinstid) as cnxh:
                    self.info('get pending plan from %s', cwinstid)
                    for plan in cnxh.pending_plans():
                        self._queue_plan(cnxh, plan)
            except Exception, ex:
                self.exception(str(ex))
        # service loop
        try:
            while self._quiting is None:
                try:
                    self._daemon.handleRequests(req_timeout)
                except select.error:
                    continue
                try:
                    self._start_processes()
                except SystemExit:
                    raise
                except Exception, ex:
                    self.exception('error while starting process: %s', ex)
        finally:
            pyro.ns_unregister(self.config['pyro-id'], defaultnsgroup='narval',
                               nshost=self.config['pyro-ns-host'])
            self.info('exit')

    def _quit(self):
        """stop the server"""
        self._quiting = True

    def _install_sig_handlers(self):
        """install signal handlers"""
        self.info('installing signal handlers')
        signal.signal(signal.SIGINT, lambda x, y, s=self: s._quit())
        signal.signal(signal.SIGTERM, lambda x, y, s=self: s._quit())

    # public (pyro) interface #################################################

    def queue_plan(self, cwinstid, planeid):
        """add plan to the process queue"""
        with self.config.cnxh(cwinstid) as cnxh:
            self._queue_plan(cnxh, cnxh.plan(planeid))

    def pending_plans(self, cwinstid=None):
        """return an ordered list of plans pending in the queue, from the lowest
        to the highest priority, and another list of currently running plans.

        When an instance id is specified, the lists may contains some None
        values corresponding to plans from another instance.
        """
        if cwinstid is not None:
            cwinstid = self.config.aliases.get(cwinstid, cwinstid)
        def plan_repr(t):
            if cwinstid is None or t.cwinstid == cwinstid:
                return t.as_dict()
            return None
        return ([plan_repr(t) for t in self._queue],
                [plan_repr(t) for _, t in self._running_tasks])

    def cancel_plan(self, cwinstid, planeid):
        """remove plan with the given identifier from the pending plans queue"""
        tid = '%s.%s' % (cwinstid, planeid)
        self._queue.remove(tid)
        self.info('plan %s cancelled', tid)

    # internal process managements #############################################

    def _queue_plan(self, cnxh, plan):
        self.info('queuing plan %s(%s) from %s', plan.eid, plan.dc_title(),
                  cnxh.cwinstid)
        cwinstid = plan.cw_metainformation()['source']['uri']
        if cwinstid == 'system':
            cwinstid = cnxh.cwqinstid
        else:
            cwinstid = self.config.aliases.get(cwinstid, cwinstid)
        self._queue.put(NarvalTask(cwinstid, plan))

    def _start_processes(self):
        """start pending plans according to available resources"""
        while self._queue.qsize() and len(self._running_tasks) < self.config['threads']:
            self._start_process(self._queue.get())

    def _start_process(self, task):
        """start given task in a separated thread"""
        self.info('start test %s', task.id)
        # start a thread to wait for the end of the child process
        task.starttime = datetime.now()
        thread = Thread(target=self._run_task, args=(task,))
        self._running_tasks.add( (thread, task) )
        thread.start()

    def _run_task(self, task):
        """run the task and remove it from running tasks set once finished"""
        try:
            self._spawn_task_process(task)
        finally:
            self._running_tasks.remove( (currentThread(), task) )
            self.info('task %s finished', task.id)

    def _spawn_task_process(self, task):
        """actually run the task by spawning a subprocess"""
        command = task.run_command(self.config)
        outfile = TemporaryFile(mode='w+', bufsize=0)
        errfile = TemporaryFile(mode='w+', bufsize=0)
        self.info(' '.join(command))
        cmd = Popen(command, bufsize=0, stdout=outfile, stderr=errfile)
        maxtime = task.options.get('max-time', self.config['max-time'])
        if maxtime:
            maxreprieve = task.options.get('max-reprieve',
                                           self.config['max-reprieve'])
            maxtime = maxtime + (maxreprieve or 60) * 1.25
            timer = Timer(maxtime, os.killpg, [cmd.pid, signal.SIGKILL])
            timer.start()
        else:
            timer = None
        cmd.communicate()
        if timer is not None:
            timer.cancel()
        try:
            # kill possibly remaining children
            os.killpg(cmd.pid, signal.SIGKILL)
        except OSError, ex:
            if ex.errno != 3: # XXX replace by symbolic constant
                raise
        for stream in (outfile, errfile):
            stream.seek(0)
        if cmd.returncode:
            self.error('error while running %s', command)
            self.error('`%s` returned with status : %s',
                       ' '.join(command), cmd.returncode)
        # add output to Plan entity and change it's state if necessary
        log = u''
        if os.fstat(errfile.fileno())[stat.ST_SIZE]:
            log += unicode(errfile.read(), 'utf-8', 'replace')
            self.info('***** %s error output', ' '.join(command))
            self.info(log)
        if os.fstat(outfile.fileno())[stat.ST_SIZE]:
            out = unicode(outfile.read(), 'utf-8', 'replace')
            self.info('***** %s standard output', ' '.join(command))
            self.info(out)
            log += out
        with self.config.cnxh(task.cwinstid) as cnxh:
            plan = cnxh.execute('Any X,XS WHERE X eid %(x)s, X execution_status XS',
                                {'x': task.planeid}).get_entity(0, 0)
            kwargs = {}
            if log:
                kwargs['execution_log'] = log
            if plan.execution_status not in ('done', 'failed'):
                kwargs['execution_status'] = u'killed'
            if kwargs:
                plan.set_attributes(**kwargs)
                cnxh.commit()

LOGGER = logging.getLogger('narval.bot')
set_log_methods(NarvalProcessManager, LOGGER)
