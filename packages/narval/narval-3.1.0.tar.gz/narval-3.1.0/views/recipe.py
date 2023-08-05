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

from cubicweb.selectors import (is_instance, has_related_entities,
                                objectify_selector)
from cubicweb.view import EntityView
from cubicweb.web import uicfg
from cubicweb.web.views import navigation, ibreadcrumbs, tabs, tableview
from cubicweb.web.views.dotgraphview import DotGraphView, DotPropsHandler

from cubes.narval.views import no_robot_index

_pvs = uicfg.primaryview_section
_pvdc = uicfg.primaryview_display_ctrl

# Recipe #######################################################################

_pvs.tag_attribute(('Recipe', 'name'), 'hidden')
_pvs.tag_object_of(('*', 'execution_of', 'Recipe'), 'hidden')

class RecipePrimaryView(tabs.TabbedPrimaryView):
    __select__ = is_instance('Recipe')

    default_tab = _('narval.recipe.tab_config')
    tabs = [default_tab, _('narval.recipe.tab_executions'),
            _('narval.recipe.tab_dotgraph'),
            _('narval.recipe.errors')]

    html_headers = no_robot_index


class RecipeConfigTab(tabs.PrimaryTab):
    __select__ = is_instance('Recipe')
    __regid__ = 'narval.recipe.tab_config'


class RecipeExecutionsTab(EntityView):
    __select__ = (is_instance('Recipe') &
                  has_related_entities('execution_of', 'object'))
    __regid__ = 'narval.recipe.tab_executions'

    html_headers = no_robot_index

    def cell_call(self, row, col):
        rset = self._cw.execute(
            'Any P,PST,PET, PS ORDERBY PST DESC WHERE '
            'P execution_status PS, P execution_of R, '
            'P starttime PST, P endtime PET, '
            'R eid %(r)s', {'r': self.cw_rset[row][col]})
        self.wview('narval.recipe.plans_summary', rset)


class RecipeDotGraphTab(DotGraphView):
    __select__ = is_instance('Recipe')
    __regid__ = 'narval.recipe.tab_dotgraph'

    html_headers = no_robot_index

    def build_visitor(self, entity):
        return RecipeVisitor(entity)

    def build_dotpropshandler(self):
        return RecipePropsHandler(self._cw)


class RecipeVisitor(object):
    def __init__(self, entity):
        self.entity = entity

    def nodes(self):
        for entity in self.entity.reverse_in_recipe:
            entity.complete()
            yield entity.eid, entity

    def edges(self):
        for transition in self.entity.reverse_in_recipe:
            if transition.e_schema != 'RecipeTransition':
                continue
            for incoming in transition.in_steps:
                yield incoming.eid, transition.eid, transition
            for outgoing in transition.out_steps:
                yield transition.eid, outgoing.eid, transition


class RecipePropsHandler(DotPropsHandler):

    def node_properties(self, entity):
        """return default DOT drawing options for a state or transition"""
        props = super(RecipePropsHandler, self).node_properties(entity)
        if entity.e_schema == 'RecipeStep':
            props['style'] = 'filled'
            if entity.reverse_start_step:
                props['fillcolor'] = '#88CC88'
            if entity.reverse_end_step:
                props['fillcolor'] = '#EE8888'
        else:
            # display a simple line
            props['label'] = ''
            props['height'] = 0
        return props


@objectify_selector
def has_errors(cls, req, rset=None, row=0, col=0, **kwargs):
    if not rset:
        return
    recipe = rset.get_entity(0,0)
    if recipe.check_validity():
        return 1
    return 0

class RecipeErrors(EntityView):
    __select__ = is_instance('Recipe') & has_errors()
    __regid__ = 'narval.recipe.errors'

    def cell_call(self, row, col):
        recipe = self.cw_rset.get_entity(row, col)
        errors = recipe.check_validity()
        w = self.w
        _ = self._cw._
        if not errors:
            w(u'<div>%s</div>' % _('no errors'))
            return
        recipe_errors = errors.pop(recipe.eid, None)
        if recipe_errors:
            w(u'<h2>%s</h2>' % _('Recipe errors'))
            for msg in recipe_errors:
                w(u'<div>%s</div>' % msg.render(self._cw))
        if not errors:
            return
        w(u'<h2>%s</h2>' % _('Steps errors'))
        w(u'<table class="listing">')
        w(u'<thead><th>%s</th><th>%s</th></thead>' % (_('step'), _('error')))
        w(u'<tbody>')
        for eid, msgs in sorted(errors.items()):
            w(u'<tr>')
            w(u'<td>')
            step = self._cw.entity_from_eid(eid)
            css_class = ''
            if step.initial_step:
                css_class += ' %s' % _('initial')
            if step.final_step:
                css_class += ' %s' % _('final')
            w(u'<div class="%s">%s</div>' % (css_class, step.view('outofcontext')))
            w(u'</td>')
            w(u'<td>')
            w(', '.join([msg.render(self._cw) for msg in msgs]))
            w(u'</td>')
            w(u'</tr>')
        w(u'</tbody>')
        w(u'</table>')

class RecipePlansSummaryTable(tableview.TableView):
    __select__ = is_instance('Plan')
    __regid__ = 'narval.recipe.plans_summary'

    html_headers = no_robot_index

    def call(self):
        self._cw.add_css('cubes.narval.css')
        _ = self._cw._
        super(RecipePlansSummaryTable, self).call(
            displayfilter=True, paginate=True,
            headers=[_('execution'), _('starttime'), _('endtime')],
            cellvids={0: 'narval.plan.statuscell'})

