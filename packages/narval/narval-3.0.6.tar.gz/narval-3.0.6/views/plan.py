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

from logilab.mtconverter import xml_escape
from logilab.common.tasksqueue import REVERSE_PRIORITY

from cubicweb import tags, view
from cubicweb.selectors import is_instance, match_kwargs
from cubicweb.web import uicfg
from cubicweb.web.views import (baseviews, tabs, tableview,
                                navigation, ibreadcrumbs)

from cubes.narval.views import no_robot_index


_pvs = uicfg.primaryview_section
_pvdc = uicfg.primaryview_display_ctrl

_pvs.tag_attribute(('Plan', 'execution_log'), 'relations')
_pvdc.tag_attribute(('Plan', 'execution_log'), {'vid': 'narval.formated_log'})
_pvdc.tag_attribute(('Plan', 'priority',), {'vid': 'tasksqueue.priority'})
_pvs.tag_subject_of(('Plan', 'execution_of', '*'), 'hidden')


class PlanPrimaryView(tabs.TabbedPrimaryView):
    __select__ = is_instance('Plan')

    default_tab = _('narval.plan.tab_setup')
    tabs = [default_tab]
    html_headers = no_robot_index

    def render_entity_title(self, entity):
        #self._cw.add_css('cubes.apycot.css')
        title = self._cw._('Execution of %(recipe)s') % {
            'recipe': entity.recipe.view('outofcontext')}
        self.w('<h1>%s</h1>' % title)


class PlanConfigTab(tabs.PrimaryTab):
    __regid__ = _('narval.plan.tab_setup')
    __select__ = is_instance('Plan')

    html_headers = no_robot_index


class PlanBreadCrumbTextView(ibreadcrumbs.BreadCrumbTextView):
    __select__ = is_instance('Plan')
    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        starttime = entity.printable_value('starttime')
        if starttime:
            self.w(starttime)
        else:
            self.w(entity.printable_value('execution_status'))

class PlanIBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    __select__ = is_instance('Plan')

    def parent_entity(self):
        """hierarchy, used for breadcrumbs"""
        return self.entity.recipe


class PlanIPrevNextAdapter(navigation.IPrevNextAdapter):
    __select__ = is_instance('Plan')

    def previous_entity(self):
        rset = self._cw.execute(
            'Any X,R ORDERBY X DESC LIMIT 1 '
            'WHERE X is Plan, X execution_of R, R eid %(c)s, '
            'X eid < %(x)s',
            {'x': self.entity.eid, 'c': self.entity.recipe.eid})
        if rset:
            return rset.get_entity(0, 0)

    def next_entity(self):
        rset = self._cw.execute(
            'Any X,R ORDERBY X ASC LIMIT 1 '
            'WHERE X is Plan, X execution_of R, R eid %(c)s, '
            'X eid > %(x)s',
            {'x': self.entity.eid, 'c': self.entity.recipe.eid})
        if rset:
            return rset.get_entity(0, 0)


class PriorityView(view.EntityView):
    __regid__ = 'tasksqueue.priority'
    __select__ = is_instance('Plan') & match_kwargs('rtype')

    def cell_call(self, row, col, rtype, **kwargs):
        entity = self.cw_rset.get_entity(row, col)
        value = getattr(entity, rtype)
        if value:
            priority = REVERSE_PRIORITY[value]
            self.w(u'<span class="priority_%s">' % priority)
            self.w(xml_escape(self._cw._(priority)))
            self.w(u'</span>')


class PlanStatusCell(view.EntityView):
    __regid__ = 'narval.plan.statuscell'
    __select__ = is_instance('Plan')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w(tags.a(entity.printable_value('execution_status'),
                      href=entity.absolute_url(),
                      klass="global status_%s" % entity.execution_status,
                      title=self._cw._('see detailed execution report')))


class PlanOptionsCell(view.EntityView):
    __regid__ = 'narval.plan.optionscell'
    __select__ = is_instance('Plan')

    def cell_call(self, row, col, **kwargs):
        entity = self.cw_rset.get_entity(row, col)
        if entity.options:
            self.w(xml_escape('; '.join(entity.options.splitlines())))


class QueuedStatusView(view.View):
    __regid__ = 'narval.plan.botstatus'

    def cell_call(self, row, col):
        if self.cw_rset[row][col]:
            self.w(u'<div class="validPlan">\u2714</div>')
        else:
            self.w(u'<div class="invalidPlan">\u2717</div>')
