#!/usr/bin/python3

# Convert .rpy translation blocks to .pot gettext template

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

import sys, os, glob
import re
import subprocess, shutil

projectpath = sys.argv[1]

# Refresh strings
try:
    # Ensure Ren'Py keeps the strings order (rather than append new strings)
    shutil.rmtree(os.path.join(projectpath,'game','tl','pot'))
except FileNotFoundError:
    pass
# TODO: renpy within renpy == sys.executable -EO sys.argv[0]
# cf. launcher/game/project.rpy
subprocess.call(['renpy.sh', projectpath, 'translate', 'pot'])
# possibly:
# subprocess.call(['renpy.sh', projectpath, 'translate', 'pot', '--compile'])

print("Generating game.pot...")
out = open('game.pot', 'w')
for filename in glob.glob(os.path.join(projectpath,'game','tl','pot','**','*.rpy'), recursive=True):
    # translations for renpy/common/ system files - update with the_question's instead
    if filename == os.path.join(projectpath,'game','tl','pot','common.rpy'):
        continue
    # TODO: screens.rpy probably contains custom strings in addition to common ones
    if filename == os.path.join(projectpath,'game','tl','pot','screens.rpy'):
        continue

    out.write('# ' + filename + '\n')
    f = open(filename)
    step1 = ''
    # Warning: very crude POC ;)
    for line in f.readlines():
        if line[0] == '\ufeff':  # BOM
            line = line[1:]
        if (re.match('^ *#', line)  # comments
            or re.match('^translate \w+ strings:', line)  # base strings block
            or re.match('^ *new ', line)  # translated base string
            or line == '\n'):  # empty string
            continue
        if re.match('^ *old ', line):
            # old "xxx" -> [no context]:xxx
            line = re.sub('^ *old "(.*)"', ':\\1', line)
        elif line.startswith('translate '):
            # keep context ID and merge with next line
            line = re.sub('^translate \w+ (\w+):\n', '\\1:', line)
        else:
            # only keep "-delimited string in dialog lines
            line = re.sub('^ *(?:[^"][^ ]* )*"(.*)"(?: [^"][^ ]*)*\n', '\\1\n', line)
        step1 += line
    
    lines = step1.split("\n")[:-1]
    
    for line in lines:
        (ctxt, line) = line.split(':', maxsplit=1)
        if ctxt:
            out.write('msgctxt "' + ctxt + '"\n')
        out.write('msgid "' + line + '"\n')
        out.write('msgstr ""\n')
        out.write('\n')
