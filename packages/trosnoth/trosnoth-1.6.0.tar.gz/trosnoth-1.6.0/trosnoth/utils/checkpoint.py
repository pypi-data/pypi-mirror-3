# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2011 Joshua D Bartlett
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

import os
import re
import sys

from trosnoth import data

checkpointReached = set()
def checkpoint(name):
    checkpointReached.add(name)

def saveCheckpoints():
    path = data.getPath(data.user, 'checkpoints-reached')
    f = open(path, 'a')
    for c in checkpointReached:
        f.write('%s\n' % c)
    f.close()

checkpointRE = re.compile(
        '\s*(?:(?:utils\.)?checkpoint\.)?checkpoint\((?P<name>.*)\)')

def clearCheckpoints():
    path = data.getPath(data.user, 'checkpoints-reached')
    os.remove(path)

def message(msg=''):
    print msg

def displayCheckpoints():
    toppath = '.'
    if len(sys.argv) > 2:
        toppath = sys.argv[2]
    checkpoints = {}
    message('Gathering checkpoints in path %r' % toppath)
    for path, dirs, filenames in os.walk(toppath):
        if '.hg' in path:
            continue
        for f in filenames:
            fullpath = os.path.join(toppath, path, f)
            if not f.endswith('.py'):
                continue
            linenum = 0
            for line in open(fullpath, 'r'):
                linenum += 1
                m = checkpointRE.match(line)
                if m is None:
                    continue
                name = m.group('name')
                try:
                    name = eval(name)
                except Exception:
                    message('Could not get name for checkpoint (%s line %d)' %
                            (fullpath, linenum))
                    message(line)
                    continue
                if name in checkpoints:
                    message('Warning: checkpoint %r exists (%s line %d)' %
                            (name, fullpath, linenum))
                    continue
                checkpoints[name] = (fullpath, linenum)
    message()

    reachedpath = data.getPath(data.user, 'checkpoints-reached')
    if os.path.exists(reachedpath):
        reached = set(open(reachedpath, 'r').read().splitlines())
    else:
        reached = set()
    if len(reached) > 0 or len(checkpoints) > 0:
        maxLength = max([len(i) for i in reached] +
                [len(i) for i in checkpoints.keys()])
        pattern = '  %%%ds \t%%s' % maxLength

    if len(reached) == 0:
        message('No reached checkpoint data found.')
    else:
        message('Checkpoints reached:')
        reached = list(reached)
        reached.sort()
        for name in reached:
            if name in checkpoints:
                filename, linenum = checkpoints[name]
                message(pattern % (name, '%s line %d' % checkpoints[name]))
                del checkpoints[name]
            else:
                message(pattern % (name, 'UNKNOWN LOCATION'))

    message()
    if len(checkpoints) == 0:
        message('No unreached checkpoints found.')
    else:
        message('Checkpoints never reached:')
        unreached = checkpoints.keys()
        unreached.sort()
        for name in unreached:
            message(pattern % (name, '%s line %d' % checkpoints[name]))

if __name__ == '__main__':
    if len(sys.argv) == 1 or sys.argv[1] not in ('clear', 'list'):
        name = sys.argv[0]
        message('Usage:')
        message('  %s clear - clears checkpoint data' % name)
        message('  %s list [path] - lists checkpoints reached and not reached,'
                % name)
        message('         starting looking for checkpoints in given path.')
    elif sys.argv[1] == 'clear':
        clearCheckpoints()
    else:
        displayCheckpoints()
