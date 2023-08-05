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
"""Models steps/actions/transforms prototypes.

A prototype is basically used to select inputs elements and to check outputs


:var C_STEP: int constant for the step level
:var C_PLAN: int constant for the plan level
:var C_PARENT: int constant for the parent plan level
:var C_MEM: int constant for the memory level

:var _CONTEXT:
  dictionary mapping literal string values to integer constants for the
  from_context attribute
:var _REV_CONTEXT: dictionary mapping integer constants to literal string values
"""

__docformat__ = "restructuredtext en"

import logging
from copy import copy

C_STEP = 0
C_PLAN = 1
C_PARENT = 2
C_MEM = 3

_CONTEXT = {'step': C_STEP, 'plan': C_PLAN,
            'parent_plan': C_PARENT, 'memory': C_MEM}
_REV_CONTEXT = {C_STEP: 'step',
                C_PLAN: 'plan',
                C_PARENT: 'parent_plan',
                C_MEM: 'memory'}



EXPR_CONTEXT = {}

def eval_expression(expr, context=None):
    """return the result of the evaluation of <expr> in <context>

    usually context has at least a "elmt" name defined, referencing a
    memory element

    :param expr: the expression to evaluate

    :param context: the context to use as locals during evaluation

    :return: the result of the evaluation
    """
    if context is None:
        context = {}
    return eval(expr, EXPR_CONTEXT, context)

def _tagger_id(node):
    """return a unique tagger id for a step / transition"""
    return (node.plan.name, node.id)


def is_tagged(element, node):
    """return true if the element as been tagged by node (tagging step or
    transition)
    """
    return _tagger_id(node) in (getattr(element, '_narval_tags', ()) or ())

def tag_element(element, node):
    """mark element as tagged by node (step or transition)"""
    # XXX lock
    if getattr(element, '_narval_tags', None) is None:
        element._narval_tags = set()
    element._narval_tags.add(_tagger_id(node))

def _default_contextes(from_context, to_context):
    if from_context is None:
        from_context = 0
    if to_context is None:
        to_context = 3
    return from_context, to_context


class PrototypeException(Exception) :
    """raised on input / output error"""


class PrototypeEntry(object):
    """A input or output prototype entry. You can use the subscription notation
    to access to / set the attributes of the prototype (match, optional...)

    :ivar matches: list of expressions to be matched by the condition
    :ivar list: flag indicating wether the condition accepts more than 1 element
    """

    def __init__(self):
        self.owner = None
        self.matches = []

    def __repr__(self):
        return getattr(self, 'id', '') + '\n'.join(self.matches)

    def clone(self):
        """make a proper copy of this prototype object and return it"""
        entry = copy(self)
        #entry.clone_attrs(self._ns_attrs, True)
        entry.matches = self.matches[:]
        return entry


class Condition(PrototypeEntry):
    """a transition's condition. Attributes :

    :ivar use:
      flag indicating wether an element triggering the condition may trigger
      it more than once (use==False)
    :ivar from_context: string controlling the element searching process
    :ivar to_context: string controlling the element searching process

    :type valid_elmts: list(AlElement)
    :ivar valid_elmts: list of elements matching the condition
    """

    def __init__(self, use=False, from_context=None, to_context=None):
        super(Condition, self).__init__()
        self.use = use
        from_context, to_context = _default_contextes(from_context, to_context)
        self.from_context = from_context
        self.to_context = to_context
        self.matching_elmts = set()
        self._satisfied_matches = set()

    def match_elements(self, elements, context=None):
        """match elements agains the condition. Return true when each
        match of the condition has been satisfied.

        :type elements: iterable
        :param elements: elements to filter against the prototype

        :type context: dict or None
        :param elements: optional context used to evaluate match expressions

        :rtype: list
        :return: elements satisfying the condition if it's now fully satisfied
        """
        context = context or {}
        use = self.use
        elements = [elmt for elmt in elements
                    if not (elmt._narval_outdated or (use and is_tagged(elmt, self.owner)))]
        for i, expr in enumerate(self.matches):
            if i in self._satisfied_matches:
                continue
            for element in elements:
                context['elmt'] = element
                if eval_expression(expr, context):
                    self._satisfied_matches.add(i)
                    self.matching_elmts.add(element)
        # only return matching elements when each al:match has been satisfied
        if self.is_satisfied():
            return self.matching_elmts
        return []

    def is_satisfied(self):
        """return true if the condition is now satisfied (i.e. each
        match in the condition is satisfied)
        """
        return len(self._satisfied_matches) == len(self.matches)


class InputEntry(PrototypeEntry):
    """a action or step input prototype. Attributes :

    :ivar id: the input id, required and unique for the step / action
    :ivar optional: flag indicating wether the input is optional or required
    :ivar use:
      flag indicating wether an element triggering the input may trigger it more
      than once (use==False)

    :ivar from_context:
      identifier of the level from which we should begin to look for
      matching elements

    :ivar to_context:
      identifier of the level until which we should stop looking for
      matching elements
    """
    def __init__(self, id, optional=False, list=False, use=False,
                 from_context=None, to_context=None):
        super(InputEntry, self).__init__()
        # XXX list
        self.id = id
        self.optional = optional
        self.list = list
        self.use = use
        from_context, to_context = _default_contextes(from_context, to_context)
        self.from_context = from_context
        self.to_context = to_context

    def matching_elements(self, elements, context=None):
        """return elements matching the prototype

        :type elements: iterable
        :param elements: elements to filter against the prototype

        :rtype: list
        :return: elements among the given ones satisfying the prototype
        """
        match_elmts = []
        use, matches = self.use, self.matches
        context = context or {}
        for element in elements:
            if not getattr(element, '_narval_outdated', None) and (
                (not use) or (use and not is_tagged(element, self.owner))):
                context['elmt'] = element
                for expr in matches:
                    if not eval_expression(expr, context):
                        break
                else:
                    match_elmts.append(element)
        return match_elmts


class OutputEntry(PrototypeEntry):
    """a action or step output prototype. Attributes :

    :ivar id: the output id, required and unique for the step / action
    :ivar optional: flag indicating wether the output is optional or required
    :ivar outdates:
      an optional string referencing and input id to outdate elements from
      this entry
    """

    def __init__(self, id, optional=False, list=False, outdates=None):
        super(OutputEntry, self).__init__()
        self.id = id
        self.optional = optional
        self.list = list
        self.outdates = outdates

    def matching_elements(self, elements, context=None):
        """return elements matching the prototype

        :type elements: iterable
        :param elements: elements to filter against the prototype

        :rtype: list
        :return: elements among the given ones satisfying the prototype
        """
        match_e = []
        context = context or {}
        for element in elements:
            context['elmt'] = element
            for expr in self.matches:
                if not eval_expression(expr, context):
                    break
            else:
                match_e.append(element)
        return match_e


class Prototype(object):
    """A step / action prototype is a list of input / output prototypes

    :type overload: `Prototype` or None
    :ivar overload:
      optional overloaded prototype (i.e. when we are a step prototype refining
      its target's prototype
    """

    def __init__(self) :
        self._inputs, self._outputs = [], []
        self.overload = None
        self.owner = None
        self.in_mixed, self.out_mixed = None, None

    def set_owner(self, owner) :
        """set owner on this prototype and on this prototype's inputs

        :type owner: `narval.plan.PlanStep`
        :param owner: the step owning this prototype
        """
        self.owner = owner
        for input_proto in self._inputs:
            input_proto.owner = owner

    def prepare(self, overloaded):
        """prepare a step prototype

        :type overloaded:  `Prototype`
        :param overloaded: the step's target prototype
        """
        self.overload = overloaded

    def add_in_entry(self, entry):
        """add an input prototype entry

        :type entry: `InputEntry`
        :param id: the prototype entry object
        """
        self._inputs.append(entry)

    def add_out_entry(self, entry):
        """add an output prototype entry

        :type entry: `OutputEntry`
        :param id: the prototype entry object
        """
        self._outputs.append(entry)

    def input_prototype(self):
        """return the merged input prototypes

        :rtype: list
        :return:
          the list of merged input prototypes (i.e. step prototype + target
          prototype)
        """
        if self.in_mixed:
            return self.in_mixed
        if self.overload:
            newlist = merge_input(self.overload._inputs, self._inputs)
            self.in_mixed = newlist
            for input_proto in newlist:
                input_proto.owner = self.owner
        else:
            newlist = [elmt for elmt in self._inputs
                       if elmt.matches or not elmt.optional]
        return newlist

    def output_prototype(self):
        """return the merged output prototypes

        :rtype: list
        :return:
          the list of merged output prototypes (i.e. step prototype + target
          prototype)"""
        if self.out_mixed:
            return self.out_mixed
        if self.overload:
            newlist = merge_output(self.overload._outputs, self._outputs)
            self.out_mixed = newlist
        else:
            newlist = [elmt for elmt in self._outputs
                       if elmt.matches or not elmt.optional]
        return newlist

    def check(self, target):
        """check this is a valid prototype

        :type target:
          `narval.action.ActionElement`
        :param target: the step's target

        :raise `PrototypeException`: if this is not a valid prototype
        """
        target_in_proto = target.prototype._inputs
        target_out_proto = target.prototype._outputs
        for step_in_proto in self._inputs:
            self.check_entry(target_in_proto, step_in_proto)
        for step_out_proto in self._outputs:
            self.check_entry(target_out_proto, step_out_proto)
        errors = []
        for entry in target_in_proto:
            if entry.id is None:
                errors.append('* input without id found in action %s.%s' %
                              (target.group, target.name))
        for entry in target_out_proto:
            if entry.id is None:
                errors.append('* output without id found in action %s.%s' %
                              (target.group, target.name))
        errors += _check_entries(merge_input(target_in_proto, self._inputs))
        errors += _check_entries(merge_output(target_out_proto, self._outputs))
        if errors:
            raise PrototypeException('  \n' + '  \n'.join(errors))

    def check_entry(self, entries, entry) :
        """check <entry> is in <entries>

        :type entries: list
        :param entries: a list of elements

        :type entry: narval.public.ALElement
        :param entry: the element to check

        :raise `PrototypeException`: if the entry is not in the entries set
        """
        e_id = entry.id
        if e_id is None:
            raise PrototypeException('entry without id found')
        for old in entries:
            if old.id == e_id:
                break
        else :
            raise PrototypeException('entry with id %s not found' % e_id)



def _check_entries(entries):
    """check prototype entries

    :type entries: list
    :param entries: list of prototype entries to check

    :rtype: list
    :return: a list of strings describing errors (empty list means no error)
    """
    errors, ids_dict = [], {}
    for entry in entries:
        if not entry.matches and not entry.optional:
            errors.append('* input prototype error: no match for %s' %
                          entry.id)
        if ids_dict.has_key(entry.id):
            errors.append('* input prototype error: duplicate id %s' %
                          entry.id)
        else:
            ids_dict[entry.id] = 1
    return errors


def merge_input(target_proto, step_proto) :
    """merge input step prototype with target prototype

    :type target_proto: list
    :param target_proto: list of target prototype input entries

    :type step_proto: list
    :param step_proto: list of step prototype input entries

    :rtype: list
    :return: the list of merged prototype entries
    """
    newlist = []
    for old in target_proto:
        for new in step_proto:
            if old.id == new.id :
                merged = old.clone()
                # the "list" attribute is not overidable
                # FIXME: check that "step.list == action.list" in check_recipe
                # FIXME: should not do this if the default value is used !
                if old.optional and not new.optional:
                    merged.optional = False
                if not old.use and new.use:
                    merged.use = True
                for expr in new.matches:
                    if expr not in old.matches:
                        merged.matches.append(expr)
                merged.from_context = new.from_context
                merged.to_context = new.to_context
                #if merged.matches or not merged.optional:
                newlist.append(merged)
                break
        else:
            #if old.matches or not old.optional:
            newlist.append(old)
    return newlist


def merge_output(target_proto, step_proto) :
    """merge output step prototype with target prototype

    :type target_proto: list
    :param target_proto: list of target prototype output entries

    :type step_proto: list
    :param step_proto: list of step prototype output entries

    :rtype: list
    :return: the list of merged prototype entries
    """
    newlist = []
    for old in target_proto:
        for new in step_proto:
            if old.id == new.id :
                merged = old.clone()
                # FIXME:  check that "step.list == action.list" in check_recipe
                # and step.optional == action.optional
                if not old.outdates and new.outdates:
                    merged.outdates = new.outdates
                for expr in new.matches:
                    if expr not in old.matches:
                        merged.matches.append(expr)
                if merged.matches or not merged.optional:
                    newlist.append(merged)
                break
        else:
            #if old.matches or not old.optional:
            newlist.append(old)
    return newlist


# action decorators ############################################################

def action(id, doc=None, finalizer=None, nonexecuted=None):
    def decorator(f):
        assert not id in _ACTIONS, 'an action %s already exists' % id
        _ACTIONS[id] = {'func': f,
                        'module': f.__module__,
                        'doc': doc or f.__doc__,
                        'prototype': Prototype(),
                        'finalizer_func': finalizer,
                        'nonexecuted_func': nonexecuted,
                        }
        _PROTOS[f] = _ACTIONS[id]['prototype']
        LOGGER = logging.getLogger('narval.engine')
        LOGGER.debug('action %s registered with id %s' % (f, id))
        return f
    return decorator

def input(id, *conditions, **kwargs):
    def decorator(f):
        fproto = _get_proto(f)
        inputproto = InputEntry(id, **kwargs)
        inputproto.matches += conditions
        fproto.add_in_entry(inputproto)
        return f
    return decorator

def output(id, *conditions, **kwargs):
    def decorator(f):
        fproto = _get_proto(f)
        outputproto = OutputEntry(id, **kwargs)
        outputproto.matches += conditions
        fproto.add_out_entry(outputproto)
        return f
    return decorator

# action accessor ##############################################################

def get_action(id):
    return _ACTIONS[id]

# private stuff ################################################################

_ACTIONS = {}
_PROTOS = {}

def _get_proto(f):
    try:
        return _PROTOS[f]
    except KeyError:
        raise Exception('Function not registered as action. You should use the '
                        '@action decorator as first decorator (eg the first '
                        'one above the function definition)')
