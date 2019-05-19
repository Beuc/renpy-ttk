#!/usr/bin/python

# Convert .rpy translation blocks and strings to .pot gettext template

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

# PATH=~/.../renpy-7.2.2-sdk:$PATH ./i18n_renpy2pot.py ~/.../mygame/
# msgmerge old.po game.pot > new.po
# Or Poedit old.po > Catalog > Update from POT File > game.pot

from __future__ import print_function
import sys, os, fnmatch
import re
import subprocess, shutil
import tlparser

def tl2pot(projectpath):
    # Refresh strings
    try:
        # Ensure Ren'Py keeps the strings order (rather than append new strings)
        shutil.rmtree(os.path.join(projectpath,'game','tl','pot'))
    except OSError:
        pass
    # TODO: renpy within renpy == sys.executable -EO sys.argv[0]
    # cf. launcher/game/project.rpy
    print("Calling Ren'Py translate")
    # using --compile otherwise Ren'Py sometimes skips half of the files
    ret = subprocess.call(['renpy.sh', projectpath, 'translate', 'pot', '--compile'])
    if ret != 0:
        raise Exception("Ren'Py error")
    
    strings = []
    for curdir, subdirs, filenames in os.walk(os.path.join(projectpath,'game','tl','pot')):
        for filename in fnmatch.filter(filenames, '*.rpy'):
            print("Parsing  " + os.path.join(curdir,filename))
            f = open(os.path.join(curdir,filename), 'r')
            lines = f.readlines()
            if lines[0].startswith('\xef\xbb\xbf'):
                lines[0] = lines[0][3:]  # BOM

            lines.reverse()
            while len(lines) > 0:
                strings.extend(tlparser.parse_next_block(lines))
    
    occurrences = {}
    for s in strings:
        occurrences[s['text']] = occurrences.get(s['text'], 0) + 1

    out = open('game.pot', 'w')
    out.write(r"""msgid ""
msgstr ""
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"

""")
    for s in strings:
        out.write('#: ' + s['source'] + '\n')
        if occurrences[s['text']] > 1:
            out.write('msgctxt "' + (s['id'] or s['source']) + '"\n')
        out.write('msgid "' + s['text'] + '"\n')
        out.write('msgstr ""\n')
        out.write('\n')
    print("Wrote 'game.pot'.")

if __name__ == '__main__':
    tl2pot(sys.argv[1])
