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
"""delegate classes for step execution, according to step's type"""

__docformat__ = "restructuredtext en"

import sys
import traceback
from copy import copy

from logilab.common import flatten
from logilab.common.proc import RESOURCE_LIMIT_EXCEPTION

from narvalbot.prototype import get_action, tag_element
from narvalbot.elements import ErrorElement

def source_tag(element, step) :
    """tag an element as coming from step and step's plan

    :type element: `narval.public.ALElement`
    :param element: element to tag

    :type step: `narval.plan.PlanStep`
    :param step: the step which has produced the element
    """
    element._narval_from_plan = step.plan._narval_eid
    element._narval_from_step = step.id

# Exceptions ##################################################################

class DelegateException(Exception):
    """raised when delegate faces problem

    :type list: list
    :ivar list: list of errors
    """

    def __init__(self, list):
        self.list = list
        Exception.__init__(self, list)

class BadInput(DelegateException):
    """problem with inputs in prepare()"""

class BadOutput(DelegateException):
    """problem with outputs in end()"""

class ErrorOutput(DelegateException):
    """found an error element in outputs"""


###############################################################################

class Delegate(object):
    """Handles the preparation, execution and termination of a step

    :type step: `narval.plan.PlanStep`
    :ivar step: a reference to the step object

    :type target: str
    :ivar target: <group>.<name> of the step's target
    """

    def __init__(self, step) :
        self.step = step
        self.target = None

    def init(self):
        """init the step (at narval plan creation time)"""
        raise NotImplementedError()

    def prepare(self):
        """prepare the step (when step is ready to run)"""
        raise NotImplementedError()

    def run(self):
        """execute the step"""
        raise NotImplementedError()

    def end(self):
        """the step has finished"""
        raise NotImplementedError()


class RecipeDelegate(Delegate) :
    """step's recipe delegate

    :type recipe: `narval.recipe.RecipeElement`
    :ivar recipe: the recipe target of the step
    """
    def init(self):
        pass

    def prepare(self):
        """prepare the step"""
        step = self.step
        self.recipe = step.plan.memory.get_recipe(step.target)
        step.set_state('ready')

    def run(self):
        """execute the step"""
        step = self.step
        step.outputs = []
        mem = step.plan.memory
        step.set_state('running')
        name = step.target
        msg = None#self.recipe.check_syntax()[1]
        if msg:
            err = mem.mk_error(msg, 'bad recipe')
            source_tag(err, step)
            step.plan.add_elements([err])
            step.set_state('failed')
        else:
            mem.start_plan(self.recipe, step)

    def end(self):
        """the step has finished"""
        self.step.set_state('done')


class ActionDelegate(Delegate) :
    """step's action delegate

    :type action: `narval.action.ActionElement`
    :ivar action: the action target of the step
    """
    def init(self):
        # will check action availability
        self._set_target()
        if self.action['finalizer_func']:
            self.step.plan.finalizers.append(self.action['finalizer_func'])
        self.step.nonexecuted_func = self.action['nonexecuted_func']

    def prepare(self):
        """prepare the step"""
        assert self.step.state == 'todo', (self.step.state, id(self.step))
        step = self.step
        # check plan state
        if step.plan.state not in ('running', 'fireable'):
            step.set_state('failed')
        else:
            # prototype
            try:
                step.prototype.prepare(self.action['prototype'])
            except RESOURCE_LIMIT_EXCEPTION:
                raise
            except Exception, ex:
                step.error('exception while executing target for step %s',
                           self.step.readable_name(), exc_info=True)
                step.set_state('failed')
            else:
                # inputs
                try:
                    step.inputs = self.retreive_inputs()
                    step.set_state('ready')
                except BadInput, ex :
                    for type, msg in ex.list :
                        msg = 'Bad input for %s: %s' % (step.readable_name(), msg)
                        err = step.plan.memory.mk_error(msg, type)
                        source_tag(err, step)
                        step.plan.add_elements([err])
                    step.set_state('failed')

    def retreive_inputs(self):
        """fetchs and computes inputs for the step according to its prototype

        :raise `BadInput`: if there is some error preventing inputs computation

        :rtype: dict
        :return: a dictionary defining step's inputs
        """
        step = self.step
        selected_inputs = {}
        foreach_f = step.foreach
        foreach_input = None
        errors = []
        context = {}
        # add arguments
        if step.arguments:
            step.plan.add_elements(step.arguments)
        # select inputs
        for input in step.prototype.input_prototype():
            list, use, optional = input.list, input.use, input.optional
            cands = step.get_inputs(input, context)
            # look for map, fail if imprecise
            if foreach_f and input.id == foreach_f:
                foreach_input = input
                if list:
                    errors.append(('bad foreach','applies to a list'))
                else:
                    list = True
            # select
            nb = len(cands)
            if (nb == 1) or (nb > 0 and list) or (nb == 0 and optional):
                selected_inputs[input] = cands
                if use:
                    for elmt in cands:
                        tag_element(elmt, self.step)
            elif nb:
                candidates = '\n\t'.join([str(elmt) for elmt in cands])
                msg = "%d inputs instead of one with prototype= %s. " \
                      "Candidates are \n\t%s" % (nb, str(input), candidates)
                errors.append( ('undecidable input', msg) )
            else:
                errors.append(('missing input',
                               "no input found with prototype=\n%s" % input))
            if not errors:
                # add matched elements to context using the input's id, so it can
                # be used in expression of following inputs
                if list:
                    context[input.id] = cands
                elif cands:
                    context[input.id] = cands[0]
                else:
                    context[input.id] = None
        if foreach_f and not foreach_input:
            errors.append(('bad foreach', 'no input with id %s' % foreach_f))
        # fail on errors
        if errors:
            raise BadInput(errors)
        step.input_foreach = foreach_input
        # ready to run
        return selected_inputs


    def run(self):
        """execute the step"""# in a new thread"""
        try:
            step = self.step
            plan = step.plan
            step.set_state('running')
            input_sets = []
            output_sets = step.output_sets
            # make input sets
            if step.input_foreach:
                for elmt in step.inputs[step.input_foreach]:
                    input_set = copy(step.inputs)
                    input_set[step.input_foreach] = [elmt]
                    input_sets.append(input_set)
            else:
                input_sets.append(copy(step.inputs))
            # execute
            for input_set in input_sets:
                # add elements to plan context
                for elements_list in input_set.values():
                    plan.add_elements(elements_list)
                output_sets.append( (input_set, self._execute(input_set)) )
            # done
            step.set_state('end')
        except RESOURCE_LIMIT_EXCEPTION, ex:
            context = 'running step %s' % step.readable_name()
            step.resource_reached(ex, context)
            step.set_state('killed')
        except Exception, ex:
            step.error('Exception raised while running step %s'
                       % step.readable_name(), exc_info=True)
            step.set_state('error')
        finally:
            step.plan.memory.cnxh.commit()

    def _execute(self, input_set):
        """execute the target with the given input set

        :type input_set: dict
        :param input_set: dictionary defining step's inputs

        :rtype: list
        :return: the list of elements produced by the step, with eventual errors
        """
        try:
            # get output and delete args
            output = self._execute_target(input_set)
        except RESOURCE_LIMIT_EXCEPTION, exc:
            raise
        except Exception, exc: # catch anything
            plan = self.step.plan
            output = {'error': plan.memory.mk_traceback_error(plan, sys.exc_info())}
        return output

    def _execute_target(self, input_set):
        """execute the target with the given input set

        :type input_set: dict
        :param input_set: dictionary defining step's inputs

        :rtype: list
        :return: the list of elements produced by the step
        """
        args_d = {}
        for input, element_list in input_set.items() :
            id, list = input.id, input.list
            if list:
                args_d[id] = []
                for element in element_list:
                    element.input_id = id
                    args_d[id].append(element)
            elif element_list:
                element = element_list[0]
                element.input_id = id
                args_d[id] = element
            else:
                args_d[id] = None
        output_dict = self.action['func'](args_d)
        assert type(output_dict) is dict, "type(ouptut_dict) = %s, should be %s" % \
               (type(output_dict), dict)
        return output_dict


    def end(self):
        """end the step"""
        step = self.step
        step.outputs = []
        final_state = 'done'
        # check output
        try:
            for input_set, outputs in step.output_sets:
                try:
                    self._check_for_error_elements(outputs)
                    output_ok = self._match_output(outputs)
                    self._accept_output(input_set, output_ok)
                    step.outputs.append(output_ok)
                except ErrorOutput, ex :
                    for error in ex.list :
                        source_tag(error, step)
                        step.plan.add_elements([error])
                    if final_state != 'failed' :
                        final_state = 'error'
                except BadOutput, ex :
                    msg = 'Action %s at step %s returned bad output:' % (
                        step.target, step.id)
                    for txt in ex.list :
                        if isinstance(txt, str):
                            txt = unicode(txt, 'UTF-8')
                        msg = '%s\n- %s'% (msg, txt)
                    error = step.plan.memory.mk_error(msg, 'bad output')
                    step.plan.add_elements([error])
                    final_state = 'failed'
        except RESOURCE_LIMIT_EXCEPTION, exc:
            context = 'processing end of step %s' % step.readable_name()
            self.resource_reached(exc, context=context)
            final_state = 'killed'
            raise
        except:
            step.critical('Error while processing the end of step %s'
                          % step.readable_name(), exc_info=True)
            final_state = 'error'
        finally:
            step.set_state(final_state)


    def _check_for_error_elements(self, outputs):
        """check presence of error elements in outputs

        :type outputs: list
        :param outputs: list of produced elements

        :raise `ErrorOutput`: if there is at least one error element in outputs
        """
        errors = [elmt for elmt in flatten(outputs.values())
                  if isinstance(elmt, ErrorElement)]
        if errors :
            raise ErrorOutput(errors)


    def _match_output(self, outputs):
        """check that outputs match the prototype

        :type outputs: dict
        :param outputs: dictionary of produced elements

        :raise `BadOutput`:
          if there is some elements not satisfying the step's prototype

        :rtype: dict
        :return:
          the dictionary of output elements indexed by their ouput entry in
          the prototype
        """
        problems = []
        # try to match output elements to prototype and prepare output_ok
        output_ok, output_p_dict = {}, {}
        for output_p in self.step.prototype.output_prototype():
            output_p_dict[output_p.id] = output_p
            output_ok[output_p] = []
        for opid, elmts in outputs.items():
            if elmts is None:
                continue
            if not isinstance(elmts, (list, tuple)):
                elmts = (elmts,)
            try:
                output_p = output_p_dict[opid]
            except KeyError:
                if opid != 'error':
                    problems.append('No output prototype with id=%s' % opid)
                continue
            for elmt in elmts:
                if not output_p.matching_elements( (elmt,) ):
                    problems.append('%s is not matched by output with id=%s'
                                    % (elmt, opid))
                else:
                    output_ok[output_p].append(elmt)
        # check that number of outputs is correct
        for output_p, elmts in output_ok.items():
            if len(elmts) == 0 and not output_p.optional:
                problems.append("Missing output for %s" % output_p)
            elif len(elmts) > 1 and not output_p.list :
                problems.append("Too many outputs. Got %s expected %s"
                                % (elmts, output_p))
        if problems :
            raise BadOutput(problems)
        # FIXME: check that the same element isn't matched by more than
        #        one output prototype ?
        return output_ok


    def _accept_output(self, input_set, output_ok):
        """process accepted outputs

        :type input_set: dict
        :param input_set: dictionary of step's input elements

        :type output_ok: dict
        :param output_ok: dictionary of step's output elements
        """
        pending = None
        for output, elmt_list in output_ok.items():
##             # FIXME: hard coded id ?!
##             if output.id == 'startplan':
##                 pending = output
##                 continue
            output_ok[output] = self._accept_one_output(input_set, output,
                                                        elmt_list)
        if pending is not None:
            output_ok[pending] = self._accept_one_output(input_set, pending,
                                                         output_ok[pending])

    def _accept_one_output(self, input_set, output, elmts_list):
        """process one output (may contains multiple elements) :
        handle use, outdates and add elements to the parent plan

        :type input_set: dict
        :param input_set: dictionary of step's input elements

        :type output: `narval.prototype.OutputEntry`
        :param output: the output prototype entry

        :type elmts_list: list
        :param elmts_list: list of elements matching the given prototype entry

        :rtype: list
        :return: the list of accepted elements for the given output
        """
        step = self.step
        imported_elmts = elmts_list[:]
        # tag
        for elmt in imported_elmts:
            source_tag(elmt, step)
        # outdates
        outdates = output.outdates
        if outdates:
            for input_entry, elmts in input_set.items() :
                if input_entry.id == outdates:
                    for elmt in elmts:
                        elmt._narval_outdated=  True
                    break
            else:
                raise Exception('No input with id %s' % outdates)
        # add to plan
        step.plan.add_elements(imported_elmts)
        return imported_elmts


    def _set_target(self) :
        """get the action element

        :rtype: `narval.action.ActionElement`
        :return: the step's target
        """
        self.action = get_action(self.step.target)
        #return mem.check_date(mem.get_action(step.target))
