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
"""Engine is the Narval interpreter"""

__docformat__ = "restructuredtext en"

import logging
import sys
import os
import threading
import traceback
from datetime import datetime
from Queue import Queue, Empty
from functools import wraps

from logilab.common.proc import ResourceController, RESOURCE_LIMIT_EXCEPTION
from logilab.common import logging_ext as lext
from logilab.mtconverter import xml_escape

from narvalbot import memory, plan, load_plugins, resource_reached
from narvalbot.prototype import eval_expression

# def recipe_from_action(action_name, name='??', group='??'):
#     """make and return an anonymous recipe wrapping a single action"""
#     recipe = RecipeElement(name=name, group=group)
#     action_step = Step(id='1', type='action', target=action_name)
#     recipe.add_element(action_step)
#     return recipe

# class BadRecipe(Exception): pass


class HTMLFormatter(logging.Formatter):
    """A formatter for the logging standard module, using format easily
    parseable for later in the web (html) ui.
    """

    def format(self, record):
        msg = record.getMessage()
        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            if msg[-1:] != "\n":
                msg += "\n"
            msg =  record.exc_text
        if isinstance(msg, unicode):
            msg = msg.encode('utf-8')
        return '%s\t%s\t%s\t%s<br/>' % (record.levelno,
                                        record.filename or '',
                                        record.lineno or '',
                                        xml_escape(msg))


class Narval(object):
    """Narval is your pal !

    Terminology:

    * memory: place where Narval stores all it knows of.

    * elements: pieces of information stored in memory

    * recipe: a recipe is an element that describes a sequence of steps,
      separated by transitions. A recipe does nothing. It is knowledge.

    * plan: a plan is an element. A plan is an instance of a recipe. A plan
      actually does something.

    * step: A step can point to an action or a recipe.

    * transition: a transition links steps in a recipe. it can be fired off
      when the associated condition is true.


    Other advantages of Narval are supposed to be:

    * its reflexivity: it can reason about what it is doing, as what it is
      doing are running plans and plans are elements in memory. it can reason
      about what it knows how to do, as recipes are elements in memory. It can
      reason about what it can do as each action is defined as a transformation
      (set of inputs and outputs).

    * it has possibilities for machine learning. because everything is recorded,
      and because of the above flexibility, lots of possibilities are opened for
      automatic learning.


    :type registry: `narval.reader.Registry`
    :ivar registry: the interpreter's registry

    :type alive: bool
    :ivar alive: indicates whether the interpreter is running

    :type quit_when_done: bool
    :ivar quit_when_done:
      indicates whether the interpreter should stop when there is nothing more
      to do

    :type event_queue: Queue
    :ivar event_queue: the event queue, cumulating posted events

    :type step_by_step: bool
    :ivar step_by_step:
      indicates whether the interpreter is running in step by step mode

    :type debug: bool
    :ivar debug: indicates whether the interpreter is running in debug mode

    :type memory: `narval.Memory.Memory`
    :ivar memory: interpreter's main memory

    :type rc: `narval.narvalrc.NarvalRC`
    :ivar rc: interpreter's user configuration
    """

    def __init__(self, cwinstid, config, quit_when_done=True):
        self.rc = config
        self.alive = True
        self.quit_when_done = quit_when_done
        # event queue
        self.event_queue = Queue()
        self.ready_steps = None
        self.ready_plans = None
        # debug
        self.step_by_step = False
        self.step_by_step_semaphore = threading.Semaphore(0)
        # create memory
        self.memory = memory.Memory(self, cwinstid)
        # # create scheduler
        # self.event_scheduler = EventScheduler(self.post_event)
        self.resource_ctrl = ResourceController(config.max_cpu_time,
                                                config.max_time,
                                                config.max_memory,
                                                config.max_reprieve)
        threshold = lext.get_threshold(True, config.log_threshold)
        lext.init_log(True, logthreshold=threshold, fmt=HTMLFormatter())
        logging.getLogger('narval').setLevel(threshold)
        if config.plugins:
            load_plugins(self, config.plugins)

    def run(self):
        """mainloop. Execute plans endlessly unless a debugger says 'wait' or
        an event says 'quit'
        """
        # self.event_scheduler.start()
        # not true during functional tests due to monkey patches
        if threading.currentThread().getName() == 'MainThread':
            self.resource_ctrl.setup_limit()
        try:
            self._run()
        finally:
            if threading.currentThread().getName() == 'MainThread':
                self.resource_ctrl.clean_limit()

    def _run(self):
        while self.alive :
            # done ?
            if self.quit_when_done and self.event_queue.empty() and \
               not self.memory.are_active_plans() :
                self.shutdown()
                continue
            # clear lists
            self.ready_steps = []
            self.ready_plans = []
            # debug
            if self.step_by_step :
                self.step_by_step_semaphore.acquire()
            # wait for event
            try:
                event = self._pop_event()
            except Empty:
                continue
            # catch all error there to avoid killing the event thread
            # (in which case narval won't be able to do anything anymore...)
            try:
                self._process_event(event)
            except SystemExit:
                raise
            except RESOURCE_LIMIT_EXCEPTION, ex:
                self.resource_reached(ex, 'processing event %s' % event)
                raise
            except Exception:
                self.error('Exception raised while processing event %s',
                           event, exc_info=True)
            # fire transitions
            for plan in self.ready_plans:
                self.debug('running plan %s', plan.readable_name())
                try:
                    plan.run()
                except RESOURCE_LIMIT_EXCEPTION:
                    context = 'running plan %s' % plan.readable_name()
                    self.resource_reached(ex, context)
                    # XXX set plan status
                    raise
                except:
                    self.error('Exception raised while running plan %s',
                               plan.readable_name(), exc_info=True)
                    self.memory.plans.remove(plan)
                    # XXX set plan status
            # run steps
            for step in self.ready_steps:
                self.debug('running step %s', step.readable_name())
                try:
                    step.run()
                except RESOURCE_LIMIT_EXCEPTION:
                    self.critical('Resource limit reach')
                    context = 'running step %s' % step.readable_name()
                    self.resource_reached(ex, context)
                    step.set_state('killed')
                    raise
                except:
                    self.error('Exception raised while running step %s',
                               step.readable_name(), exc_info=True)
                    step.set_state('failed')

    def shutdown(self):
        """shutdown the narval interpreter"""
        self.post_event( ('quit',) )

    def quit(self):
        """shutdown all running services to stop the narval interpreter"""
        self.debug("I'm dying: event quit in the queue ! <:~(")
        self.alive = False
        self.memory.cnxh.close()

    def _process_event(self, event):
        """process an engine event

        :type event: tuple
        :param event:
          the event to process, where the first element is the event's type and
          additional elements the event's arguments
        """
        event_type = event[0]
        # start plan ('start_plan', planName,(parent_plan,parent_step),elements)
        if event_type == 'start_plan':
            self._start_plan(*event[1:])
        # plan_end ('planEnd', plan), step_end ('stepEnd', step)
        elif event_type in ('plan_end', 'step_end'):
            event[1].end()
        # add_element ('add_element', element_as_xml)
        elif event_type == 'add_element':
            self.memory.add_element_as_string(event[1])
        # remove_element ('remove_element', _narval_eid)
        elif event_type == 'remove_element':
            self.memory.remove_element_by_id(event[1])
        # replace_element ('replace_element', _narval_eid, element_as_xml)
        elif event_type == 'replace_element':
            self.memory.replace_element_as_string(event[1], event[2])
        # forget element ('forget_element', elmt)
        elif event_type == 'forget_element':
            self.memory.remove_element(event[1])
        # time condition ('time-condition', transition)
        elif event_type == 'time_condition':
            event[1].time_condition_match()
        elif event_type == 'quit':
            self.quit()
        # unknown
        else:
            self.error("unknown event %s", event)

    # debug ####################################################################

    def debug_suspend(self):
        """suspend execution"""
        self.step_by_step = True

    def debug_continue(self):
        """resume execution"""
        self.step_by_step = False
        self.step_by_step_semaphore.release()

    def debug_step_one_step(self):
        """run one execution's step

        :rtype: bool
        :return: the value of the flag indicating if we are in debug mode
        """
        if self.step_by_step:
            self.step_by_step_semaphore.release()
        return self.step_by_step

    # event queue & schedule ###################################################

    def post_event(self, event):
        """add an event to the event queue

        :type event: tuple
        :param event: the event to queue
        """
        self._fire_event('engine', 'post_queue_event',
                         str(id(event)), str(event))
        self.event_queue.put(event)

    def schedule_event(self, event, when=0, period=0, date=False):
        """schedule an event with delay or date, and optional period

        :type event: tuple
        :param event: the event to schedule

        :type when: int or float
        :param when: delay in seconds or absolute date

        :type period: int
        :param period:
          period in seconds, if the event should be automatically restarted
          every X seconds

        :type date: bool
        :param date:
          flag indicating the when is a delay (date == False) or absolute date
          using the epoch representation
        """
        evt = (event, when, period, date)
        self._fire_event('engine', 'post_scheduler_event',
                         str(id(evt)), str(evt))
        self.event_scheduler.schedule_event(evt)

    def _pop_event(self):
        """pop an event to proceed. If not event is available, this method will
        block until an event is posted.

        :rtype: tuple
        :return: the poped event to schedule
        """
        # we have to set a timeout and catch Empty exception in the caller
        # so that we get a chance to get other interruptions
        # this seems to be due to an implementation change in python, making
        # interruptions unvailaible while blocking on Queue.get
        event = self.event_queue.get(timeout=2)
        self._fire_event('engine', 'pop_queue_event', str(id(event)))
        return event

    def _fire_event(self, target, method, *args):
        """record event to the communication service if it's running

        :type target: str
        :param target: the event's target

        :type method: str
        :param method: the event's name

        :param args: arbitrary additional arguements defining the vent
        """
        self.debug('fire event %s %s%s', target, method, args)

    # (Un)Load stuff in memory ################################################

    # def check_date(self, element):
    #     """check load date for action / recipe and reload it if necessary

    #     :type element: `narval.public.ALElement`
    #     :param element: the recipe or action element to check

    #     :rtype: `narval.public.ALElement`
    #     :return: the reloaded element or the given one
    #     """
    #     # FIXME - reload actions broken - customized actions? how to find actions in share
    #     assert isinstance(element, ActionElement) or \
    #            isinstance(element, RecipeElement), element.__class__
    #     if not hasattr(element, 'load_date'):
    #         return element
    #     group, name, path = element.group, element.name, element.from_file
    #     if isinstance(element, ActionElement):
    #         callback = bibal.reload_module
    #         get_f = self.memory.get_actions
    #     else:
    #         callback = bibal.reload_recipe
    #         get_f = self.memory.get_recipes
    #     if os.stat(path)[8] > int(element.load_date):
    #         new_elmts = {}
    #         def add(elmt):
    #             """dummy bibal callback, adding elements to the dictionary"""
    #             new_elmts[elmt.name] = elmt
    #         try:
    #             element = callback(self.registry, add, group, name, path)
    #         except:
    #             log_traceback(LOG_ERR, sys.exc_info())
    #         else:
    #             # update memory elements for this cookbook / module
    #             for elmt in [elmt for elmt in get_f() if elmt.group == group]:
    #                 assert elmt._narval_eid, 'no _narval_eid on element %s'% elmt
    #                 if new_elmts[elmt.name]:
    #                     self.memory.replace_element(elmt, new_elmts[elmt.name])
    #                     del new_elmts[elmt.name]
    #                 else:
    #                     self.memory.remove_element(elmt)
    #             self.memory.add_elements(new_elmts.values())
    #     return element

    # Internal events #########################################################

    def memory_change(self, action, element, old_element=None) :
        """memory change hook, called when an element has been added, removed
        or replaced in memory

        :type action: str
        :param action:
          one of 'add', 'remove', 'replace' according to the change's type

        :type element: `narval.public.ALElement`
        :param element: the element which has changed in the memory

        :type old_element: `narval.public.ALElement`
        :param old_element:
          the element being replaced in case of a 'replace' action, None for
          all other actions
        """
        assert action in ('add', 'remove', 'replace')
        _narval_eid = element._narval_eid
        assert _narval_eid, 'No _narval_eid on memory element %s' % element
        # fire event
        self._fire_event('memory', '%s_element' % action, _narval_eid)
        # # event that calls for a service (listen-on, start plan, activators...)
        # if action == 'add' and IListenOn.providedBy(element):
        #     self.post_event( ('start_rpc', element.type, element.port) )
        # if action != 'remove':
        #     if isinstance(element, StartPlanElement):
        #         self.start_plan(element)
        #     elif isinstance(element, QuitElement):
        #         self.shutdown()
        # if self.protocol_handlers:
        #     h_act = self._find_handler(element, 'activator')
        #     if h_act:
        #         handler = h_act[0]
        #         # got a protocol handler activator element
        #         new_action = 'activate'
        #         if action == 'remove':
        #             new_action = 'deactivate'
        #         self.control_handler_activation(element, new_action, handler)
        #     elif action == 'add':
        #         # not an activator. is it a protocol handler request element ?
        #         h_input =  self._find_handler(element, 'input', None)
        #         if h_input:
        #             _, protocol_handler = h_input
        #             protocol_handler.handle_outgoing(element)


    def step_change(self, step):
        """step change hook, called when a step's status has changed

        :type step: `narval.plan.PlanStep`
        :param step: the step who's status changed
        """
        state = step.state
        self._fire_event('plan', 'step_status_changed', step.plan._narval_eid,
                         step.id, step.state)
        if state == 'ready' :
            self.ready_steps.append(step)
        elif state == 'end' :
            self.post_event( ('step_end', step) )


    def plan_change(self, plan, action='state', element=None):
        """plan change hook, called when plan's status has changed or when an
        element has been added or removed in the plan's memory

        :type plan: `narval.plan.PlanElement`
        :param plan: the changing plan

        :type action: str
        :param action:
          one of 'state', 'add' or 'remove' according to the change's type

        :type element: `narval.public.ALElement`
        :param element:
          the element which has been added or removed in the plan's memory,
          implying action in ('add', 'remove')
        """
        assert action in ('state', 'add', 'remove')
        if action == 'state' :
            state = plan.state
            self._fire_event('plan', 'plan_status_changed',
                             plan._narval_eid, state)
            if state == 'fireable' or state == 'ready':
                self.ready_plans.append(plan)
            elif state in ('end', 'failed-end'):
                self.post_event( ('plan_end', plan) )
            elif state in ('done', 'failed'):
                pass
                # schedule decay
                #self.schedule_event(('forget_element', plan), plan.decay)
        else:
            self._fire_event('plan', 'plan_%s_element' % action,
                             plan._narval_eid, element._narval_eid)


    def transition_change(self, transition):
        """transition change hook, called when a transition's status has
        changed

        :type transition: `narval.plan.PlanTransition`
        :param transition: the transition who's status changed
        """
        self._fire_event('plan', 'transition_status_changed',
                         transition.plan._narval_eid, transition.id, transition.state)

    # Start plan utilities ####################################################

    def _start_plan(self, cwplan, parent_step=None, cwrecipe=None):
        """build a plan from a recipe

        :type element: `StartPlanElement`
        :param element: the element defining the plan to start
        """
        if parent_step is None:
            if not cwplan.execution_status == 'ready':
                raise Exception('plan not in the "ready" state')
            cwplan.set_attributes(starttime=datetime.now())
            self.memory.cnxh.commit()
        # make plan and add it to memory
        narvalplan = plan.Plan(cwplan, parent_step, cwrecipe)
        self.memory.add_element(narvalplan)
        if cwplan.arguments:
            context = []
            for line in cwplan.arguments.splitlines():
                line = line.strip()
                if line:
                    context.append(eval_expression(line))
            narvalplan.add_elements(context)
        self._fire_event('plan', 'instanciate_recipe',
                         cwplan.eid, narvalplan.name, narvalplan._narval_eid)
        narvalplan.start()

    # Memory manipulation (IInteraction) #######################################

    def start_plan_by_eid(self, peid):
        cwplan = self.memory.cnxh.plan(peid)
        self.post_event( ('start_plan', cwplan) )

    # def get_element(self, _narval_eid):
    #     """return the element with the given identifier as an xml string, or
    #     None if no element with the given _narval_eid exists in memory

    #     :type _narval_eid: int
    #     :param _narval_eid: the identifier of the element to retreive

    #     :rtype: str or None
    #     :return: the element with the given identifier as XML if found
    #     """
    #     element = self.memory.get_element(_narval_eid)
    #     if element:
    #         return element.as_xml('UTF-8')
    #     return None

    # def add_element(self, element_xml):
    #     """add a new element as an xml string to the memory

    #     :type element_xml: str
    #     :param element_xml: an XML string representing the element to add
    #     """
    #     self.post_event( ('add_element', element_xml) )

    # def remove_element(self, _narval_eid):
    #     """remove the element with the given _narval_eid from the memory

    #     :type _narval_eid: int
    #     :param _narval_eid: the identifier of the element to remove
    #     """
    #     self.post_event( ('remove_element', _narval_eid) )

    # def replace_element(self, _narval_eid, new_element_xml):
    #     """replace the element with the given _narval_eid by the given new element (as
    #     an xml string)

    #     :type _narval_eid: int
    #     :param _narval_eid: the identifier of the element to replace

    #     :type new_element_xml: str
    #     :param new_element_xml:
    #       an XML string representing the element that will replace the old one
    #     """
    #     self.post_event( ('replace_element', _narval_eid, new_element_xml) )

LOGGER = logging.getLogger('narval.engine')
lext.set_log_methods(Narval, LOGGER)
Narval.resource_reached = resource_reached
