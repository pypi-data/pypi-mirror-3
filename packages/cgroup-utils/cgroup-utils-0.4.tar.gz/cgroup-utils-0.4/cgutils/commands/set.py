# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# See the COPYING file for license information.
#
# Copyright (c) 2012 peo3 <peo314159265@gmail.com>

import os.path
import sys

from cgutils import cgroup
from cgutils import command
from cgutils import fileops


class Command(command.Command):
    NAME = 'set'

    parser = command.Command.parser
    parser.usage = "%%prog %s [options] <control_file> <value>" % NAME

    def run(self, args):
        if len(args) != 2:
            self.parser.error('Invalid arguments: ' + ' '.join(args))

        if self.options.debug:
            print args

        path = args[0]
        value = args[1]

        if not os.path.exists(path):
            print("%s not found" % path)
            sys.exit(1)

        fileops.write(path, value)
