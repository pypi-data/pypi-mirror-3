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
"""classes used to handle plan elements (i.e. running recipe)"""
from __future__ import with_statement

__docformat__ = "restructuredtext en"

import sys
import logging
from copy import copy
from datetime import datetime

from logilab.common.proc import RESOURCE_LIMIT_EXCEPTION
from logilab.common.logging_ext import set_log_methods

from narvalbot import prototype as proto, resource_reached
from narvalbot.delegates import RecipeDelegate, ActionDelegate
from narvalbot.prototype import (C_STEP, C_PLAN, C_PARENT, C_MEM,
                                 eval_expression)


class StateMixin(object):
    """a mixin for stateful classes (Plan / PlanStep / PlanTransition)

    :type SDD: dict
    :cvar SDD:
      states diagram definition (each entry is a state, associated with the
      list of possible destination states from it

    :type state: str
    :ivar state: the current state
    """

    SDD = {}
    state = None

    def set_state(self, state):
        """go to the given state

        :type state: str
        :param state: the new state

        :raise AssertionError:
          if the state is not reachable from the current state according to
          the states diagram definition
        """
        # -- precondition
        oldstate = self.state
        if oldstate is None:
            self.state = state
        elif state != oldstate:
            self.info('%s %s -> %s' % (self.readable_name(), oldstate,  state))
            assert state in self.SDD[oldstate], \
                   'Bad state diagram transition in %s %s from %s to %s' % (
                self.__class__.__name__, self.readable_name(), oldstate, state)
            # change state
            self.state = state
            # propagate change
            for func in self._get_callbacks(state):
                try:
                    func(self)
                except RESOURCE_LIMIT_EXCEPTION, exc:
                    context = 'calling state %s callback for %s' % (state, self.readable_name())
                    self.resource_reached(exc, context)
                    raise
                except Exception:
                    self.error('error in %s callback' % state, exc_info=True)

    def _get_callbacks(self, state):
        """return a list of functions / methods that should be called on a
        state change event

        :type state: str
        :param state: the new state

        :raise NotImplementedError: **must be provided by concrete classes**
        """
        raise NotImplementedError()


class PlanTransition(StateMixin):
    """a plan transition is a transition in a running recipe (i.e. a plan)

    :type plan: `Plan`
    :ivar plan: the plan of this transition
    """

    SDD = {'wait-step': ['wait-time', 'wait-condition',
                         'fireable', 'impossible'],
           'wait-time': ['wait-condition', 'fireable', 'impossible'],
           'wait-condition': ['fireable', 'impossible'],
           'fireable': ['fired', 'impossible'],
           'fired': [],
           'impossible': []
           }

    def __init__(self, cwtransition, plan):
        self.id = cwtransition.eid
        self.priority = cwtransition.priority
        self.in_steps, self.out_steps = [], []
        self.on_error = {}
        #self.time_conditions = transition.time_conditions
        self.conditions = []
        for trcond in cwtransition.conditions:
            cond = proto.Condition(trcond.use,
                                   trcond.from_context, trcond.to_context)
            for condition in trcond.matches_condition:
                cond.matches.append(condition.expression)
            self.conditions.append(cond)
            cond.owner = self
        self.justify_table = []
        self.plan = plan
        self.init_conditions = False
        self.prev_steps_elmts  = []
        self.set_state('wait-step')

    def add_in_step(self, step, on_error=False):
        """add an input step

        :type step: `Step`
        :param step: step to add to transition's inputs

        :type on_error: str
        :param on_error:
          one of 'yes' or 'no' indicating whether the input is triggered on error
        """
        self.on_error[step.id] = on_error
        self.in_steps.append(step)

    def readable_name(self):
        return '%s.%s' % (self.plan.readable_name(), self.id)

    def fire(self):
        """fire the transition :
        * add elements going through the transition to the plan
        * set state as 'fired'
        * prepare outgoing steps
        """
        # tag elements that correspond to 'use' conditions
        for condition, list in self.justify_table:
            if condition.use:
                for element in list:
                    proto.tag_element(element, self)
            # add to the plan the elements that justify the transition
            self.plan.add_elements(list)
        # set new state
        self.set_state('fired')
        # run out_steps
        for step in self.out_steps:
            step.prepare(self)


    def get_inputs(self, input, context):
        """select elements by priority, according to the input prototype

        :type input: `narval.prototype.InputEntry`
        :param input: an input prototype

        :rtype: list
        :return:
          the list of elements matching the prototype in this transition or in
          elements from incoming steps
        """
        cands = []
        for cond, list in self.justify_table:
            cands += input.matching_elements(list, context)
        if not cands:
            cands += input.matching_elements(self.prev_steps_elmts, context)
        return cands

    # changelisteners interfaces ###############################################

    def step_change(self, step):
        """a step has changed : verify state of in-steps until the transition
        may be fireable (i.e. all incoming steps are finished (but the
        transition may still have to wait some [time] conditions)

        :type step: `PlanStep`
        :param step: the step who's changed
        """
        if self.state != 'fired':
            for step in self.in_steps:
                state = step.state
                on_error = self.on_error[step.id]
                # if true, transition is impossible
                if ( state in ['history', 'impossible']
                     or (state == 'done' and on_error)
                     or (state in ('error', 'failed', 'killed') and not on_error) ):
                    self.set_state('impossible')
                    break
                # if true, transition may be possible later: wait
                elif ( (state != 'done' and not on_error)
                       or (state not in ('error', 'failed') and on_error) ):
                    self.set_state('wait-step')
                    break
            else:
                # in-steps ok, check time condition
                self._evaluate_time()

    def element_change(self, element):
        """an element has changed : check if the element doesn't satisfy a
        condition

        :type element: `narval.public.ALElement`
        :param element: the element who's changed
        """
        if self.init_conditions and self.state == 'wait-condition':
            self._evaluate_conditions_element(element)
            self._check_conditions()

    def time_condition_match(self):
        """hook called when a time condition is satified : go to the
        'wait-condition' state
        """
        self.set_state('wait-condition')
        self._evaluate_conditions()

    # private ##################################################################

    def _get_callbacks(self, state):
        """return a list of functions / methods that should be called on a
        state change event

        :type state: str
        :param state: the new state

        :rtype: list
        :return: the list of methods that should be called on state change
        """
        result = [self.plan.memory.transition_change,
                  self.plan.transition_change]
        for step in self.out_steps + self.in_steps:
            result.append(step.transition_change)
        return result

    def _evaluate_time(self):
        """verify that **at least one** of the time conditions holds or wait
        for it. If there is no time condition, evaluate elements conditions
        """
        # if self.time_conditions:
        #     dates = []
        #     for time_condition in self.time_conditions :
        #         dates.append(ShallowCalendar(time_condition).get_next_date())
        #     self.set_state('wait-time')
        #     self.plan.memory.transition_wait_time(self, min(dates))
        # else :
        # no time condition, proceed with other conditions
        self._evaluate_conditions()

    def _evaluate_conditions(self):
        """check elements conditions associated with the transition when all
        input steps are done
        """
        # if not initialized yet, do it now
        if not self.init_conditions:
            self._init_conditions()
            self.init_conditions = True
        self._check_conditions()

    def _init_conditions(self):
        """intialize the transition:

        1. fetch elements from incoming steps

        2. try to get valid elements for optional condition, from fetched
           elements or from the plan
        """
        for step in self.in_steps :
            for step_outputs in step.outputs:
                for elmts in step_outputs.values():
                    self.prev_steps_elmts += elmts
        for cond in self.conditions:
            # order elements by priority
            if cond.from_context <= C_STEP:
                cond.match_elements(self.prev_steps_elmts)
                #if len(cond.matching_element):
                #    cond.actual_context = C_STEP
            if not cond.is_satisfied():
                self.plan.get_inputs(cond)

    def _evaluate_conditions_element(self, element):
        """check conditions associated with the transition when all input steps
        are done (_evaluate_conditions done) and when an element is added in
        memory, to check wether this element is satisfying some unsatisfied
        condition

        :type element: `narval.public.ALElement`
        :param element: the element just added to the memory
        """
        # get element context
        if element in self.plan.p_elements:
            e_context = C_PLAN
        else:
            if self.plan.get_parent_level(element) == -1:
                e_context = C_MEM
            else:
                e_context = C_PARENT
        for cond in self.conditions:
            # better context and match ?
            if cond.from_context <= e_context <= cond.to_context:
                cond.match_elements([element])
                cond.actual_context = e_context

    def _check_conditions(self):
        """check that all transition's conditions are satisfied, and set the
        state to fireable when if every thing is ok
        """
        for cond in self.conditions:
            if not cond.is_satisfied():
                # if to_context == C_STEP here, the condition won't ever
                # be satisfied
                if cond.to_context == C_STEP:
                    self.set_state('impossible')
                else:
                    self.set_state('wait-condition')
                break
        else:
            # every condition is satisfied, init table and set fireable
            for cond in self.conditions:
                cands = cond.matching_elmts
                if len(cands) > 0:
                    if not cond.list:
                        # FIXME: this is just a quick fix, used to fix pb with
                        # simultaneous presence elements
                        cands = [cands.pop()]
                    self.justify_table.append((cond, cands))
            self.set_state('fireable')



class PlanStep(StateMixin):
    """a plan step is a step in a running recipe (i.e. a plan)

    :type plan: `Plan`
    :ivar plan: the plan of this transition

    :type delegate: None or `RecipeDelegate` or `ActionDelegate`
    :ivar delegate:
      the `narval.delegates.Delegate` object according to the step's target

    :type outputs: list
    :ivar outputs: elements produced by this step
    """

    SDD = {'todo':       ['ready', 'failed', 'impossible'],
           'ready':      ['running'],
           'running':    ['end', 'failed', 'killed', 'error'],
           'end':        ['done', 'failed', 'error'],
           'done':       ['history'],
           'history':    [],
           'impossible': [],
           'failed':     [],
           'error':      [],
           'killed':      [],
           }
    END_STATES = ('done', 'end', 'error', 'killed', 'failed')
    ERROR_STATES = ('impossible', 'error', 'killed', 'failed')


    def  __init__(self, cwstep, plan):
        self.id = cwstep.eid
        self.label = cwstep.label
        self.type = cwstep.type
        self.target = cwstep.target
        self.foreach = cwstep.for_each
        self.in_transitions, self.out_transitions = [], []
        self.prototype = proto.Prototype()
        for stepinput in cwstep.takes_input:
            inputproto = proto.InputEntry(stepinput.id,
                                          use=stepinput.use,
                                          optional=stepinput.optional,
                                          from_context=stepinput.from_context,
                                          to_context=stepinput.to_context)
            for condition in stepinput.matches_condition:
                inputproto.matches.append(condition.expression)
            self.prototype.add_in_entry(inputproto)
        for stepoutput in cwstep.generates_output:
            outputproto = proto.OutputEntry(stepoutput.id,
                                            optional=stepoutput.optional,
                                            outdates=stepoutput.outdates)
            for condition in stepoutput.matches_condition:
                outputproto.matches.append(condition.expression)
            self.prototype.add_out_entry(outputproto)
        self.arguments = []
        if cwstep.arguments:
            for line in cwstep.arguments.splitlines():
                line = line.strip()
                if line:
                    self.arguments.append(eval_expression(line))
        self.plan = plan
        self.fired_transition = None
        self.outputs = []
        self.output_sets = []
        self.delegate = None
        self.prototype.set_owner(self)
        self.set_state('todo')
        self.nonexecuted_func = None

    def readable_name(self):
        return '%s.%s.%s.%s' % (self.plan.readable_name(),
                                self.type, self.target, self.id)

    # Step element methods #####################################################

    def init(self):
        if not self.delegate :
            self._make_delegate()
        self.delegate.init()

    def prepare(self, transition=None):
        """prepare the step

        :type transition: None or `PlanTransition`
        :param transition: optional transition incoming to this step
        """
        self.fired_transition = transition
        try:
            self.delegate.prepare()
        except RESOURCE_LIMIT_EXCEPTION:
            raise
        except Exception:
            err = self.plan.memory.mk_traceback_error(self.plan, sys.exc_info())
            self.plan.add_elements([err])
            self.set_state('failed')

    def run(self):
        """execute the step"""
        self.delegate.run()

    def end(self):
        """end the step"""
        self.delegate.end()

    def get_inputs(self, input, context):
        """select elements by priority, according to the input prototype

        :type input: `narval.prototype.InputEntry`
        :param input: an input prototype

        :rtype: list
        :return:
          the list of elements matching the prototype in this step's arguments,
          in the incoming transition and / or in the step's plan
        """
        cands = []
        from_ctx, to_ctx = input.from_context, input.to_context
        if self.arguments:
            cands = input.matching_elements(self.arguments, context)
        if self.fired_transition and from_ctx <= C_STEP and to_ctx >= C_STEP:
            cands += self.fired_transition.get_inputs(input, context)
        if not cands and to_ctx > C_STEP:
            cands = self.plan.get_inputs(input, context)
        return cands

    # ChangeListener interface #################################################

    def transition_change(self, transition):
        """transition change hook, called when a transition's status has
        changed

        :type transition: `PlanTransition`
        :param transition: the transition who's status changed
        """
        for transition in self.out_transitions :
            if transition.state == 'fired' and self.state == 'done':
                self.set_state('history')
                break
        else:
            if self.in_transitions :
                for transition in self.in_transitions :
                    if transition.state != 'impossible' :
                        break
                else:
                    self.set_state('impossible')

    def plan_change(self, plan):
        """a child plan has status changed, fix our state accordingly

        :type plan: `Plan`
        :param plan: the changing plan
        """
        # if child plan is end or failed, this step is end or failed
        if plan != self.plan:
            child_plan_state = plan.state
            if  child_plan_state == 'end' :
                self.set_state('end')
            elif child_plan_state == 'failed' :
                self.set_state('failed')

    # private #################################################################

    def _make_delegate(self):
        """create the delegate according to the step's type"""
        type = self.type
        assert type in ('recipe', 'action'), 'Unknown type %s' % type
        if type == 'recipe' :
            self.delegate = RecipeDelegate(self)
        elif type == 'action' :
            self.delegate = ActionDelegate(self)

    def _get_callbacks(self, state):
        """return a list of functions / methods that should be called on a
        state change event

        :type state: str
        :param state: the new state

        :rtype: tuple or list
        :return: the list of methods that should be called on state change
        """
        if state == 'end' :
            # shortcut propagation
            return (self.plan.memory.step_change,)
        # nonexecuted_func *must* be called before triggering plan level callback,
        # else we may have race condition issue.
        result = []
        if state == 'impossible' and self.nonexecuted_func:
            result.append(self.nonexecuted_func)
        result += [self.plan.memory.step_change, self.plan.step_change]
        for transition in self.out_transitions:
            result.append(transition.step_change)
        return result



class Plan(StateMixin):
    """a plan element is a running recipe: RecipeElement + execution context

    :type p_elements: list
    :ivar p_elements: elements in this plan

    :type start_step: `PlanStep`
    :ivar start_step: first step of the recipe

    :type end_step: `PlanStep`
    :ivar end_step: last step of the recipe

    :type parent_plan: `Plan` or None
    :ivar parent_plan: reference to the parent plan if any

    :type parent_step: `PlanStep` or None
    :ivar parent_step: reference to the parent step in the parent plan if any

    :type transitions: dict
    :ivar transitions: dictionary of transitions indexed by their state
    """

    # State diagram Definition ################################################
    SDD = {'ready': ['running'],
           'running': ['fireable', 'failing', 'end'],
           'fireable': ['running', 'failing', 'end'],
           'failing': ['failed-end'],
           'failed-end': ['failed'],
           'failed': [],
           'end': ['done'],
           'done': []
           }

    def __init__(self, cwplan, parent_step=None, recipe=None):
        self.cwplan = cwplan
        if cwplan.options:
            self.options = cwplan.options_dict()
        else:
            self.options = {}
        if recipe is None:
            recipe = cwplan.recipe
            assert parent_step is None, 'parent_step specified while no recipe'
        else:
            assert parent_step, 'recipe specified while no parent_step'
        self.name = recipe.name
        # parent step/plan, when this plan is a recipe step execution
        self.parent_step = parent_step
        self.parent_plan = parent_step and parent_step.plan or None
        # quick link to step/transitions by id
        self.elements = {}
        # all transitions in this plan
        self.transitions = []
        self.transition_states = {'impossible': [],
                                  'wait-step': [], 'wait-condition': [],
                                  'wait-time': [], 'fireable': [],
                                  'history': []}
        # list for elements used by this plan
        self.p_elements = [self]
        # finalizers function, to call at the end of the plan execution,
        # whatever occured
        self.finalizers = []
        # build narval plan from cubicweb recipe
        self.init_from_recipe(recipe)

    def readable_name(self):
        return self.name

    def init_from_recipe(self, cwrecipe):
        self.start_step = self.end_step = None
        # instantiate recipe with dynamic objects
        for cwstep in cwrecipe.steps:
            step = PlanStep(cwstep, self)
            self.elements[step.id] = step
            if cwstep is cwrecipe.initial_step:
                self.start_step = step
            if cwstep is cwrecipe.final_step:
                self.end_step = step
            step.init()
        for cwtrans in cwrecipe.transitions:
            trans = PlanTransition(cwtrans, self)
            self.elements[trans.id] = trans
            self.transitions.append(trans)
            # relink transition to steps
            on_err = cwtrans.on_error
            for ref in cwtrans.in_steps:
                step = self.elements[ref.eid]
                step.out_transitions.append(trans)
                trans.add_in_step(step, ref.eid in on_err)
            for ref in cwtrans.out_steps:
                step = self.elements[ref.eid]
                step.in_transitions.append(trans)
                trans.out_steps.append(step)
                #trans.add_out_step(step)
            assert trans.in_steps and trans.out_steps, (
                trans.in_steps, trans.out_steps)
        assert self.start_step, 'no start step'
        assert self.end_step, 'no end step'
        self._active_steps = {}
        self.set_state('ready')

    def set_state(self, state):
        if self.parent_plan is None:
            kwargs = None
            if state in ('done', 'failed'):
                kwargs = {'endtime':   datetime.now()}
            if kwargs is not None:
                self.cwplan.set_attributes(execution_status=unicode(state),
                                           **kwargs)
                self.memory.cnxh.commit()
        super(Plan, self).set_state(state)

    # Plan element methods #####################################################

    def set_parents(self, parent_plan, parent_step):
        """set the plan parent information

        :type parent_plan: `Plan`
        :param parent_plan: the plan from which is issued this plan

        :type parent_step: `Step`
        :param parent_step: the step from which is issued this plan
        """
        self.parent_plan, self.parent_step = parent_plan, parent_step

    def start(self):
        """start the plan (state change to running and prepare the first step)
        """
        self.set_state('running')
        self.start_step.prepare()

    def run(self):
        """run the plan : fire fireable transitions by priority order"""
        # look for transition of highest priority
        transitions, priority = [], -1
        for t in self.transition_states['fireable'] :
            p = t.priority or 0
            if p > priority:
                transitions = [t]
                priority = p
            elif p == priority:
                transitions.append(t)
        assert len(transitions), "Couldn't select transition to fire: %s" % self.transition_states
        if len(transitions) > 1:
            msg = "Can't choose between several fireable transitions"
            self.memory.mk_error(msg, 'bad recipe')
            for transition in self.transition_states['fireable']:
                transition.set_state('impossible')
        else:
            transition = transitions[0]
            # fire transition
            transition.fire()
            self.transition_states['fireable'] = []

    def end(self):
        """end the plan : set state to 'done' or 'failed' according to the
        current state, and restart the plan if necessary
        """
        # change state
        if self.state == 'end':
            self.set_state('done')
        elif self.state == 'failed-end':
            self.set_state('failed')
        # # if plan has mark 'restart': restart it !
        # if self.restart:
        #     plan = '%s.%s' % (self.group, self.name)
        #     self.memory.start_plan(plan, None, None, [])

    def get_inputs(self, input, context=None):
        """select elements by priority, according to the input prototype

        :type input: `narval.prototype.InputEntry`
        :param input: an input prototype

        :rtype: list
        :return:
          the list of elements matching the prototype in this plan and its
          parent plans, up to the memory
        """
        from_ctx = input.from_context
        to_ctx = input.to_context
        cands = []
        if from_ctx <= C_PLAN and to_ctx >= C_PLAN:
            cands = input.matching_elements(self.p_elements, context)
            #input.actual_context = C_PLAN
        if not cands and to_ctx >= C_PARENT:
            if self.parent_step and from_ctx <= C_PARENT:
                cands = self.parent_step.get_inputs(input, context)
                #input.actual_context = C_PARENT
            elif to_ctx >= C_MEM:
                cands = self.memory.get_inputs(input, context)
                # filter elements generated by this plan
                cands = [elmt for elmt in cands
                         if elmt._narval_from_plan != self._narval_eid]
                #input.actual_context = C_MEM
        return cands

    def get_parent_level(self, element, p_level=0):
        """get the level, starting from <p_level> where the given element has
        been found. -1 means that the element has been found in memory

        :type element: `narval.public.ALElement`
        :param element: the element to search

        :type p_level: int
        :param p_level:
          starting level index, you should usually not give this parameter
          explicitly

        :rtype: int
        :return: the number of parent level where the element has been found
        """
        if element in self.p_elements:
            return p_level
        if self.parent_plan:
            return self.parent_plan.get_parent_level(element, p_level+1)
        # element in memory
        return -1

    def add_elements(self, elements) :
        """add a list of elements to the plan (if element is not already in the
        context of the plan)

        :type elements: list
        :param elements: list of elements to add to the plan
        """
        for elmt in set(elements).difference(set(self.p_elements)):
            self.memory.add_element(elmt)
            self.p_elements.append(elmt)
            # propagate happy news
            self.memory.plan_change(self, 'add', elmt)
        # FIXME (syt): duh ? what's this for ?
        if self.parent_step:
            self.parent_step.outputs.append({1:elements})

    def remove_elements(self, elements):
        """remove a list of elements from the plan

        :type elements: list
        :param elements: list of elements to remove from the plan
        """
        memory = self.memory
        if elements is self.p_elements:
            for elmt in elements:
                # propagate sad news
                memory.plan_change(self, 'remove', elmt)
                # erase
                memory.delete_ref_to_element(elmt)
            self.p_elements = []
        else:
            p_elements = self.p_elements
            for elmt in set(elements).intersection(set(self.p_elements)):
                for i in xrange(len(p_elements)):
                    if p_elements[i] is elmt:
                        p_elements.pop(i)
                        # propagate sad news
                        memory.plan_change(self, 'remove', elmt)
                        # erase
                        memory.delete_ref_to_element(elmt)
                        break
                else:
                    self.warning('element with _narval_eid=%s not in plan' % elmt._narval_eid)

    def cleanup(self):
        """cleanup the plan: remove all elements in the plan's context"""
        self.remove_elements(self.p_elements)

    # change listeners interfaces ##############################################

    def transition_change(self, transition):
        """transition change hook, called when a transition's status has
        changed

        :type transition: `PlanTransition`
        :param transition: the transition who's status changed
        """
        if transition.state == 'fireable' :
            self.transition_states['fireable'].append(transition)
            self.set_state('fireable')

    def step_change(self, step):
        """step change hook, called when a step's status has changed

        :type step: `PlanStep`
        :param step: the step who's status changed
        """
        s = step.state
        if s == 'running':
            self._set_active(step, 'running')
        elif step is self.end_step :
            if s == 'done':
                self.set_state('end')
            elif s in step.ERROR_STATES :
                self.set_state('failing')
        if s in step.END_STATES:
            self._set_finished(step)
        if self.state == 'failing' and not self._active_steps:
            self.set_state('failed-end')

    def element_change(self, element):
        """an element has been modified in memory, propagate information to
        transitions

        :type element: narval.public.ALElement
        :param element: the modified element
        """
        for transition in self.transitions:
            transition.element_change(element)

    def _get_callbacks(self, state):
        """return a list of functions / methods that should be called on a
        state change event

        :type state: str
        :param state: the new state

        :rtype: tuple
        :return: the list of methods that should be called on state change
        """
        if state in ('done', 'failed'):
            result = self.finalizers
        else:
            result = []
        result.append(self.memory.plan_change)
        if self.parent_step:
            result.append(self.parent_step.plan_change)
        return result

    def _set_active(self, step, state):
        """set a step as active (the step should not already be active)

        :type step: `PlanStep`
        :param step: the step to activate

        :type state: str
        :param state: the active state
        """
        if state is not None:
            self.set_state(state)
        assert not self._active_steps.has_key(step)
        self._active_steps[step] = 1

    def _set_finished(self, step):
        """set a step as done (the step should be active)

        :type step: `PlanStep`
        :param step: the step to finish
        """
        if self._active_steps.has_key(step):
            del self._active_steps[step]


# def make_plan(recipe, parent_plan, parent_step):
#     """create a plan from the recipe

#     :rtype: `Plan`
#     :return: a new plan instance for this recipe
#     """
#     plan = Plan(recipe=recipe)
#     plan.set_parents(parent_plan, parent_step)
#     return plan

LOGGER = logging.getLogger('narval.engine')
set_log_methods(Plan, LOGGER)
Plan.resource_reached = resource_reached
set_log_methods(PlanStep, LOGGER)
PlanTransition.resource_reached = resource_reached
set_log_methods(PlanTransition, LOGGER)
PlanStep.resource_reached = resource_reached



proto.EXPR_CONTEXT['Plan'] = Plan
