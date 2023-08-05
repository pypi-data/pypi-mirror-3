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

from cubicweb.selectors import is_instance, none_rset
from cubicweb.web.views import tableview

from cubes.narval.views import no_robot_index

class PlanSummaryTable(tableview.TableView):
    __regid__ = 'narval.plan.summarytable'
    __select__ = is_instance('Plan') | none_rset()

    html_headers = no_robot_index
    title = _('Narval plans')
    category = 'startupview'

    def call(self, showpe=True):
        #self._cw.add_css('cubes.apycot.css')
        _ = self._cw._
        if self.cw_rset is None:
            assert showpe
            self.cw_rset = self._cw.execute(
                'Any P,PR,P,PST,PET, PS,PO ORDERBY PST DESC WHERE '
                'P execution_of PR, P execution_status PS, P options PO, '
                'P starttime PST, P endtime PET')
            self.w('<h1>%s</h1>' % _(self.title))
            if not self.cw_rset:
                self.w(_('no plans'))
                return
        headers = [_('Plan'), _('Recipe'),
                   _('starttime'), _('endtime')]
        cellvids = {0: 'narval.plan.statuscell',
                    2: 'narval.plan.optionscell'}
        super(PlanSummaryTable, self).call(displayfilter=True, paginate=True,
                                           headers=headers, cellvids=cellvids)

