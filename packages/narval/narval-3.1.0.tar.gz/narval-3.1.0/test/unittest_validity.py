# Copyright (c) 2000-2010 LOGILAB S.A. (Paris, FRANCE).
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
"""cubicweb-narval validity tests classes"""
__docformat__ = "restructuredtext en"

from cubicweb.devtools.testlib import CubicWebTC

class ValidityTC(CubicWebTC):

    def test_no_element(self):
        recipe = self.session.create_entity('Recipe', name=u'toto')
        self.commit()
        errors = recipe.check_validity()
        self.assertEqual([recipe.eid], errors.keys())
        self.assertEqual(errors[recipe.eid][0].msg, 'no elements')

    def test_no_initial_final(self):
        recipe = self.session.create_entity('Recipe', name=u'toto')
        step = recipe.add_step(u'action', u'apycot.init')
        self.commit()
        errors = recipe.check_validity()
        self.assertEqual([e.msg for e in errors[recipe.eid]],
                          [u'initial step is missing', u'final step is missing'])
        self.assertEqual([e.msg for e in errors[step.eid]],
                          [u'this step must have at least one incoming transition',
                           u'this step must have at least one outgoing transition'])

    def test_initial_no_successor(self):
        recipe = self.session.create_entity('Recipe', name=u'toto')
        step = recipe.add_step(u'action', u'apycot.init', initial=True)
        self.commit()
        errors = recipe.check_validity()
        self.assertEqual([e.msg for e in errors[recipe.eid]],
                          [u'final step is missing'])
        self.assertEqual([e.msg for e in errors[step.eid]],
                          [u'this step must have at least one outgoing transition'])

    def test_final_no_predecessor(self):
        recipe = self.session.create_entity('Recipe', name=u'toto')
        step = recipe.add_step(u'action', u'apycot.init', final=True)
        self.commit()
        errors = recipe.check_validity()
        self.assertEqual([e.msg for e in errors[recipe.eid]],
                          [u'initial step is missing'])
        self.assertEqual([e.msg for e in errors[step.eid]],
                          [u'this step must have at least one incoming transition'])

    def test_final_no_predecessor(self):
        recipe = self.session.create_entity('Recipe', name=u'toto')
        stepi = recipe.add_step(u'action', u'apycot.init', initial=True)
        stepf = recipe.add_step(u'action', u'apycot.init', final=True)
        self.commit()
        errors = recipe.check_validity()
        self.assertEqual([e.msg for e in errors[stepi.eid]],
                          [u'this step must have at least one outgoing transition'])
        self.assertEqual([e.msg for e in errors[stepf.eid]],
                          [u'this step must have at least one incoming transition'])

    def test_loop(self):
        recipe = self.session.create_entity('Recipe', name=u'toto')
        step = recipe.add_step(u'action', u'apycot.init', initial=True, final=True)
        recipe.add_transition(step, step)
        self.commit()
        self.assertEqual(recipe.check_validity()[recipe.eid][0].cycle, [step.eid])

    def test_cycle(self):
        recipe = self.session.create_entity('Recipe', name=u'toto')
        step1 = recipe.add_step(u'action', u'apycot.init', initial=True, final=True)
        step2 = recipe.add_step(u'action', u'apycot.init')
        step3 = recipe.add_step(u'action', u'apycot.init', initial=True, final=True)
        recipe.add_transition(step1, step2)
        recipe.add_transition(step2, step3)
        recipe.add_transition(step3, step1)
        self.commit()
        self.assertEqual(recipe.check_validity()[recipe.eid][0].cycle, [step1.eid, step2.eid, step3.eid])

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
