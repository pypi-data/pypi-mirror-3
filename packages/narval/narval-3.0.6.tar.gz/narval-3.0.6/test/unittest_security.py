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
from __future__ import with_statement
__docformat__ = "restructuredtext en"

from logilab.common.tasksqueue import LOW
from cubicweb import ValidationError
from cubicweb.devtools.testlib import CubicWebTC

class NarvalSecurityTC(CubicWebTC):

    def setUp(self):
        super(NarvalSecurityTC, self).setUp()
        req = self.request()
        self.narvaux = req.create_entity('CWGroup', name=u'narvaux')
        self.toto = self.create_user(u'toto', groups=('narvaux', 'users'))
        self.titi = self.create_user(u'titi', groups=('users',))

    def test_noop(self):
        req = self.request()
        recipe = req.create_entity('Recipe', name=u'functest.noop')
        step1 = recipe.add_step(u'action', u'basic.noop', initial=True)
        step2 = recipe.add_step(u'action', u'basic.noop', final=True)
        tr = recipe.add_transition(step1, step2)

        eperm = req.create_entity('CWPermission', name=u'execute', label=u'execute (narvaux)')
        req.execute('SET R require_permission P WHERE R eid %(r)s, P eid %(p)s',
                    {'r': recipe.eid, 'p': eperm.eid})
        req.execute('SET P require_group G WHERE G eid %(g)s, P eid %(p)s',
                    {'g': self.narvaux.eid, 'p': eperm.eid})

        self.commit()
        with self.login('titi'):
            req = self.request()
            self.assertRaises(ValidationError, req.create_entity, 'Plan',
                              priority=LOW, arguments=u'Options()',
                              execution_of=recipe)
            req.cnx.rollback()
        with self.login('toto'):
            req = self.request()
            plan = req.create_entity('Plan', priority=LOW, arguments=u'Options()',
                                     execution_of=recipe)
            self.commit()

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
