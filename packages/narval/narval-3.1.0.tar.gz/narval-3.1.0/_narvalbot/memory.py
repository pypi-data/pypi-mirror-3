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
"""Narval's main memory"""

__docformat__ = "restructuredtext en"

import time
import traceback
import logging

from narvalbot import ConnectionHandler
from narvalbot.plan import Plan
from narvalbot.elements import ErrorElement
from narvalbot.prototype import eval_expression

LOGGER = logging.getLogger('narval.engine')

def mk_time_stamp():
    """return a time stamp

    :rtype: float
    :return: time representation for now
    """
    return time.time()


class Memory(object):
    """narval's main memory, holds a set of elements, derived from
    `narval.public.ALElement`


    :type narval: `narval.engine.Narval`
    :ivar narval: the narval interpreter

    :type elements: dict
    :ivar elements: elements in memory, indexed by their _narval_eid

    :type actions: dict
    :ivar actions:
      _narval_eid of actions (`narval.action.ActionElement`) in memory, indexed
      by their identity (<group>.<name>)

    :type recipes: dict
    :ivar recipes:
      _narval_eid of recipes (`narval.recipe.RecipeElement`) in memory, indexed
      by their identity (<group>.<name>)

    :type plans: list
    :ivar plans:
      list of plans (`narval.PlanElement`) in memory

    :type _narval_eid_count: int
    :ivar _narval_eid_count: _narval_eid counter

    :type _narval_eid_ref_count: dict
    :ivar _narval_eid_ref_count:
      references counter : keys are _narval_eids and values number of references to the
      element with the given _narval_eid
    """


    def __init__(self, narval, cwinstid):
        self.narval = narval
        self.cnxh = ConnectionHandler(cwinstid, narval.rc.pyro_ns_host)
        self.elements = {}
        #self._aliases = {}
        self.plans = []
        self._narval_eid_count = 1
        self._narval_eid_ref_count = {}
        # proxy for some engine methods
        self.step_change = self.narval.step_change
        self.plan_change = self.narval.plan_change
        self.transition_change = self.narval.transition_change

    def get_element(self, _narval_eid):
        """return the element with the given _narval_eid

        :type _narval_eid: int
        :param _narval_eid: the unique identifier of the element

        :rtype: `narval.public.ALElement` or None
        :return: the element or None if the given _narval_eid is not found
        """
        return self.elements.get(_narval_eid)

    def get_elements(self) :
        """return all elements in memory"""
        return self.elements.values()

    def get_recipe(self, name):
        """return the recipe with the given name"""
        rset = self.cnxh.execute('Recipe X WHERE X name %(name)s', {'name': name})
        if not rset:
            raise Exception('No such recipe %s' % name)
        return rset.get_entity(0, 0)

    # memory manipulation methods ##############################################

    def add_elements(self, elements):
        """add the given elements list to the memory

        :type elements: list
        :param elements: list of element to add in memory
        """
        map(self.add_element, elements)

    def add_element(self, element):
        """add an element to memory

        if the element has already an _narval_eid, just increment its reference counter
        else, (ie yet in memory) assign unique id to the element (_narval_eid) and
        append it to memory.

        :type element: `narval.public.ALElement`
        :param element: the element to add in memory

        :rtype: tuple
        :return: the _narval_eid of the element and the element itself
        """
        for attr in ('_narval_outdated', '_narval_eid', '_narval_tags'):
            if not hasattr(element, attr):
                setattr(element, attr, None)
        if element._narval_eid:
            _narval_eid = element._narval_eid
            if _narval_eid in self._narval_eid_ref_count.keys():
                self._narval_eid_ref_count[_narval_eid] += 1
            else:
                self._narval_eid_ref_count[_narval_eid] = 1
        else :
            # assign new _narval_eid to element
            element._narval_eid = _narval_eid = self._narval_eid_count
            self._narval_eid_count += 1
            self._narval_eid_ref_count[_narval_eid] = 1
            element.timestamp = mk_time_stamp()
            # do some caching processing
            self.elements[_narval_eid] = element
            if isinstance(element, Plan):
                self.plans.append(element)
            element.memory = self
            if hasattr(element, 'added_to_narval_memory'):
                element.added_to_narval_memory(self)
            # element added to memory: fire event.
            LOGGER.info('element %s added to memory with id %s', element, _narval_eid)
            self.narval.memory_change('add', element)
            # this new element may trigger a transition. propagate.
            for plan in self.plans:
                plan.element_change(element)

    def replace_element(self, old_element, new_element):
        """replace an element in memory

        :type old_element: `narval.public.ALElement`
        :param old_element: the element that should be replaced

        :type new_element: `narval.public.ALElement`
        :param new_element: the new element
        """
        new_element._narval_eid = old_element._narval_eid
        new_element.memory = self
        self.elements[old_element._narval_eid] = new_element
        if isinstance(old_element, Plan):
            self.plans.remove(old_element)
        elif isinstance(old_element, RecipeElement):
            del self.recipes[old_element.get_identity()]
        elif isinstance(old_element, ActionElement):
            del self.actions[old_element.get_identity()]
        if isinstance(new_element, Plan):
            self.plans.append(new_element)
        elif isinstance(new_element, RecipeElement):
            self.recipes[new_element.get_identity()] = new_element
        elif isinstance(new_element, ActionElement):
            self.actions[new_element.get_identity()] = new_element
        self.narval.memory_change('replace', new_element, old_element)
        # FIXME: this new element may trigger a transition. propagate ?

    def remove_element(self, element):
        """remove an element from memory

        persistent or outdated elements are actually not removed

        :type element: `narval.public.ALElement`
        :param element: the element that should be removed
        """
        if element._narval_outdated:
            clear_tags(element)
            self.narval.memory_change('remove', element)
            del self.elements[element._narval_eid]
            if isinstance(element, Plan):
                self.plans.remove(element)
                element.cleanup()
            elif isinstance(element, RecipeElement):
                del self.recipes[element.get_identity()]
            elif isinstance(element, ActionElement):
                del self.actions[element.get_identity()]
            del element

    def remove_element_by_id(self, _narval_eid):
        """remove the element with the given _narval_eid from the memory

        :type _narval_eid: int
        :param _narval_eid: the identifier of the element to remove
        """
        try:
            self.remove_element(self.elements[_narval_eid])
        except KeyError :
            LOGGER.warning('no element with _narval_eid %s in memory',
                           _narval_eid)

    def delete_ref_to_element(self, element):
        """decrement the reference counter for the given element

        :type element: `narval.public.ALElement`
        :param element: element that should be "decrefed"
        """
        _narval_eid = element._narval_eid
        self._narval_eid_ref_count[_narval_eid] -= 1
        if self._narval_eid_ref_count[_narval_eid] < 1:
            self.remove_element(element)

    def references_count(self, _narval_eid):
        """return the number of references on the element with the given _narval_eid"""
        return self._narval_eid_ref_count[_narval_eid]

    # memory facilities ########################################################

    def are_active_plans(self) :
        """return true if there are some active plans in memory

        :rtype: bool
        :return:
          flag indicating whether there are or not some active plans in memory
        """
        for plan in self.plans:
            if plan.state not in ('done', 'failed'):
                return True
        return False

    def mk_error(self, msg, err_type=None) :
        """build an error element

        :type msg: str
        :param msg: the error's message

        :type err_type: str or None
        :param err_type: optional error's type

        :rtype: IError
        :return: an error element with the given type / msg
        """
        LOGGER.error('building error (%s): %s' % (err_type, msg))
        return ErrorElement(msg, err_type)

    def mk_traceback_error(self, plan, info) :
        """build an error element from a python traceback

        :type plan: plan
        :param plan: the originate plan of the error

        :type info: tuple
        :param info:
          the result of sys.exc_info(), ie a tuple (ex class, ex instance,
          traceback)

        :rtype: IError
        :return: an error element with the given type / msg
        """
        exc_class, value, tbck = info
        tb_string = traceback.format_exception(exc_class, value, tbck)
        msg = 'error in plan %s: \n%s' % (plan.name, ''.join(tb_string))
        return self.mk_error(msg, exc_class)

    def get_inputs(self, input, context=None):
        """return elements in memory matching the given input prototype, after
        having incremented their reference counter

        :type input: `narval.prototype.InputEntry`
        :param input: the prototype input looking for elements

        :rtype: list
        :return: matching elements
        """
        cands = input.matching_elements(self.elements.values(), context)
        # FIXME (syt): i think the commented code below introduce a memory leak,
        # since elements retreived via this method are also inc-refed when
        # the plan.add_elements call memory.add_elements, while plan.cleanup
        # only remove a single reference
        #
        #for cand in cands:
        #    self._narval_eid_ref_count[cand._narval_eid] += 1
        return cands

    def matching_elements(self, expr):
        """return a generator on elements matching the given expression"""
        for element in self.elements.values():
            if eval_expression(expr, {'elmt': element}):
                yield element

    def transition_wait_time(self, transition, date):
        """schedule a time condition for a transition

        :type transition: `narval.PlanTransition`
        :param transition: the transition with a time condition

        :type date: float
        :param date: the absolute date of the time condition
        """
        self.narval.schedule_event(('time_condition', transition), when=date,
                                   date=True)

    def start_plan(self, cwrecipe, parent_step):
        cwplan = parent_step.plan.cwplan
        self.narval.post_event( ('start_plan', cwplan, parent_step, cwrecipe) )

    # def check_date(self, element):
    #     """see `narval.engine.Narval.check_date`"""
    #     return self.narval.check_date(element)
