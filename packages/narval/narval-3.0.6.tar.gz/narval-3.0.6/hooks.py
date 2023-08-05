# copyright 2010-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-narval specific hooks and operations"""

from datetime import datetime, timedelta

from cubicweb import ValidationError
from cubicweb.selectors import is_instance
from cubicweb.server import hook

from cubes.narval import proxy

__docformat__ = "restructuredtext en"


class ServerStartupHook(hook.Hook):
    """add looping task to automatically start tests
    """
    __regid__ = 'narval.startup'
    events = ('server_startup',)
    def __call__(self):
        cleanupdelay = self.repo.config['plan-cleanup-delay']
        if not cleanupdelay:
            return # no auto cleanup
        cleanupinterval = min(60*60*24, cleanupdelay)
        def cleanup_plans(repo, delay=timedelta(seconds=cleanupdelay),
                          now=datetime.now):
            session = repo.internal_session()
            mindate = now() - delay
            try:
                for etype in [repo.schema['Plan']] + repo.schema['Plan'].specialized_by():
                    session.execute('DELETE %s TE WHERE '
                                    'TE modification_date < %%(min)s' % etype,
                                    {'min': mindate})
                    session.commit()
                    session.set_pool()
            finally:
                session.close()
        self.repo.looping_task(cleanupinterval, cleanup_plans, self.repo)


class QueuePlan(hook.DataOperationMixIn, hook.Operation):

    def postcommit_event(self):
        config = self.session.vreg.config
        try:
            bot = proxy.bot_proxy(config, self.session.transaction_data)
        except Exception, ex:
            self.exception('cant contact narval: %s', ex)
            return
        for peid in self.get_data():
            # XXX change plan state created -> ready or queued ?
            try:
                bot.queue_plan(config['pyro-instance-id'], peid)
            except Exception, ex:
                self.exception('error while calling narval: %s', ex)
                break # few chances other will succeed


class AfterPlanCreated(hook.Hook):
    """a plan has been created:
    * check it can actually be started
    * if so, ask the bot to execute it

    XXX do this on the 'execution_of' relation creation
    """
    __regid__ = 'narval.start_plan'
    __select__ = hook.Hook.__select__ & is_instance('Plan')
    events = ('after_add_entity',)

    def __call__(self):
        plan = self.entity
        if not plan.recipe.may_be_started():
            msg = self._cw._('recipe may not be started')
            raise ValidationError(plan.eid, {None: msg})
        QueuePlan.get_instance(self._cw).add_data(self.entity.eid)
