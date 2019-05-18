#!/usr/bin/python3

# Convert gettext .mo catalog to .rpy translate blocks

# Copyright (C) 2019  Sylvain Beucler

# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import re
import gettext
import sys, os, shutil, glob, tempfile, subprocess

# Doc: manual .mo test:
# mkdir -p $LANG/LC_MESSAGES/
# msgfmt xxx.po -o $LANG/LC_MESSAGES/game.mo
# TEXTDOMAINDIR=. gettext -s -d game "Start"
# TEXTDOMAINDIR=. gettext -s -d game "script_abcd1234"$'\x4'"You've created a new Ren'Py game."

projectpath = sys.argv[1]
mofile = sys.argv[2]
renpy_target_language = sys.argv[3]

# Reset target language to original strings so we can match them
# TODO: update existing translations instead of removing them,
# retrieving original dialogue translations through tl/None/*.rpy and
# their IDs.
try:
    shutil.rmtree(os.path.join(projectpath,'game','tl',renpy_target_language))
except FileNotFoundError:
    pass
subprocess.call(['renpy.sh', projectpath, 'translate', renpy_target_language])

with tempfile.TemporaryDirectory() as localedir:
    # Setup gettext directory structure
    msgdir = os.path.join(localedir, os.environ['LANG'], 'LC_MESSAGES')
    os.makedirs(msgdir)
    #shutil.copy2(sys.argv[1], os.path.join(localedir, 'game.mo')
    if mofile.endswith('.po'):
        pofile = mofile
        ret = subprocess.call(['msgfmt', pofile, '-v', '-o', os.path.join(msgdir, 'game.mo')])
        if ret != 0:
            raise Exception("msgfmt failed")
    else:
        shutil.copy2(mofile, os.path.join(msgdir, 'game.mo'))
    gettext.bindtextdomain('game', localedir)
    gettext.dgettext('game', 'text')

    for filename in glob.glob(os.path.join(projectpath,'game','tl',renpy_target_language,'**','*.rpy'), recursive=True):    
        # translations for renpy/common/ system files - not for us
        if filename == os.path.join('tl',renpy_target_language,'common.rpy'):
            # TODO: update with renpy/the_question/game/tl/xxx/common.rpy
            # (more translations than in launcher/game)
            # Note: only contains base strings
            # shutil.copy2(...)
            continue
        # TODO: screens.rpy probably contains custom strings in addition to common ones
        if filename == os.path.join(projectpath,'game','tl',renpy_target_language,'screens.rpy'):
            # TODO: update with renpy/the_question/game/tl/xxx/screens.rpy
            # (more translations than in launcher/game)
            # Note: only contains base strings
            # shutil.copy2(...)
            continue
    
        f_in = open(filename, 'r')
        lines = f_in.readlines()[::-1]  # reverse so we can pop/append efficiently
        f_in.close()
    
        out = open(filename, 'w')
        while len(lines) > 0:
            line = lines.pop()
            # empty line (possibly with comment)
            if re.match(r'^\s*(#.*)?\n$', line):
                out.write(line)
            # translate block
            elif line.startswith('translate'):
                msgid = line.strip(':\n').split()[2]
                if msgid == 'strings':
                    # basic strings block
                    out.write(line)
                    # TODO
                    pass
                else:
                    # dialog block
                    out.write(line)
                    while len(lines) > 0:
                        line = lines.pop()
                        if line.startswith('translate'):
                            lines.append(line)
                            break
                        elif re.match(r'^\s*(#.*)?\n$', line):
                            out.write(line)
                        else:
                            # dialog line
                            m = re.search(r' "((?:[^\\"]|\\.)*)"', line)
                            msgstr = msgid+'\x04'+m.groups()[0]
                            translation = gettext.dgettext('game', msgstr)
                            if translation != msgstr:
                                line = re.sub(' "(?:[^\\"]|\\.)*"', ' "'+translation+'"', line)
                            out.write(line)
            # Unknown
            else:
                out.write(line)
