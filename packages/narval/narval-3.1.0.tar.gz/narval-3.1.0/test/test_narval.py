# copyright 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of narval.
#
# narval is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# narval is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with narval.  If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-narval automatic tests"""

from logilab.common.testlib import unittest_main

from cubicweb.devtools.testlib import AutomaticWebTest


class AutomaticWebTest(AutomaticWebTest):
    no_auto_populate = set(('Plan',))
    ignored_relations = set(('execution_of',))

    def to_test_etypes(self):
        return set(('Recipe',))

    def list_startup_views(self):
        return ('narval.plan.summarytable',)


if __name__ == '__main__':
    unittest_main()
