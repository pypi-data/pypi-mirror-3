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
"""cubicweb-narval schema"""
from logilab.common.tasksqueue import MEDIUM, PRIORITY
from yams.buildobjs import (DEFAULT_ATTRPERMS, EntityType, RelationDefinition,
                            String, Bytes, Datetime, Time, Boolean, Int)
from cubicweb.schema import (PUB_SYSTEM_ENTITY_PERMS, PUB_SYSTEM_REL_PERMS,
                             RQLConstraint)

IMMUTABLE_ATTR_PERMS = DEFAULT_ATTRPERMS.copy()
IMMUTABLE_ATTR_PERMS['update'] = ()

class Recipe(EntityType):
    __permissions__ = PUB_SYSTEM_ENTITY_PERMS
    name = String(maxsize=256, unique=True,
                  description=_("the recipe's name"))

class require_permission(RelationDefinition):
    subject = 'Recipe'
    object = 'CWPermission'

class RecipeStep(EntityType):
    __permissions__ = PUB_SYSTEM_ENTITY_PERMS
    label = String()
    type = String(vocabulary=('recipe', 'action'),
                  description=_(""))
    target = String(maxsize=256,
                    description=_("the step's target name (either an action or a recipe)"))
    for_each = String(maxsize=256,
                      description=_("optional identifier of an input on which the step should be repeated"))
    arguments = String(description=_('predefined arguments for this step, as python expressions (one per line).'
                                     'You can instantiate any object defined in narval\'s expression context.'))

class RecipeTransition(EntityType):
    __permissions__ = PUB_SYSTEM_ENTITY_PERMS
    priority = Int(description=_("when several transitions are fireable, there should be one (and only one) with a greater priority that will be fired."))


class NarvalConditionExpression(EntityType):
    __permissions__ = PUB_SYSTEM_ENTITY_PERMS
    expression = String()


class RecipeTransitionCondition(EntityType):
    __permissions__ = PUB_SYSTEM_ENTITY_PERMS
    use = Boolean(description=_('flag indicating wether an element triggering the condition may trigger it more than once'),
                  default=False)
    from_context = Int(vocabulary=range(4), default=0,
                       description=_('level from which we should begin to look for matching elements'))
    to_context = Int(vocabulary=range(4), default=3,
                     description=_('level until which we should stop looking for matching elements'))


class RecipeStepInput(EntityType):
    __permissions__ = PUB_SYSTEM_ENTITY_PERMS
    id = String(maxsize=256, description=('the input id, required and unique for the step / action'),
                required=True)
    use = Boolean(description=_('flag indicating wether an element triggering the input may trigger it more than once'),
                  default=False)
    optional = Boolean(description=_('flag indicating wether the input is optional or required'),
                       default=False)
    from_context = Int(vocabulary=range(4), default=0,
                       description=_('level from which we should begin to look for matching elements'))
    to_context = Int(vocabulary=range(4), default=3,
                     description=_('level until which we should stop looking for matching elements'))


class RecipeStepOutput(EntityType):
    __permissions__ = PUB_SYSTEM_ENTITY_PERMS
    id = String(maxsize=256, description=('the output id, required and unique for the step / action'),
                required=True)
    optional = Boolean(description=('flag indicating wether the output is optional or required'))
    outdates = String(description=_('an optional string referencing and input id to outdate elements from this entry'))


class Plan(EntityType):
     # add permissions actually checked according to recipe
    __permissions__ = {'read': ('managers', 'users', 'guests', 'narval'),
                       'add': ('managers', 'users', 'narval'),
                       'update': ('narval',),
                       'delete': ('managers',),
                       }
    priority = Int(default=MEDIUM,
                   vocabulary=PRIORITY.values(),
                   __permissions__=IMMUTABLE_ATTR_PERMS)
    options = String(description=_('plan option: key=value, one per line'),
                     __permissions__=IMMUTABLE_ATTR_PERMS)
    arguments = String(description=_('predefined arguments for this plan, as python expressions (one per line).'
                                     'You can instantiate any object defined in narval\'s expression context.'),
                       __permissions__=IMMUTABLE_ATTR_PERMS)

    execution_status = String(maxsize=20, default='ready',
                              vocabulary=[_('ready'), _('running'),
                                _('done'), _('failed'), _('killed')],
                              indexed=True, internationalizable=True)
    starttime = Datetime()
    endtime   = Datetime()
    execution_log = String()


class in_recipe(RelationDefinition):
    __permissions__ = PUB_SYSTEM_REL_PERMS
    subject = ('RecipeStep', 'RecipeTransition')
    object = 'Recipe'
    composite = 'object'
    cardinality = '1*'
    inlined = True

class start_step(RelationDefinition):
    __permissions__ = PUB_SYSTEM_REL_PERMS
    subject = 'Recipe'
    object = 'RecipeStep'
    cardinality = '??' # XXX should be '1?', left to '??' to ease recipe creation
    inlined = True

class end_step(RelationDefinition):
    __permissions__ = PUB_SYSTEM_REL_PERMS
    subject = 'Recipe'
    object = 'RecipeStep'
    cardinality = '??' # XXX should be '1?', left to '??' to ease recipe creation
    inlined = True


class in_steps(RelationDefinition):
    __permissions__ = PUB_SYSTEM_REL_PERMS
    subject = 'RecipeTransition'
    object = 'RecipeStep'
    description = _('list of steps incoming to this transition')
    cardinality = '+*'


class in_error_steps(RelationDefinition):
    __permissions__ = PUB_SYSTEM_REL_PERMS
    subject = 'RecipeTransition'
    object = 'RecipeStep'
    description = _('list of steps incoming to this transition if they ended on error')
    constraints = [RQLConstraint('S in_steps O')]

class out_steps(RelationDefinition):
    __permissions__ = PUB_SYSTEM_REL_PERMS
    subject = 'RecipeTransition'
    object = 'RecipeStep'
    description = _('list of steps outgoing from this transition')
    cardinality = '+*'

class conditions(RelationDefinition):
    __permissions__ = PUB_SYSTEM_REL_PERMS
    subject = 'RecipeTransition'
    object = 'RecipeTransitionCondition'
    description = _('conditions to satisfy before being fireable')
    composite = 'subject'
    cardinality = '*1'


class takes_input(RelationDefinition):
    __permissions__ = PUB_SYSTEM_REL_PERMS
    subject = 'RecipeStep'
    object = 'RecipeStepInput'
    #description = _('')
    composite = 'subject'
    cardinality = '*1'

class generates_output(RelationDefinition):
    __permissions__ = PUB_SYSTEM_REL_PERMS
    subject = 'RecipeStep'
    object = 'RecipeStepOutput'
    #description = _('')
    composite = 'subject'
    cardinality = '*1'


class matches_condition(RelationDefinition):
    __permissions__ = PUB_SYSTEM_REL_PERMS
    subject = ('RecipeTransitionCondition',
               'RecipeStepInput', 'RecipeStepOutput')
    object = 'NarvalConditionExpression'
    composite = 'subject'
    cardinality = '*1'


class execution_of(RelationDefinition):
    # add permissions actually checked according to recipe
    __permissions__ = {'read': ('managers', 'users', 'guests', 'narval'),
                       'add': ('managers', 'users', 'narval'),
                       'delete': ('managers',),
                       }
    subject = 'Plan'
    object = 'Recipe'
    inlined = True
    cardinality = '1*'
    composite = 'object'
