#!/usr/bin/python

# Convert .rpy translation blocks and strings to .pot gettext template

# Copyright (C) 2019, 2020  Sylvain Beucler

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

from __future__ import print_function
import sys, os, fnmatch, operator, io
import re
import shutil
import rttk.run, rttk.tlparser, rttk.utf_8_sig

def tl2pot(projectpath, outfile='game.pot'):
    # Refresh strings
    try:
        # Ensure Ren'Py keeps the strings order (rather than append new strings)
        shutil.rmtree(os.path.join(projectpath,'game','tl','pot'))
    except OSError:
        pass

    print("Calling Ren'Py translate to get the latest strings")
    # using --compile otherwise Ren'Py sometimes skips half of the files
    rttk.run.renpy([projectpath, 'translate', 'pot', '--compile'])

    strings = []
    for curdir, subdirs, filenames in sorted(os.walk(os.path.join(projectpath,'game','tl','pot')), key=operator.itemgetter(0)):
        for filename in sorted(fnmatch.filter(filenames, '*.rpy')):
            print("Parsing " + os.path.join(curdir,filename))
            f = io.open(os.path.join(curdir,filename), 'r', encoding='utf-8-sig')
            lines = f.readlines()
            lines.reverse()
            cur_strings = []
            while len(lines) > 0:
                parsed = rttk.tlparser.parse_next_block(lines)
                for s in parsed:
                    if s['text'] is None:
                        continue
                    if s['text'] == '':
                        # '' is special in gettext, don't attempt to translate it
                        continue
                    cur_strings.append(s)
            cur_strings.sort(key=lambda s: (s['source'].split(':')[0], int(s['source'].split(':')[1])))
            strings.extend(cur_strings)
    
    occurrences = {}
    for s in strings:
        occurrences[s['text']] = occurrences.get(s['text'], 0) + 1

    out = io.open(outfile, 'w', encoding='utf-8')
    out.write(ur"""msgid ""
msgstr ""
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"

""")
    for s in strings:
        out.write(u'#: ' + s['source'] + u'\n')
        if occurrences[s['text']] > 1:
            out.write(u'msgctxt "' + (s['id'] or s['source']) + u'"\n')
        out.write(u'msgid "' + s['text'] + u'"\n')
        out.write(u'msgstr ""\n')
        out.write(u'\n')
    print("Wrote '" + outfile + "'.")

    try:
        # Clean-up
        shutil.rmtree(os.path.join(projectpath,'game','tl','pot'))
    except OSError:
        pass

if __name__ == '__main__':
    tl2pot(sys.argv[1])
