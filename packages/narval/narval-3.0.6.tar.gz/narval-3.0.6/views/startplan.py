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
"""cubicweb-narval views/forms/actions/components for web ui"""

from logilab.common.tasksqueue import PRIORITY, REVERSE_PRIORITY, MEDIUM

from cubicweb import ValidationError
from cubicweb.selectors import is_instance, match_user_groups, score_entity
from cubicweb.uilib import domid
from cubicweb.view import EntityView
from cubicweb.web import Redirect
from cubicweb.web import component, formfields as ff, formwidgets as fw
from cubicweb.web.views import forms


class StartPlanForm(forms.EntityFieldsForm):
    __regid__ = 'narval.startplanform'
    __select__ = (match_user_groups('managers', 'staff')
                  & is_instance('Recipe')
                  & score_entity(lambda x: x.may_be_started()))

    form_renderer_id = 'htable'
    form_buttons = [fw.SubmitButton(label=_('start plan'))]

    @property
    def action(self):
        return self.edited_entity.absolute_url(vid='narval.startplan')

    priority = ff.IntField(choices=[(l, unicode(v)) for l, v in PRIORITY.iteritems()],
                           value=unicode(MEDIUM),
                           label=_('execution priority'),
                           sort=False, internationalizable=True)


class StartPlanComponent(component.EntityCtxComponent):
    __regid__ = 'narval.startplanform'
    __select__ = (component.EntityCtxComponent.__select__
                  & StartPlanForm.__select__)
    context = 'navcontentbottom'
    def render(self, w):
        w(u'<h2>%s</h2>' % self._cw._('start plan'))
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        form = self._cw.vreg['forms'].select('narval.startplanform', self._cw,
                                             entity=entity)
        form.render(w=w)


class StartPlanView(EntityView):
    __regid__ = 'narval.startplan'
    __select__ = StartPlanForm.__select__
    plan = None

    def msg_url(self, msg):
        try:
            url = self._cw.build_url(self._cw.form['__redirectpath'],
                                     __message=msg)
        except KeyError:
            if len(self.cw_rset) == 1:
                if self.plan is None:
                    entity = self.cw_rset.get_entity(0, 0)
                    url = entity.absolute_url(tab=domid('narval.recipe.tab_executions'),
                                              __message=msg)
                else:
                    url = self.plan.absolute_url(__message=msg)
            else:
                url = self._cw.build_url('view', __message=msg, vid='botstatus')
        return url

    def call(self, priority=MEDIUM):
        priority = priority or self._cw.form.get('priority', MEDIUM)
        for i in xrange(self.cw_rset.rowcount):
            try:
                self.cell_call(i, 0, priority=priority)
            except ValidationError:
                raise
            except Exception, ex:
                raise Redirect(self.msg_url(unicode(ex)))
        raise Redirect(self.msg_url(self._cw._('plan(s) queued')))

    def cell_call(self, row, col, priority=MEDIUM):
        recipe = self.cw_rset.get_entity(row, col)
        self.plan = self._cw.create_entity('Plan', priority=priority,
                                           execution_of=recipe)
