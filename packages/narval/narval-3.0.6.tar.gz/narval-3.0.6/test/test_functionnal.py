from cubicweb import ValidationError, devtools

from cubes.narval.testutils import NarvalBaseTC

from narvalbot import main
from narvalbot.elements import EnsureOptions, Options
from narvalbot.prototype import EXPR_CONTEXT, action, input, output

class ArbitraryObject(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

EXPR_CONTEXT['ArbitraryObject'] = ArbitraryObject

@input('input', "isinstance(elmt, Options)")
@action('test.needs_one_input')
def act_needs_one_input(inputs) :
    assert inputs['input']['value'] == 1
    return {}

class NarvalFunctionalTC(NarvalBaseTC):
    """Test for no operation recipe"""
    def test_noop(self):
        recipe = self.req.create_entity('Recipe', name=u'functest.noop')
        step1 = recipe.add_step(u'action', u'basic.noop', initial=True)
        step2 = recipe.add_step(u'action', u'basic.noop', final=True)
        recipe.add_transition(step1, step2)
        recipe = self.req.entity_from_eid(recipe.eid)
        self.run_recipe(recipe)

    def test_noop_cycle(self):
        recipe = self.req.create_entity('Recipe', name=u'functest.noop')
        step = recipe.add_step(u'action', u'basic.noop', initial=True, final=True)
        recipe.add_transition(step, step)
        recipe = self.req.entity_from_eid(recipe.eid)
        self.assertRaises(ValidationError, self.run_recipe, recipe)

    def test_plan_arguments(self):
        recipe = self.req.create_entity('Recipe', name=u'functest.mirror')
        step = recipe.add_step(u'action', u'basic.mirror', for_each=u'input',
                               initial=True, final=True)
        self.run_recipe(recipe, arguments=u'ArbitraryObject(attr=1)')
        memelements = main.ENGINE.memory.elements.values()
        self.assertEqual(len(memelements), 2)
        self.failUnless([x for x in memelements if isinstance(x, ArbitraryObject)])
        plan = [x for x in memelements if isinstance(x, EXPR_CONTEXT['Plan'])][0]
        self.assertEqual(len(plan.p_elements), 4, plan.p_elements)
        self.assertIn(plan, plan.p_elements)
        a, b = [x for x in plan.p_elements if isinstance(x, ArbitraryObject)]
        self.failIf(a is b)

    def test_step_arguments_base(self):
        recipe = self.req.create_entity('Recipe', name=u'functest.mirror')
        step = recipe.add_step(u'action', u'basic.mirror', initial=True,
                               final=True, arguments=u'ArbitraryObject(attr=1)')
        self.run_recipe(recipe)
        memelements = main.ENGINE.memory.elements.values()
        self.assertEqual(len(memelements), 2)
        self.failUnless([x for x in memelements if isinstance(x, ArbitraryObject)])
        plan = [x for x in memelements if isinstance(x, EXPR_CONTEXT['Plan'])][0]
        self.assertEqual(len(plan.p_elements), 3, plan.p_elements)
        self.assertIn(plan, plan.p_elements)
        a, b = [x for x in plan.p_elements if isinstance(x, ArbitraryObject)]
        self.failIf(a is b)

    def test_step_arguments_priority(self):
        recipe = self.req.create_entity('Recipe', name=u'functest.argpriority')
        step = recipe.add_step(u'action', u'test.needs_one_input', initial=True,
                               final=True, arguments=u'Options(value=1)')
        self.run_recipe(recipe, arguments=u'Options(value=2)')
        memelements = main.ENGINE.memory.elements.values()
        self.assertEqual(len(memelements), 3, memelements)
        self.assertEqual(len([x for x in memelements if isinstance(x, Options)]), 2)

    def test_step_outdates(self):
        # XXX not sure outdates is really useful...
        recipe = self.req.create_entity('Recipe', name=u'functest.mirror')
        step = recipe.add_step(u'action', u'basic.mirror', initial=True,
                               final=True, arguments=u'ArbitraryObject(attr=1)')
        step.add_output(u'output', outdates=u'input')
        self.run_recipe(recipe)
        memelements = main.ENGINE.memory.elements.values()
        plan = [x for x in memelements if isinstance(x, EXPR_CONTEXT['Plan'])][0]
        a, b = [x for x in plan.p_elements if isinstance(x, ArbitraryObject)]
        self.failIf(a is b)
        self.failIf(a._narval_outdated and b._narval_outdated)
        self.failUnless(a._narval_outdated or b._narval_outdated)
        self.failIf(getattr(a, '_narval_tags', None) or getattr(b, '_narval_tags', None))

    def test_step_use(self):
        # XXX not sure outdates is really useful...
        recipe = self.req.create_entity('Recipe', name=u'functest.mirror')
        step = recipe.add_step(u'action', u'basic.mirror', initial=True,
                               final=True, arguments=u'ArbitraryObject(attr=1)')
        step.add_input(u'input', use=True)
        self.run_recipe(recipe)
        memelements = main.ENGINE.memory.elements.values()
        plan = [x for x in memelements if isinstance(x, EXPR_CONTEXT['Plan'])][0]
        a, b = [x for x in plan.p_elements if isinstance(x, ArbitraryObject)]
        self.failIf(a is b)
        self.failIf(a._narval_outdated or b._narval_outdated)
        self.failUnless(getattr(a, '_narval_tags', None) or getattr(b, '_narval_tags', None))
        # we actually get it on both a and b due to mirror misimplementation
        self.assertEqual(a._narval_tags, set([(u'functest.mirror', step.eid)]))

    def test_subrecipe(self):
        subrecipe = self.req.create_entity('Recipe', name=u'functest.noop')
        subrecipe.add_step(u'action', u'basic.noop', initial=True, final=True)
        recipe = self.req.create_entity('Recipe', name=u'functest.subrecipe')
        recipe.add_step(u'recipe', u'functest.noop', initial=True, final=True)
        self.run_recipe(recipe)


    def test_added_to_narval_memory_hook_1(self):
        recipe = self.req.create_entity('Recipe', name=u'functest.argpriority')
        step = recipe.add_step(u'action', u'test.needs_one_input', initial=True,
                               final=True, arguments=u'EnsureOptions(value=1)')
        self.run_recipe(recipe, arguments=u'Options(value=2)')
        memelements = main.ENGINE.memory.elements.values()
        self.assertEqual(len(memelements), 3, memelements)
        self.failUnless([x for x in memelements if x.__class__ is EnsureOptions])
        self.failUnless([x for x in memelements if x.__class__ is Options])
        self.failUnless([x for x in memelements if isinstance(x, EXPR_CONTEXT['Plan'])])
        opt = (x for x in memelements if x.__class__ is Options).next()
        self.assertEqual(opt['value'], 1)

    def test_added_to_narval_memory_hook_2(self):
        recipe = self.req.create_entity('Recipe', name=u'functest.argpriority')
        step = recipe.add_step(u'action', u'test.needs_one_input', initial=True,
                               final=True, arguments=u'EnsureOptions(value=1)')
        self.run_recipe(recipe)
        memelements = main.ENGINE.memory.elements.values()
        self.assertEqual(len(memelements), 2, memelements)
        self.failIf([x for x in memelements if x.__class__ is EnsureOptions])
        self.failUnless([x for x in memelements if x.__class__ is Options])
        self.failUnless([x for x in memelements if isinstance(x, EXPR_CONTEXT['Plan'])])
        opt = (x for x in memelements if x.__class__ is Options).next()
        self.assertEqual(opt['value'], 1)

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
