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

import sys, os

# Change these values to customize exactly how it is changed.
fromYear = 2010
toYear = 2011

startWith = "# Trosnoth"
replaceFrom = '''# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-%s Joshua D Bartlett''' % fromYear
replaceWith = '''# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-%s Joshua D Bartlett''' % toYear

try:
    WindowsError
except NameError:
    class WindowsError(Exception):
        pass

def fix(directory):
    filenames = os.listdir(directory)
    a = 0
    for fn in filenames:
        try:
            fix(os.path.join(directory, fn))
        except (WindowsError, OSError):
            if os.path.splitext(fn)[1] == '.py':
                f = open(os.path.join(directory, fn), 'rU')
                line = f.read()
                if line.startswith(startWith):
                    newline = line.replace(replaceFrom,
                                           replaceWith)
                    f.close()
                    f = open(os.path.join(directory, fn), 'w')
                    f.write(newline)
                f.close()

    return a

if __name__ == '__main__':
    if len(sys.argv) == 1:
        import trosnoth
        f = os.path.dirname(trosnoth.__file__)
        fix(f)
    elif len(sys.argv) == 2:
        fix(sys.argv[1])
    else:
        print '%s takes at most 1 argument' % sys.argv[0]

    raw_input("Done...")
