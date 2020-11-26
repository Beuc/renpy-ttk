#!/usr/bin/python

# Convert .rpy translation blocks and strings to .po gettext catalog

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

# Use cases:
# - import your game's translation started in Ren'Py format
# - import default Ren'Py translated strings from "The Question"

from __future__ import print_function
import sys, os, fnmatch, operator, io
import re
import shutil
import rttk.run, rttk.tlparser, rttk.utf_8_sig


def tl2po(projectpath, language, outfile=None):
    if not re.match('^[a-z_]+$', language, re.IGNORECASE):
        raise Exception("Invalid language name", language)
    if not os.path.isdir(os.path.join(projectpath,'game','tl',language)):
        raise Exception("Language not found", os.path.join(projectpath,'game','tl',language))

    if outfile is None:
        outfile = language+'.po'

    # Refresh strings
    print("Calling Ren'Py translate to get latest strings")
    try:
        # Ensure Ren'Py keeps the strings order (rather than append new strings)
        shutil.rmtree(os.path.join(projectpath,'game','tl','pot'))
    except OSError:
        pass
    # using --compile otherwise Ren'Py sometimes skips half of the files
    rttk.run.renpy([projectpath, 'translate', 'pot', '--compile'])
    
    originals = []
    for curdir, subdirs, filenames in sorted(os.walk(os.path.join(projectpath,'game','tl','pot')), key=operator.itemgetter(0)):
        for filename in sorted(fnmatch.filter(filenames, '*.rpy')):
            print("Parsing " + os.path.join(curdir,filename))
            f = io.open(os.path.join(curdir,filename), 'r', encoding='utf-8-sig')
            lines = f.readlines()
            lines.reverse()
            while len(lines) > 0:
                parsed = rttk.tlparser.parse_next_block(lines)
                for s in parsed:
                    if s['text'] is None:
                        continue
                    if s['text'] == '':
                        # '' is special in gettext, don't attempt to translate it
                        continue
                    originals.append(s)

    translated = []
    for curdir, subdirs, filenames in os.walk(os.path.join(projectpath,'game','tl',language)):
        for filename in fnmatch.filter(filenames, '*.rpy'):
            print("Parsing  " + os.path.join(curdir,filename))
            f = io.open(os.path.join(curdir,filename), 'r', encoding='utf-8-sig')
            lines = f.readlines()
            lines.reverse()
            while len(lines) > 0:
                translated.extend(rttk.tlparser.parse_next_block(lines))

    t_blocks_index = {}
    t_basestr_index = {}
    for s in translated:
        if s['id']:
            t_blocks_index[s['id']] = s['text']
        else:
            t_basestr_index[s['text']] = s['translation']
    
    occurrences = {}
    for s in originals:
        occurrences[s['text']] = occurrences.get(s['text'], 0) + 1

    out = io.open(outfile, 'w', encoding='utf-8')
    out.write(ur"""msgid ""
msgstr ""
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"

""")
    for s in originals:
        out.write(u'#: ' + s['source'] + u'\n')
        if occurrences[s['text']] > 1:
            out.write(u'msgctxt "' + (s['id'] or s['source']) + u'"\n')
        out.write('msgid "' + s['text'] + '"\n')
        if s['id'] is not None and t_blocks_index.has_key(s['id']):
            out.write(u'msgstr "' + (t_blocks_index[s['id']] or '') + u'"\n')
        else:
            out.write(u'msgstr "' + t_basestr_index.get(s['text'],'') + u'"\n')
        out.write(u'\n')
    print("Wrote '" + outfile + "'.")

    try:
        # Clean-up
        shutil.rmtree(os.path.join(projectpath,'game','tl','pot'))
    except OSError:
        pass

if __name__ == '__main__':
    tl2po(sys.argv[1], sys.argv[2])
