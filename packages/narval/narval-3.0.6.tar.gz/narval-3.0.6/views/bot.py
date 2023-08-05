# copyright 2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

__docformat__ = "restructuredtext en"
_ = unicode

from cubicweb import tags
from cubicweb.view import StartupView

from cubes.narval.proxy import bot_proxy


class BotStatusView(StartupView):
    """This view displays pending and running plans when the bot is available,
    otherwise displays error message explaining why the bot is unavailable.
    """
    __regid__ = 'botstatus'
    title = _('Process manager status')

    def call(self):
        req = self._cw
        _ = req._
        self._cw.add_css('cubes.narval.css')
        # bot availability
        if not 'vtitle' in req.form:
            self.w(u'<h1>%s</h1>' % _(self.title))
        self.queueds, self.runnings = [], []
        try:
            bot = bot_proxy(req.vreg.config, req.data)
            self.queueds, self.runnings = bot.pending_plans(req.vreg.config['pyro-instance-id'])
            self.w(u'<p>%s</p>' % _('Bot is up and available.'))
        except Exception, ex:
            msg = _(u'Bot is not available for the following reason:')
            self.w(u'<p>%s %s</p>' % (msg, ex))
        self._running_plans()
        self._not_running_running_plans()
        self._pending_plans()
        self._latest_done_plans()

    def _running_plans(self):
        if self.runnings:
            # Do not specify the status of the plans because it can be outdated
            rset = self._cw.execute('Any P,PS, P, PO WHERE P is_instance_of Plan, '
                                    'P options PO, P starttime PS, P eid IN (%s)'
                                    % ','.join(str(running['eid'])
                                               for running in self.runnings))
        else:
            rset = None
        if rset:
            self.w(u'<h2>%s</h2>' % self._cw._('Running plans (%i)') % len(rset))
            self.wview('table', rset,
                       headers=[self._cw._('Plan_plural'),
                                self._cw._('starttime'), self._cw._('options')],
                       cellvids={2: 'narval.plan.optionscell'})
        else:
            self.w(u'<div>%s</div>' % self._cw._('No running plan.'))

    def _not_running_running_plans(self):
        if self.runnings:
            rset = self._cw.execute('Any P,PS,P, PO WHERE P is_instance_of Plan, '
                                    'P execution_status "running", P options PO, '
                                    'P starttime PS, NOT P eid IN (%s)'
                                    % ','.join(str(running['eid'])
                                               for running in self.runnings))
        else:
            rset = self._cw.execute('Any P,PS,P, PO WHERE P is_instance_of Plan, '
                                    'P execution_status "running", P starttime PS, P options PO')
        if rset:
            self.w(u'<h2>%s</h2>'
                   % self._cw._('Actually not running plans (%i)') % len(rset))
            self.w(u'<p>%s</p>' % self._cw._(
                'Those plans are in the running status but are not actually '
                'being executed. This is usually due to severe error during '
                'execution (such as the engine being killed). You probably '
                'want to delete those plans.'))
            self.wview('table', rset,
                       headers=[self._cw._('Plan_plural'),
                                self._cw._('starttime'), self._cw._('options')],
                       cellvids={1: 'narval.plan.optionscell'})

    def _pending_plans(self):
        # "NOT P eid IN (%s)": plans could be in "ready" state in db
        # whereas they are running in the process manager
        if self.runnings:
            rset = self._cw.execute('Any P, PR, P, NULL, PO WHERE P is_instance_of Plan, '
                                    'P execution_status "ready", P priority PR, P options PO,'
                                    ' NOT P eid IN (%s)'
                                    % ','.join(str(running['eid'])
                                               for running in self.runnings))
        else:
            rset = self._cw.execute('Any P, PR, P, NULL, PO WHERE P is_instance_of Plan, '
                                    'P execution_status "ready", P priority PR, P options PO')
        if rset:
            _ = self._cw._
            self.w(u'<h2>%s</h2>' % _('Pending plans (%i)') % len(rset))
            # append boolean flag telling if the plan is actually queued or not
            queued_eids = set(queued['eid'] for queued in self.queueds)
            for row in rset.rows:
                if row[0] in queued_eids:
                    row[3] = True
                else:
                    row[3] = False
            # now display the table
            self.wview('table', rset,
                       headers=[_('Plan_plural'), _('priority'), _('options'),
                                _('scheduled')],
                       cellvids={2: 'narval.plan.optionscell',
                                 3: 'narval.plan.botstatus'})

    def _latest_done_plans(self):
        rset = self._cw.execute('Any P,PS,PE,P, PO ORDERBY PMD DESC LIMIT 3 WHERE '
                                'P is_instance_of Plan, '
                                'NOT P execution_status IN ("ready", "running"), '
                                'P starttime PS, P endtime PE,'
                                'P options PO, P modification_date PMD')
        if rset:
            self.w(u'<h2>%s</h2>' % self._cw._('Latest plans executed'))
            self.wview('table', rset,
                       headers=[self._cw._('Plan_plural'),
                                self._cw._('starttime'), self._cw._('endtime'),
                                self._cw._('options')],
                       cellvids={3: 'narval.plan.optionscell'})

