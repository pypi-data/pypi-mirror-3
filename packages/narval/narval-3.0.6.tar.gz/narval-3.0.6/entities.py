# Copyright (c) 2000-2010 LOGILAB S.A. (Paris, FRANCE).
# Copyright (c) 2004-2005 DoCoMo Euro-Labs GmbH (Munich, Germany).
#
# http://www.docomolab-euro.com/ -- mailto:tarlano@docomolab-euro.com
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
"""cubicweb-narval entity's classes"""

__docformat__ = "restructuredtext en"

from logilab.common.graph import get_cycles
from logilab.common.textutils import (TIME_UNITS, BYTE_UNITS,
                                      apply_units, text_to_dict)

from cubicweb.entities import AnyEntity, fetch_config
from cubes.narval.utils import Msg, Cyclemsg

class Recipe(AnyEntity):
    __regid__ = 'Recipe'
    __permissions__ = ('execute',)
    rest_attr = 'name'
    fetch_attrs, fetch_order = fetch_config(['name', 'start_step', 'end_step'])

    @property
    def elements(self):
        return self.reverse_in_recipe

    @property
    def transitions(self):
        return [e for e in self.reverse_in_recipe
                if isinstance(e, RecipeTransition)]

    @property
    def steps(self):
        return [e for e in self.reverse_in_recipe
                if isinstance(e, RecipeStep)]

    @property
    def initial_step(self):
        return self.start_step and self.start_step[0] or None

    @property
    def final_step(self):
        return self.end_step and self.end_step[0] or None

    def may_be_started(self):
        return self._permissions_are_fulfiled() and not self.check_validity()

    def _permissions_are_fulfiled(self):
        if self._cw.user.matching_groups(('managers', 'narval')):
            return True
        rset = self._cw.execute('CWPermission P WHERE R require_permission P, P name "execute", '
                                'P require_group G, U in_group G, U eid %(u)s, R eid %(r)s',
                                {'u': self._cw.user.eid, 'r': self.eid})
        return bool(rset)

    def add_step(self, type, target, initial=False, final=False, **kwargs):
        step = self._cw.create_entity('RecipeStep', type=type, target=target,
                                       in_recipe=self, **kwargs)
        if initial:
            self.set_relations(start_step=step)
        if final:
            self.set_relations(end_step=step)
        return step

    def add_transition(self, insteps, outsteps, on_error=False, **kwargs):
        if on_error:
            kwargs['in_error_steps'] = insteps
        return self._cw.create_entity('RecipeTransition', in_recipe=self,
                                      in_steps=insteps, out_steps=outsteps,
                                      **kwargs)

    def get_cycles(self):
        if not self.initial_step:
            return ()
        graph = {}
        def collect(step):
            if step.eid in graph:
                return
            for trans in step.reverse_in_steps:
                for outstep in trans.out_steps:
                    graph.setdefault(step.eid, []).append(outstep.eid)
                    collect(outstep)
        collect(self.initial_step)
        return get_cycles(graph)

    def check_validity(self):
        """ check :
         * start/end
         * untied steps
         * cycles
         * nonexistent action/recette
         """
        _ = self._cw._
        if not self.elements:
            return {self.eid: [Msg(_('no elements'))]}
        errors = {}
        if self.initial_step is None:
            errors.setdefault(self.eid, []).append(Msg(_('initial step is missing')))
        if self.final_step is None:
            errors.setdefault(self.eid, []).append(Msg(_('final step is missing')))
        # untied steps
        for step in self.steps:
            step_errors = step.check_validity()
            errors.update(step_errors)
        # cycles
        for cycle in self.get_cycles():
            errors.setdefault(self.eid, []).append(Cyclemsg(cycle))
        return errors


class Plan(AnyEntity):
    __regid__ = 'Plan'
    fetch_attrs, fetch_order = fetch_config(['execution_status', 'execution_of',
                                             'priority', 'options'])

    def dc_title(self):
        return self._cw._('execution of %s') % self.recipe.dc_title()

    @property
    def recipe(self):
        return self.execution_of[0]

    def options_dict(self):
        if self.options:
            options = text_to_dict(self.options)
            for option in (u'max-cpu-time', u'max-reprieve', u'max-time'):
                if option in options:
                    options[option] = apply_units(options[option], TIME_UNITS)
            if u'max-memory' in options:
                options[u'max-memory'] = apply_units(options[u'max-memory'],
                                                     BYTE_UNITS)
        return {}


class RecipeTransition(AnyEntity):
    __regid__ = 'RecipeTransition'
    fetch_attrs, fetch_order = fetch_config(['priority'])

    @property
    def on_error(self):
        return set(x.eid for x in self.in_error_steps)


class RecipeStep(AnyEntity):
    __regid__ = 'RecipeStep'
    fetch_attrs, fetch_order = fetch_config(['label', 'type', 'target', 'for_each'])


    def dc_title(self):
        if self.label:
            return self.label
        return '%s (%s)' % (self.target, self._cw._(self.type))

    def add_input(self, id, *conditions, **kwargs):
        proto = self._cw.create_entity('RecipeStepInput', id=id,
                                       reverse_takes_input=self,
                                       **kwargs)
        for expr in conditions:
            proto.add_condition(expr)
        return proto

    def add_output(self, id, *conditions, **kwargs):
        proto = self._cw.create_entity('RecipeStepOutput', id=id,
                                       reverse_generates_output=self,
                                       **kwargs)
        for expr in conditions:
            proto.add_condition(expr)
        return proto

    def add_next_step(self, type, target, final=False, **kwargs):
        new_step = self.recipe.add_step(type, target, final=final, **kwargs)
        self.recipe.add_transition(self, new_step)
        return new_step

    @property
    def initial_step(self):
        return self.reverse_start_step and self.reverse_start_step[0] or None

    @property
    def final_step(self):
        return self.reverse_end_step and self.reverse_end_step[0] or None

    @property
    def recipe(self):
        return self.in_recipe and self.in_recipe[0] or None

    def check_validity(self):
        _ = self._cw._
        errors = {}
        if self.type:
            if self.type == 'recipe':
                rset = self._cw.execute('Recipe R WHERE R name %(n)s', {'n': self.target})
                if not rset:
                    msg = _('target recipe does not exist')
                    errors.setdefault(self.eid, []).append(Msg(msg))
            # XXX if type==action, we should ask to the bot
        if self.initial_step and self.final_step:
            return errors
        if self.initial_step and not self.reverse_in_steps:
            msg = _('this step must have at least one outgoing transition')
            return {self.eid: [Msg(msg)]}
        if self.final_step and not self.reverse_out_steps:
            msg = _('this step must have at least one incoming transition')
            return {self.eid: [Msg(msg)]}
        if not self.reverse_in_steps and not self.final_step:
            msg = _('this step must have at least one incoming transition')
            errors.setdefault(self.eid, []).append(Msg(msg))
        if not self.reverse_out_steps and not self.initial_step:
            msg = _('this step must have at least one outgoing transition')
            errors.setdefault(self.eid, []).append(Msg(msg))
        return errors


class NarvalPrototypeMixIn(object):

    def add_condition(self, expr):
        self._cw.create_entity('NarvalConditionExpression',
                               expression=expr,
                               reverse_matches_condition=self)


class NarvalConditionExpression(NarvalPrototypeMixIn, AnyEntity):
    __regid__ = 'NarvalConditionExpression'
    fetch_attrs, fetch_order = fetch_config(['expression'])
    @property
    def prototype(self):
        return self.reverse_matches_condition[0]


class RecipeTransitionCondition(NarvalPrototypeMixIn, AnyEntity):
    __regid__ = 'RecipeTransitionCondition'
    fetch_attrs, fetch_order = fetch_config(['use', 'from_context', 'to_context'])


class RecipeStepInput(NarvalPrototypeMixIn, AnyEntity):
    __regid__ = 'RecipeStepInput'
    fetch_attrs, fetch_order = fetch_config(['id', 'use', 'optional',
                                             'from_context', 'to_context'])


class RecipeStepOutput(AnyEntity):
    __regid__ = 'RecipeStepOutput'
    fetch_attrs, fetch_order = fetch_config(['id', 'optional', 'outdates'])
