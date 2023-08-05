# Copyright (c) 2010 LOGILAB S.A. (Paris, FRANCE).
#
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

from logilab.mtconverter import xml_escape

class Msg(object):
    """ a small message wrapper class
    with a render method """
    def __init__(self, msg):
        self.msg = msg

    def render(self, cw):
        return xml_escape(self.msg)

class Cyclemsg(object):
    """ wraps a cycle + render method """
    def __init__(self, cycle):
        self.cycle = cycle

    def render(self, cw):
        out = []
        for eid in self.cycle:
            step = cw.entity_from_eid(eid)
            out.append(step.view('outofcontext'))
        cycle =  ' &#8658; '.join(out)
        return cw._('these steps form a cycle:') + u'<div>%s</div>' % cycle
