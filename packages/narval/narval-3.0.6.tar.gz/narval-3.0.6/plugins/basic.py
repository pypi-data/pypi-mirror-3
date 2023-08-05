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
"""Basic narval actions, such as noop, file reading/writing, executing arbitrary
system command...
"""

__docformat__ = 'restructuredtext en'
_ = unicode

import os
import subprocess
import shutil
from glob import glob
from copy import copy

from narvalbot.prototype import action, input, output


@action('basic.noop')
def act_noop(inputs) :
    """No OPeration"""
    return {}


@input('input')
@output('output')
@action('basic.mirror')
def act_mirror(inputs) :
    """Copy inputs to outputs"""
    return {'output': copy(inputs['input'])}


@input('path_src', "isinstance(elmt, FilePath)")
@input('path_dest', "isinstance(elmt, FilePath)")
@action('basic.move')
def act_move(inputs) :
    """Move file or directory from path_src to path_dest"""
    src, dest = inputs['path_src'], inputs['path_dest']
    if not src.host and not dest.host:
        for src_path in glob(src.path):
            shutil.move(src_path, os.path.join(dest.path,
                                               os.path.basename(src_path)))
    else:
        act_copy(inputs)
        # XXX delete source
    return {}


@input('path_src', "isinstance(elmt, FilePath)")
@input('path_dest', "isinstance(elmt, FilePath)")
@action('basic.copy')
def act_copy(inputs) :
    """copy file or directory using scp protocol from path_src to path_dest"""
    src, dest = inputs['path_src'], inputs['path_dest']
    if not src.host and not dest.host:
        for src_path in glob(src.path):
            try:
                shutil.copy(src_path, dest.path)
            except IOError: # src_path is a folder
                shutil.copytree(src_path,
                                os.path.join(dest.path,
                                             os.path.basename(src_path)))
    else:
        # output to pipe to avoid spurious messages
        subprocess.call(args=(['scp', '-r'] + glob(src.path) + [_format_path(dest)]),
                        stdout=subprocess.PIPE)
    return {}

def _format_path(file_path):
    return ':'.join([__i for __i in [file_path.host,
                                     file_path.path] if __i])
